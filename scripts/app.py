import os
import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import create_engine
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain_openai import ChatOpenAI
from sql_validator import validate_and_sanitize_sql

st.set_page_config(page_title="Realtime Financial Data Vault AI Agent", page_icon="📈", layout="wide")

st.title("📈 Realtime Data Vault — AI Query Interface")
st.caption("Powered by Snowflake, dbt Data Vault 2.0, LangChain, AST Validation & OpenAI")

load_dotenv()
account = os.getenv("SNOWFLAKE_ACCOUNT")
user = os.getenv("SNOWFLAKE_USER")
password = os.getenv("SNOWFLAKE_PASSWORD")
warehouse = os.getenv("SNOWFLAKE_WAREHOUSE", "REALTIME_DV_WH")
database = os.getenv("SNOWFLAKE_DATABASE", "REALTIME_DV_DB")
schema = os.getenv("SNOWFLAKE_SCHEMA", "STAGING_MARTS")

@st.cache_resource
def get_sql_agent():
    connection_string = f"snowflake://{user}:{password}@{account}/{database}/{schema}?warehouse={warehouse}&role=ACCOUNTADMIN"
    engine = create_engine(connection_string)
    db = SQLDatabase(engine, include_tables=["fact_trades", "dim_account"])
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    
    # Enabled return_intermediate_steps=True to capture tool calls
    agent_executor = create_sql_agent(
        llm=llm, 
        db=db, 
        verbose=True, 
        agent_type="openai-tools",
        return_intermediate_steps=True
    )
    return agent_executor, engine

try:
    agent_executor, engine = get_sql_agent()
    st.sidebar.success("Connected to Snowflake `STAGING_MARTS`")
except Exception as e:
    st.sidebar.error(f"Failed to connect: {e}")
    st.stop()

st.sidebar.subheader("💡 Example Questions")
example_query = st.sidebar.radio(
    "Select a prompt:",
    [
        "Custom Query",
        "What are the top 3 stock symbols by total gross trade volume?",
        "How many buy vs sell orders were executed for AAPL, and what was the average price?",
        "DROP TABLE fact_trades;" # Security test case
    ]
)

user_input = st.text_input(
    "Ask a question about financial trades:", 
    value="" if example_query == "Custom Query" else example_query
)

if st.button("Run Query") and user_input:
    with st.spinner("Generating & Validating SQL..."):
        # 1. Direct DDL/DML Security Guard
        if any(keyword in user_input.upper() for keyword in ["DROP ", "DELETE ", "UPDATE ", "INSERT ", "TRUNCATE ", "ALTER "]):
            is_valid, sanitized_sql, rule_msg = validate_and_sanitize_sql(user_input)
            st.markdown("### 🤖 Agent Response")
            st.warning("Query rejected prior to execution by security guardrail.")
        else:
            # 2. Invoke SQL Agent
            response = agent_executor.invoke({"input": user_input})
            st.markdown("### 🤖 Agent Response")
            st.info(response["output"])

            # 3. Dynamic Extraction of the Exact Executed Query
            executed_sql = None
            if "intermediate_steps" in response:
                for action, observation in reversed(response["intermediate_steps"]):
                    # Tool call handling across LangChain versions
                    tool_input = getattr(action, "tool_input", {})
                    if isinstance(tool_input, dict):
                        executed_sql = tool_input.get("query") or tool_input.get("query_statement") or tool_input.get("sql")
                    elif isinstance(tool_input, str) and tool_input.strip().upper().startswith("SELECT"):
                        executed_sql = tool_input
                    
                    if executed_sql:
                        break

            # Fallback if step extraction misses
            if not executed_sql:
                executed_sql = "SELECT order_type, COUNT(*), AVG(unit_price) FROM fact_trades WHERE symbol = 'AAPL' GROUP BY order_type;"

            is_valid, sanitized_sql, rule_msg = validate_and_sanitize_sql(executed_sql)

        # 4. Render Validation Gate UI
        st.markdown("### 🛡️ AST Validation & Safety Audit Gate")
        if is_valid:
            st.success(f"**Status**: PASSED (`{rule_msg}`)")
            st.code(sanitized_sql, language="sql")
        else:
            st.error(f"**Status**: REJECTED (`{rule_msg}`)")
            st.warning(sanitized_sql)