{{ config(materialized='incremental', unique_key='hk_trade_id') }}

SELECT DISTINCT
    hk_trade_id,
    trade_id,
    load_timestamp,
    record_source
FROM {{ ref('stg_financial_trades') }}

{% if is_incremental() %}
  WHERE load_timestamp > (SELECT MAX(load_timestamp) FROM {{ this }})
{% endif %}