"""
Test Redis Connection
تأكد من أن Redis يعمل بشكل صحيح
"""
import os
import sys
import django
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

import redis
from django.conf import settings

def test_redis():
    """Test Redis connection"""
    print("=" * 60)
    print("🔴 اختبار اتصال Redis")
    print("=" * 60)
    
    try:
        # Get Redis URL
        redis_url = settings.CELERY_BROKER_URL
        print(f"\n📍 Redis URL: {redis_url[:50]}...")
        
        # Connect to Redis
        r = redis.from_url(redis_url)
        
        # Test ping
        print("\n🔄 اختبار Ping...")
        response = r.ping()
        print(f"✅ Ping Response: {response}")
        
        # Test set/get
        print("\n🔄 اختبار Set/Get...")
        r.set('test_key', 'SmartEdu Test')
        value = r.get('test_key')
        print(f"✅ Value: {value.decode('utf-8')}")
        
        # Test delete
        r.delete('test_key')
        print("✅ Key deleted")
        
        print("\n" + "=" * 60)
        print("✅ Redis يعمل بشكل صحيح!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print("\n" + "=" * 60)
        print(f"❌ خطأ في الاتصال بـ Redis:")
        print(f"   {str(e)}")
        print("\n💡 تأكد من:")
        print("   1. إضافة REDIS_URL في ملف .env")
        print("   2. URL صحيح من Upstash")
        print("   3. تثبيت المكتبات: pip install redis celery")
        print("=" * 60)
        return False

if __name__ == '__main__':
    test_redis()
