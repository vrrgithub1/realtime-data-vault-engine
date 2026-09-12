# Real-Time Financial Data Vault & AI Query Engine

An enterprise-grade, end-to-end real-time data engineering pipeline built with **Kafka (Redpanda)**, **Python (Polars)**, **Snowflake**, **dbt**, **GitHub Actions CI/CD**, and **LangChain**.

## Architecture Overview

```mermaid
graph TB
    subgraph layer1["📊 Event Streaming"]
        Producer["Trade Event Producer<br/>(Python)"]
    end
    
    subgraph layer2["🔄 Message Broker"]
        Kafka["Redpanda / Kafka<br/>(Message Broker)"]
    end
    
    subgraph layer3["⚙️ Data Ingestion"]
        Consumer["Polars Micro-Batch<br/>Consumer"]
    end
    
    subgraph snowflake["❄️ Snowflake Data Platform"]
        subgraph raw["Raw Data"]
            Snowflake_Raw["Snowflake RAW<br/>(Raw Layer)"]
        end
        
        subgraph vault["🔧 Data Vault 2.0"]
            Hubs["🏠 Hubs<br/>HUB_TRADE<br/>HUB_ACCOUNT"]
            Links["🔗 Links<br/>LINK_TRADE_ACCOUNT"]
            Sats["🛰️ Satellites<br/>SAT_TRADE_DETAILS"]
        end
        
        subgraph marts["⭐ Star Schema Marts"]
            Dim["📈 dim_account"]
            Fact["📊 fact_trades"]
        end
    end
    
    subgraph layer7["🤖 AI Query Engine"]
        AI["LangChain AI Agent<br/>(Natural Language Queries)"]
    end
    
    CI["🚀 GitHub Actions CI/CD"]
    
    Producer -->|Stream Events| Kafka
    Kafka -->|Consume| Consumer
    Consumer -->|Load| Snowflake_Raw
    Snowflake_Raw --> Hubs
    Snowflake_Raw --> Links
    Snowflake_Raw --> Sats
    Hubs --> Dim
    Links --> Dim
    Sats --> Dim
    Hubs --> Fact
    Links --> Fact
    Sats --> Fact
    snowflake --> AI
    
    CI -.->|Automate| snowflake
    
    style layer1 fill:#e1f5ff
    style layer2 fill:#fff3e0
    style layer3 fill:#f3e5f5
    style raw fill:#e0f2f1
    style vault fill:#fff9c4
    style marts fill:#f1f8e9
    style layer7 fill:#fce4ec
    style snowflake fill:#f0f4c3
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

