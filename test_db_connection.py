from db_models import SessionLocal, AttData

def test_sqlite_connection():
    """Test connection to your SQLite database"""
    try:
        session = SessionLocal()
        
        # Count records
        count = session.query(AttData).count()
        print(f"✅ Successfully connected to: /Users/netcom/bmsupa/biodb.db")
        print(f"📊 Total records in ATT_TABLE: {count}")
        
        # Show first 5 records
        print("\n📝 First 5 records:")
        records = session.query(AttData).limit(5).all()
        for record in records:
            print(f"  ID: {record.id}, Emp: {record.emp_id}, Name: {record.emp_name}, Time: {record.time_stamp}")
        
        session.close()
        return True
        
    except Exception as e:
        print(f"❌ Error connecting to database: {e}")
        return False

if __name__ == "__main__":
    test_sqlite_connection()