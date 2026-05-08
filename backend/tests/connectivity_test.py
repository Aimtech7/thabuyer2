import os
import sys
import django
import redis
from django.db import connections
from django.db.utils import OperationalError

# Add backend to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

def test_db_connection():
    print("[*] Testing Database Connection...")
    db_conn = connections['default']
    try:
        db_conn.cursor()
        print("[OK] Database: CONNECTED (Supabase/Postgres)")
        return True
    except OperationalError as e:
        print(f"[FAIL] Database: FAILED - {e}")
        return False

def test_redis_connection():
    print("[*] Testing Redis Connection...")
    from django.conf import settings
    # Check for redis-related settings
    redis_url = settings.CHANNEL_LAYERS['default']['CONFIG']['hosts'][0]
    try:
        r = redis.from_url(redis_url)
        r.ping()
        print(f"[OK] Redis: CONNECTED ({redis_url})")
        return True
    except Exception as e:
        print(f"[FAIL] Redis: FAILED - {e}")
        return False

def run_all_tests():
    print("="*40)
    print("THA BUYER - Connectivity Audit")
    print("="*40)
    db_ok = test_db_connection()
    redis_ok = test_redis_connection()
    print("="*40)
    if db_ok and redis_ok:
        print("RESULT: ALL SYSTEMS GO!")
    else:
        print("RESULT: SYSTEM IMPEDIMENT DETECTED")
    print("="*40)

if __name__ == "__main__":
    run_all_tests()
