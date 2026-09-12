

SELECT DISTINCT
    hk_trade_account,
    hk_trade_id,
    hk_account_id,
    load_timestamp,
    record_source
FROM REALTIME_DV_DB.STAGING_STAGING.stg_financial_trades

