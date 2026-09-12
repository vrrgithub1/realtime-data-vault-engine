# Real-Time Financial Data Vault & AI Query Engine

An enterprise-grade, end-to-end real-time data engineering pipeline built with **Kafka (Redpanda)**, **Python (Polars)**, **Snowflake**, **dbt**, **GitHub Actions CI/CD**, and **LangChain**.

## Architecture Overview

```mermaid
graph LR
    Producer["📊 Trade Event Producer<br/>(Python)"]
    Kafka["🔄 Redpanda / Kafka<br/>(Message Broker)"]
    Consumer["⚙️ Polars Micro-Batch<br/>Consumer"]
    Snowflake_Raw["❄️ Snowflake RAW<br/>(Raw Data)"]
    
    dbt["🔧 dbt Data Vault 2.0<br/>(Transformations)"]
    Hubs["🏠 Hubs<br/>HUB_TRADE, HUB_ACCOUNT"]
    Links["🔗 Links<br/>LINK_TRADE_ACCOUNT"]
    Sats["🛰️ Satellites<br/>SAT_TRADE_DETAILS"]
    
    Marts["⭐ Star Schema Marts<br/>(Dimensional Models)"]
    Dim_Account["📈 dim_account"]
    Fact_Trades["📊 fact_trades"]
    
    AI["🤖 LangChain AI Agent<br/>(Natural Language Queries)"]
    
    CI["🚀 GitHub Actions CI/CD<br/>(Automation)"]
    
    Producer -->|Stream Events| Kafka
    Kafka -->|Consume| Consumer
    Consumer -->|Load| Snowflake_Raw
    
    Snowflake_Raw -->|Raw Data| dbt
    dbt --> Hubs
    dbt --> Links
    dbt --> Sats
    
    Hubs --> Marts
    Links --> Marts
    Sats --> Marts
    
    Marts --> Dim_Account
    Marts --> Fact_Trades
    
    Dim_Account --> AI
    Fact_Trades --> AI
    
    CI -.->|Triggers Builds & Tests| dbt
    CI -.->|Monitors| Producer
    
    style Producer fill:#e1f5ff
    style Kafka fill:#fff3e0
    style Consumer fill:#f3e5f5
    style Snowflake_Raw fill:#e0f2f1
    style dbt fill:#fff9c4
    style Marts fill:#f1f8e9
    style AI fill:#fce4ec
    style CI fill:#ede7f6
```
## Key Components

1. **Event Streaming**: Python producer emitting streaming stock trade events to a Redpanda (Kafka) topic.
2. **High-Throughput Ingestion**: Python + Polars micro-batch consumer writing JSON payloads to Snowflake (`RAW.RAW_FINANCIAL_TRADES`).
3. **Data Vault 2.0 Modeling**: `dbt-snowflake` incremental models building deterministic MD5 Hash Keys across:
   - **Hubs**: `HUB_TRADE`, `HUB_ACCOUNT`
   - **Links**: `LINK_TRADE_ACCOUNT`
   - **Satellites**: `SAT_TRADE_DETAILS`
4. **Dimensional Information Marts**: Star Schema modeling producing `dim_account` and `fact_trades` for high-performance analytical queries.
5. **Continuous Integration (CI/CD)**: Automated GitHub Actions workflow testing connection health (`dbt debug`), executing transformations (`dbt run`), and running quality assertions (`dbt test`).
6. **AI Integration**: LangChain Text-to-SQL agent enabling natural language queries directly over the Snowflake Star Schema.

## How to Run

### 1. Ingestion Pipeline
```bash
# Start Redpanda Broker
docker compose -f docker/docker-compose.yml up -d

# Start Ingestion Consumer
python consumers/snowflake_stream_consumer.py
```

### 2. dbt Transformations

```Bash
cd transform
dbt run
dbt test
```

### 3. AI Agent Interface

```Bash
python scripts/ai_sql_agent.py
```

