#!/usr/bin/env python
"""
فحص إعدادات CORS
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.conf import settings

print("=" * 60)
print("🌐 فحص إعدادات CORS")
print("=" * 60)

print(f"\n✅ CORS_ALLOWED_ORIGINS:")
for origin in settings.CORS_ALLOWED_ORIGINS:
    print(f"   - {origin}")

print(f"\n✅ CORS_ALLOW_CREDENTIALS: {settings.CORS_ALLOW_CREDENTIALS}")
print(f"✅ CORS_ALLOW_ALL_ORIGINS: {getattr(settings, 'CORS_ALLOW_ALL_ORIGINS', False)}")

print("\n" + "=" * 60)
print("📊 الحالة:")
print("=" * 60)

if not settings.CORS_ALLOWED_ORIGINS:
    print("⚠️ تحذير: لا توجد Origins مسموح بها!")
    print("   → أضف http://localhost:5500 للـ .env")
else:
    print(f"✅ عدد Origins المسموح بها: {len(settings.CORS_ALLOWED_ORIGINS)}")
    
    if 'http://localhost:5500' in settings.CORS_ALLOWED_ORIGINS:
        print("✅ localhost:5500 مسموح ✓")
    else:
        print("⚠️ localhost:5500 غير مسموح!")

print("\n" + "=" * 60)
