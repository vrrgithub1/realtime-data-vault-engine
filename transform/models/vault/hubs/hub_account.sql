{{ config(materialized='incremental', unique_key='hk_account_id') }}

SELECT DISTINCT
    hk_account_id,
    account_id,
    load_timestamp,
    record_source
FROM {{ ref('stg_financial_trades') }}

{% if is_incremental() %}
  WHERE load_timestamp > (SELECT MAX(load_timestamp) FROM {{ this }})
{% endif %}