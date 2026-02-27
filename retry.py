#!/usr/bin/env python3
"""
Script to retry failed migrations from SQLite to Supabase
Run: python3 retry.py
"""

# IMPORTANT: Import the client instance, not the module
from supabase_config import supabase  # ✅ This is correct
from db_models import SessionLocal, AttData
import logging
import time

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def retry_failed():
    """Retry failed migrations"""
    db_session = SessionLocal()
    
    try:
        # Get all SQLite records
        sqlite_records = db_session.query(AttData).all()
        logger.info(f"📦 Found {len(sqlite_records)} records in SQLite")
        
        # Get existing Supabase records - using the correct client
        response = supabase.table("att_table").select("emp_id, time_stamp").execute()
        existing = {(r['emp_id'], r['time_stamp']) for r in response.data}
        logger.info(f"📊 Found {len(existing)} existing records in Supabase")
        
        # Find records not in Supabase
        to_retry = []
        for record in sqlite_records:
            if (record.emp_id, record.time_stamp) not in existing:
                to_retry.append({
                    "emp_id": record.emp_id,
                    "emp_name": record.emp_name,
                    "time_stamp": record.time_stamp
                })
        
        logger.info(f"🔄 Found {len(to_retry)} records to retry")
        
        if not to_retry:
            logger.info("✅ No records to retry!")
            return
        
        # Retry in batches
        batch_size = 50
        successful = 0
        
        for i in range(0, len(to_retry), batch_size):
            batch = to_retry[i:i + batch_size]
            
            try:
                response = supabase.table("att_table").insert(batch).execute()
                successful += len(batch)
                logger.info(f"  ✅ Retried batch {i//batch_size + 1}: {len(batch)} records")
                time.sleep(0.5)  # Rate limiting
                
            except Exception as e:
                logger.error(f"  ❌ Batch failed: {e}")
                # Try individual records
                for record in batch:
                    try:
                        response = supabase.table("att_table").insert([record]).execute()
                        successful += 1
                        logger.info(f"    ✅ Retried record for emp {record['emp_id']}")
                        time.sleep(0.1)
                    except Exception as ind_error:
                        logger.error(f"    ❌ Failed record for emp {record['emp_id']}: {ind_error}")
        
        logger.info(f"✅ Successfully retried {successful}/{len(to_retry)} records")
        
    finally:
        db_session.close()

if __name__ == "__main__":
    retry_failed()