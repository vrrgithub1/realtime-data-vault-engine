# Real-Time Financial Data Vault & AI Query Engine

An enterprise-grade, end-to-end real-time data engineering pipeline built with **Kafka (Redpanda)**, **Python (Polars)**, **Snowflake**, **dbt**, **GitHub Actions CI/CD**, and **LangChain**.

## Architecture Overview

```mermaid
flowchart TD
    %% Custom Styling
    classDef producer fill:#1e293b,stroke:#38bdf8,stroke-width:2px,color:#fff
    classDef broker fill:#1e293b,stroke:#f59e0b,stroke-width:2px,color:#fff
    classDef ingestion fill:#1e293b,stroke:#a855f7,stroke-width:2px,color:#fff
    classDef raw fill:#0f172a,stroke:#38bdf8,stroke-width:2px,color:#fff
    classDef dv fill:#0f172a,stroke:#eab308,stroke-width:2px,color:#fff
    classDef mart fill:#0f172a,stroke:#22c55e,stroke-width:2px,color:#fff
    classDef ai fill:#1e293b,stroke:#ec4899,stroke-width:2px,color:#fff
    classDef cicd fill:#1e293b,stroke:#64748b,stroke-dasharray: 5 5,color:#fff

    %% Event Streaming & Ingestion
    subgraph StreamLayer ["1. Streaming & Ingestion"]
        P["Trade Event Producer<br/>(Python)"]:::producer -->|Stream Events| B["Redpanda / Kafka<br/>(Message Broker)"]:::broker
        B -->|Consume| C["Polars Micro-Batch<br/>Consumer"]:::ingestion
    end

    %% Snowflake Platform
    subgraph Snowflake ["2. Snowflake Data Platform (REALTIME_DV_DB)"]
        C -->|Load JSON| RAW["RAW.RAW_FINANCIAL_TRADES"]:::raw
        
        subgraph Vault ["Data Vault 2.0 (VAULT)"]
            RAW -->|dbt stage & hash| STG["stg_financial_trades"]:::raw
            STG --> HUBS["Hubs<br/>(HUB_TRADE / HUB_ACCOUNT)"]:::dv
            STG --> LINKS["Links<br/>(LINK_TRADE_ACCOUNT)"]:::dv
            STG --> SATS["Satellites<br/>(SAT_TRADE_DETAILS)"]:::dv
        end
        
        subgraph Marts ["Star Schema Marts (MARTS)"]
            HUBS -->|account_id| DIM["dim_account"]:::mart
            HUBS -->|trade_id| FACT["fact_trades"]:::mart
            LINKS -->|hk_trade_account| FACT
            SATS -->|trade metrics| FACT
        end
    end

    %% Downstream & CI/CD
    subgraph AI ["3. Consumption Layer"]
        DIM --> AGENT["LangChain AI Agent<br/>(Text-to-SQL Analytics)"]:::ai
        FACT --> AGENT
    end

    CICD["GitHub Actions CI/CD<br/>(dbt run & dbt test)"]:::cicd -.-|Automates Transformations| Vault
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

