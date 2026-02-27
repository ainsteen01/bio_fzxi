from sqlalchemy import func
from db_models import AttData, SessionLocal  # Import from db_models, not itself
from supabase_config import supabase
import time
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SupabaseMigrationService:
    def __init__(self):
        self.db_session = SessionLocal()
        self.batch_size = 100
        
    def get_all_sqlite_records(self, limit=None, offset=None):
        """Fetch records from SQLite"""
        try:
            query = self.db_session.query(AttData)
            if limit:
                query = query.limit(limit)
            if offset:
                query = query.offset(offset)
            records = query.all()
            logger.info(f"📦 Fetched {len(records)} records from SQLite")
            return records
        except Exception as e:
            logger.error(f"Error fetching from SQLite: {e}")
            return []
    
    def check_record_exists_in_supabase(self, emp_id, timestamp):
        """Check if record exists in Supabase"""
        try:
            response = supabase.table("att_table")\
                .select("id")\
                .eq("emp_id", emp_id)\
                .eq("time_stamp", timestamp)\
                .execute()
            return len(response.data) > 0
        except Exception as e:
            logger.error(f"Error checking Supabase: {e}")
            return False
    
    def migrate_all_data(self):
        """Migrate all data from SQLite to Supabase"""
        try:
            # Get total count
            total_records = self.db_session.query(AttData).count()
            logger.info(f"📊 Total records in SQLite: {total_records}")
            
            if total_records == 0:
                return {"status": "success", "message": "No records to migrate"}
            
            migrated_count = 0
            skipped_count = 0
            failed_count = 0
            
            for offset in range(0, total_records, self.batch_size):
                # Get batch from SQLite
                batch_records = self.get_all_sqlite_records(
                    limit=self.batch_size, 
                    offset=offset
                )
                
                records_to_insert = []
                
                for record in batch_records:
                    exists = self.check_record_exists_in_supabase(
                        record.emp_id, 
                        record.time_stamp
                    )
                    
                    if not exists:
                        records_to_insert.append({
                            "emp_id": record.emp_id,
                            "emp_name": record.emp_name,
                            "time_stamp": record.time_stamp
                        })
                    else:
                        skipped_count += 1
                
                # Insert batch
                if records_to_insert:
                    try:
                        response = supabase.table("att_table")\
                            .insert(records_to_insert)\
                            .execute()
                        migrated_count += len(records_to_insert)
                        logger.info(f"✅ Inserted {len(records_to_insert)} records")
                    except Exception as e:
                        failed_count += len(records_to_insert)
                        logger.error(f"❌ Batch failed: {e}")
                
                # Show progress
                progress = ((offset + self.batch_size) / total_records) * 100
                logger.info(f"📊 Progress: {min(progress, 100):.1f}%")
                
                time.sleep(0.5)  # Rate limiting
            
            return {
                "status": "success",
                "total_in_sqlite": total_records,
                "migrated": migrated_count,
                "skipped": skipped_count,
                "failed": failed_count
            }
            
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            return {"status": "error", "message": str(e)}
        finally:
            self.db_session.close()
    
    def get_migration_stats(self):
        """Get migration statistics"""
        try:
            # SQLite stats
            sqlite_count = self.db_session.query(AttData).count()
            
            # Supabase stats
            supabase_response = supabase.table("att_table")\
                .select("*", count="exact")\
                .execute()
            
            supabase_count = len(supabase_response.data)
            
            return {
                "sqlite_records": sqlite_count,
                "supabase_records": supabase_count,
                "remaining": max(0, sqlite_count - supabase_count),
                "percentage_complete": (supabase_count / sqlite_count * 100) if sqlite_count > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {"error": str(e)}
        finally:
            self.db_session.close()