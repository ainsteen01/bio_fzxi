from fastapi import FastAPI, HTTPException, BackgroundTasks
from migration_service import SupabaseMigrationService
from supabase_config import supabase
from typing import Optional
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="SQLite to Supabase Migration Service")

# Initialize migration service
migration_service = SupabaseMigrationService()

@app.get("/")
def root():
    return {
        "message": "SQLite to Supabase Migration Service",
        "endpoints": {
            "/migrate-all": "Migrate all data from SQLite to Supabase",
            "/migrate-recent/{days}": "Migrate recent data (last N days)",
            "/migration-status": "Check migration status",
            "/supabase-data": "Query data from Supabase",
            "/trigger-sync": "Trigger sync from device to SQLite then to Supabase"
        }
    }

@app.post("/migrate-all")
def migrate_all_data(background_tasks: BackgroundTasks):
    """Migrate all data from SQLite to Supabase"""
    try:
        # Run migration in background to avoid timeout
        background_tasks.add_task(run_migration)
        return {
            "message": "Migration started in background",
            "status": "processing"
        }
    except Exception as e:
        logger.error(f"Error starting migration: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def run_migration():
    """Background task for migration"""
    result = migration_service.migrate_all_data()
    logger.info(f"Migration completed: {result}")

@app.get("/migration-status")
def get_migration_status():
    """Get current migration status"""
    try:
        stats = migration_service.get_migration_stats()
        return stats
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/supabase-data")
def get_supabase_data(
    emp_id: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
):
    """Query data directly from Supabase"""
    try:
        query = supabase.table("att_table")\
            .select("*")\
            .order("time_stamp", desc=True)\
            .range(offset, offset + limit - 1)
        
        if emp_id:
            query = query.eq("emp_id", emp_id)
        
        if start_date:
            query = query.gte("time_stamp", start_date)
        
        if end_date:
            query = query.lte("time_stamp", end_date)
        
        response = query.execute()
        
        return {
            "total": len(response.data),
            "offset": offset,
            "limit": limit,
            "data": response.data
        }
    
    except Exception as e:
        logger.error(f"Error querying Supabase: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/clear-and-restart")
def clear_and_restart_migration():
    """Clear Supabase data and restart migration (use carefully)"""
    try:
        # Warning: This deletes all data in Supabase!
        confirmation = input("Type 'CONFIRM' to proceed: ")  # In production, use a proper confirmation
        
        if confirmation == "CONFIRM":
            response = supabase.table("att_table").delete().neq("id", 0).execute()
            return {"message": f"Cleared {len(response.data)} records from Supabase"}
        else:
            return {"message": "Operation cancelled"}
            
    except Exception as e:
        logger.error(f"Error clearing data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Keep your original endpoints if needed, but modified to use Supabase
@app.get("/getAttendanceStats")
def get_attendance_stats():
    """Get attendance statistics from Supabase"""
    try:
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Get today's count
        today_response = supabase.table("att_table")\
            .select("*", count="exact")\
            .like("time_stamp", f"{today}%")\
            .execute()
        
        # Get unique employees
        employees_response = supabase.table("att_table")\
            .select("emp_id")\
            .execute()
        
        unique_emps = len(set([r['emp_id'] for r in employees_response.data]))
        
        # Get total count
        total_response = supabase.table("att_table")\
            .select("*", count="exact")\
            .execute()
        
        return {
            "total_records": len(total_response.data),
            "today_records": len(today_response.data),
            "unique_employees": unique_emps
        }
    
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))