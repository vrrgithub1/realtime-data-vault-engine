
  
    

create or replace transient table REALTIME_DV_DB.STAGING_VAULT.sat_trade_details
    
    
    
    
    

    as (

SELECT
    hk_trade_id,
    load_timestamp,
    symbol,
    order_type,
    quantity,
    price,
    trade_timestamp,
    record_source
FROM REALTIME_DV_DB.STAGING_STAGING.stg_financial_trades


    )
;


  