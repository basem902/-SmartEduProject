import requests
import json

url = "http://localhost:8000/api/sections/verify-student-join/"
data = {
    "student_name": "ريماس باسم محمد الحجري",
    "section_id": 1
}

print("\n🧪 اختبار API مباشرة")
print("=" * 60)
print(f"URL: {url}")
print(f"Data: {json.dumps(data, ensure_ascii=False)}")
print()

try:
    response = requests.post(url, json=data)
    print(f"📡 الحالة: {response.status_code}")
    print(f"\n📊 النتيجة:")
    result = response.json()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    if result.get('success'):
        print("\n✅ النجاح!")
        if result.get('telegram_group'):
            print(f"   📱 رابط القروب: {result['telegram_group']['invite_link']}")
        else:
            print("   ❌ telegram_group غير موجود في Response!")
    else:
        print(f"\n❌ الفشل: {result.get('message')}")
        
except Exception as e:
    print(f"\n❌ خطأ: {str(e)}")
