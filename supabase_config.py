import os
from supabase import create_client, Client
from dotenv import load_dotenv
import sys

# Load environment variables
load_dotenv()

# Get credentials from .env
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")  # Using publishable key, not secret key

# Validate credentials
if not SUPABASE_URL:
    print("❌ SUPABASE_URL not found in .env file")
    print("Please add: SUPABASE_URL=https://your-project-ref.supabase.co")
    sys.exit(1)

if not SUPABASE_KEY:
    print("❌ SUPABASE_PUBLISHABLE_KEY not found in .env file")
    print("Please add: SUPABASE_SERVICE_KEY=sb_publishable_...")
    sys.exit(1)

# Print confirmation (partial for security)
print(f"✅ SUPABASE_URL found: {SUPABASE_URL[:20]}...")
print(f"✅ SUPABASE_KEY found: {SUPABASE_KEY[:20]}...")

# Create Supabase client
try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("✅ Supabase client created successfully!")
except Exception as e:
    print(f"❌ Error creating Supabase client: {e}")
    print("\nPossible issues:")
    print("1. Your publishable key might be incorrect or expired")
    print("2. Your Supabase project might not be active")
    print("3. Network connectivity issues")
    sys.exit(1)
