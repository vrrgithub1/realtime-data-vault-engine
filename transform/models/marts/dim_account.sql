SELECT
    hk_account_id       AS account_hk,
    account_id          AS account_id,
    load_timestamp      AS created_at,
    record_source       AS record_source
FROM {{ ref('hub_account') }}