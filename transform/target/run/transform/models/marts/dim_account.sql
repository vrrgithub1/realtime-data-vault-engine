
  
    

create or replace transient table REALTIME_DV_DB.STAGING_MARTS.dim_account
    
    
    
    
    

    as (SELECT
    hk_account_id       AS account_hk,
    account_id          AS account_id,
    load_timestamp      AS created_at,
    record_source       AS record_source
FROM REALTIME_DV_DB.STAGING_VAULT.hub_account
    )
;


  