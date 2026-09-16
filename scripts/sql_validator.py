import sqlglot
import sqlglot.expressions as exp

ALLOWED_TABLES = {"fact_trades", "dim_account"}

def validate_and_sanitize_sql(sql_query: str) -> tuple[bool, str, str]:
    """
    Validates LLM-generated SQL queries using AST parsing.
    Returns: (is_valid: bool, processed_sql_or_error: str, rule_triggered: str)
    """
    try:
        # 1. Parse query AST using Snowflake dialect
        parsed = sqlglot.parse_one(sql_query, read="snowflake")

        # 2. Strict Command Type Check (Only SELECT/UNION allowed)
        if not isinstance(parsed, (exp.Select, exp.Union)):
            return False, f"Forbidden command type: {type(parsed).__name__}", "DML/DDL Prevention"

        # 3. Deep AST Inspection for embedded modifications
        for node in parsed.walk():
            # Fixed: Use exp.TruncateTable instead of exp.Truncate
            if isinstance(node, (exp.Insert, exp.Update, exp.Delete, exp.Drop, exp.Create, exp.Alter, exp.TruncateTable)):
                return False, f"Forbidden operation detected: {type(node).__name__}", "Mutating Query Guard"

        # 4. Table Access Whitelisting (Restricted strictly to MARTS layer)
        tables_in_query = {table.name.lower() for table in parsed.find_all(exp.Table)}
        unauthorized_tables = tables_in_query - ALLOWED_TABLES
        if unauthorized_tables:
            return False, f"Unauthorized table access: {unauthorized_tables}", "Schema Access Control"

        # 5. Inject Safety LIMIT if missing
        if not parsed.find(exp.Limit):
            parsed = parsed.limit(100)

        cleaned_sql = parsed.sql(dialect="snowflake")
        return True, cleaned_sql, "Passed AST & Whitelist Checks"

    except sqlglot.errors.ParseError as e:
        return False, f"SQL Syntax Error: {str(e)}", "AST Parser Error"
    except Exception as e:
        return False, f"Validation Error: {str(e)}", "Internal Audit Error"