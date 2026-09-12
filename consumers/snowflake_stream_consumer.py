import json
import os
import polars as pl
from kafka import KafkaConsumer
import snowflake.connector

from dotenv import load_dotenv

load_dotenv()  # Automatically loads variables from .env file

# Configuration
KAFKA_BROKER = '127.0.0.1:19092'
TOPIC = 'financial_trades'
BATCH_SIZE = 10  # Number of events per micro-batch flush

# Snowflake Credentials (Passed via environment variables)
SNOWFLAKE_ACCOUNT = os.getenv("SNOWFLAKE_ACCOUNT")
SNOWFLAKE_USER = os.getenv("SNOWFLAKE_USER")
SNOWFLAKE_PASSWORD = os.getenv("SNOWFLAKE_PASSWORD")
SNOWFLAKE_WAREHOUSE = "REALTIME_DV_WH"
SNOWFLAKE_DATABASE = "REALTIME_DV_DB"
SNOWFLAKE_SCHEMA = "RAW"

def get_snowflake_connection():
    return snowflake.connector.connect(
        user=SNOWFLAKE_USER,
        password=SNOWFLAKE_PASSWORD,
        account=SNOWFLAKE_ACCOUNT,
        warehouse=SNOWFLAKE_WAREHOUSE,
        database=SNOWFLAKE_DATABASE,
        schema=SNOWFLAKE_SCHEMA
    )

def insert_microbatch_to_snowflake(events):
    if not events:
        return
    
    conn = get_snowflake_connection()
    cursor = conn.cursor()
    
    try:
        # Convert list of dicts to a single JSON string array
        batch_json = json.dumps(events)
        
        # Parse entire array at once and insert rows using FLATTEN
        insert_sql = """
            INSERT INTO REALTIME_DV_DB.RAW.RAW_FINANCIAL_TRADES (PAYLOAD, RECORD_SOURCE)
            SELECT 
                value AS PAYLOAD,
                COALESCE(value:record_source::STRING, 'RED_PANDA_STREAM') AS RECORD_SOURCE
            FROM TABLE(FLATTEN(input => PARSE_JSON(%s)));
        """
        
        cursor.execute(insert_sql, (batch_json,))
        conn.commit()
        print(f"✅ Successfully ingested micro-batch of {len(events)} records into Snowflake RAW landing zone!")
    except Exception as e:
        print(f"❌ Error inserting batch to Snowflake: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    print(f"🚀 Initializing Kafka Consumer listening to {KAFKA_BROKER} on topic '{TOPIC}'...")
    
    consumer = KafkaConsumer(
        TOPIC,
        bootstrap_servers=[KAFKA_BROKER],
        auto_offset_reset='latest',
        enable_auto_commit=True,
        group_id='snowflake-landing-group',
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )
    
    event_buffer = []
    
    try:
        for message in consumer:
            event = message.value
            event_buffer.append(event)
            print(f"Buffered trade: {event.get('trade_id')} ({len(event_buffer)}/{BATCH_SIZE})")
            
            if len(event_buffer) >= BATCH_SIZE:
                insert_microbatch_to_snowflake(event_buffer)
                event_buffer.clear()
    except KeyboardInterrupt:
        print("\nConsumer stopped.")