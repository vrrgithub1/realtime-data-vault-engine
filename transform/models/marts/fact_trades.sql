WITH link_ta AS (
    SELECT 
        hk_trade_account,
        hk_trade_id,
        hk_account_id
    FROM {{ ref('link_trade_account') }}
),

sat_trade AS (
    SELECT 
        hk_trade_id,
        symbol,
        order_type,
        quantity,
        price,
        (quantity * price) AS total_trade_amount,
        trade_timestamp,
        load_timestamp
    FROM {{ ref('sat_trade_details') }}
)

SELECT
    t.hk_trade_id                   AS trade_hk,
    l.hk_account_id                 AS account_hk,
    t.trade_id                      AS trade_id,
    s.symbol                        AS symbol,
    s.order_type                    AS order_type,
    s.quantity                      AS quantity,
    s.price                         AS unit_price,
    s.total_trade_amount            AS total_trade_amount,
    s.trade_timestamp               AS trade_timestamp,
    s.load_timestamp                AS load_timestamp
FROM {{ ref('hub_trade') }} t
INNER JOIN link_ta l 
    ON t.hk_trade_id = l.hk_trade_id
INNER JOIN sat_trade s 
    ON t.hk_trade_id = s.hk_trade_id