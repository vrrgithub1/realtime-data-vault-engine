{{ config(materialized='incremental', unique_key=['hk_trade_id', 'load_timestamp']) }}

SELECT
    hk_trade_id,
    load_timestamp,
    symbol,
    order_type,
    quantity,
    price,
    trade_timestamp,
    record_source
FROM {{ ref('stg_financial_trades') }}

{% if is_incremental() %}
  WHERE load_timestamp > (SELECT MAX(load_timestamp) FROM {{ this }})
{% endif %}