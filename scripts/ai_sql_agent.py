import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain_openai import ChatOpenAI

# 1. Load environment variables
load_dotenv()

account = os.getenv("SNOWFLAKE_ACCOUNT")
user = os.getenv("SNOWFLAKE_USER")
password = os.getenv("SNOWFLAKE_PASSWORD")
warehouse = os.getenv("SNOWFLAKE_WAREHOUSE", "REALTIME_DV_WH")
database = os.getenv("SNOWFLAKE_DATABASE", "REALTIME_DV_DB")
schema = os.getenv("SNOWFLAKE_SCHEMA", "STAGING_MARTS")

# 2. Build SQLAlchemy connection string for Snowflake
connection_string = f"snowflake://{user}:{password}@{account}/{database}/{schema}?warehouse={warehouse}&role=ACCOUNTADMIN"

# 3. Connect dbt Star Schema to LangChain (Note: SQLAlchemy reflects Snowflake table names in lowercase)
engine = create_engine(connection_string)
db = SQLDatabase(engine, include_tables=["fact_trades", "dim_account"])

# 4. Initialize LLM Model
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# 5. Create SQL Agent with Data Vault / Mart context
agent_executor = create_sql_agent(
    llm=llm,
    db=db,
    verbose=True,
    agent_type="openai-tools"
)

def ask_data_agent(prompt: str):
    print(f"\n💬 Question: {prompt}")
    print("=" * 60)
    response = agent_executor.invoke({"input": prompt})
    print("\n🤖 AI Response:")
    print(response["output"])
    print("=" * 60)

if __name__ == "__main__":
    # Test Queries
    ask_data_agent("What are the top 3 stock symbols by total gross trade volume?")
    ask_data_agent("How many buy vs sell orders were executed for AAPL, and what was the average price?")