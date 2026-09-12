WITH raw_trades AS (
    SELECT 
        PAYLOAD:trade_id::STRING          AS trade_id,
        PAYLOAD:account_id::STRING        AS account_id,
        PAYLOAD:symbol::STRING            AS symbol,
        PAYLOAD:order_type::STRING        AS order_type,
        PAYLOAD:quantity::INT             AS quantity,
        PAYLOAD:price::NUMBER(10,2)       AS price,
        PAYLOAD:trade_timestamp::TIMESTAMP_TZ AS trade_timestamp,
        RECORD_SOURCE,
        INGESTED_AT                       AS load_timestamp
    FROM {{ source('raw_sources', 'RAW_FINANCIAL_TRADES') }}
)

SELECT
    trade_id,
    account_id,
    
    -- Data Vault 2.0 MD5 Hash Keys
    MD5(UPPER(TRIM(trade_id)))                                         AS hk_trade_id,
    MD5(UPPER(TRIM(account_id)))                                       AS hk_account_id,
    MD5(CONCAT_WS(';', UPPER(TRIM(trade_id)), UPPER(TRIM(account_id)))) AS hk_trade_account,
    
    symbol,
    order_type,
    quantity,
    price,
    trade_timestamp,
    
    RECORD_SOURCE AS record_source,
    load_timestamp
FROM raw_trades