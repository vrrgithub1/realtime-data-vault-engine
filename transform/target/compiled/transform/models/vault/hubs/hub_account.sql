

SELECT DISTINCT
    hk_account_id,
    account_id,
    load_timestamp,
    record_source
FROM REALTIME_DV_DB.STAGING_STAGING.stg_financial_trades

