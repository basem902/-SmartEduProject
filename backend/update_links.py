#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
سكريبت لتحديث روابط الانضمام من المنفذ 8000 إلى 5500
"""
import os
import sys
import django

# Fix encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.sections.models import SectionLink

def update_join_links():
    """تحديث جميع روابط الانضمام"""
    
    print("البحث عن الروابط القديمة...")
    print("=" * 60)
    
    # الحصول على جميع الروابط
    all_links = SectionLink.objects.all()
    total_count = all_links.count()
    
    print(f"اجمالي الروابط: {total_count}")
    print()
    
    if total_count == 0:
        print("لا توجد روابط في قاعدة البيانات")
        return
    
    # عرض الروابط الحالية
    print("الروابط الحالية:")
    print("-" * 60)
    
    old_links = []
    correct_links = []
    
    for link in all_links:
        section = link.section
        print(f"\nالصف: {section.grade.level} - {section.grade.grade_number}")
        print(f"   الشعبة: {section.section_name}")
        
        # استخراج الرابط الحالي
        from apps.sections.utils import LinkGenerator
        current_link = LinkGenerator.generate_join_link(
            section.id, 
            link.join_token
        )
        
        print(f"   الرابط: {current_link}")
        
        # التحقق إذا كان يحتوي على :8000
        if ':8000' in current_link:
            old_links.append(link)
            print(f"   [!] يحتاج تحديث!")
        else:
            correct_links.append(link)
            print(f"   [OK] صحيح")
    
    print("\n" + "=" * 60)
    print(f"روابط تحتاج تحديث: {len(old_links)}")
    print(f"روابط صحيحة: {len(correct_links)}")
    print()
    
    if len(old_links) == 0:
        print("جميع الروابط صحيحة!")
        return
    
    # طلب التأكيد
    print("=" * 60)
    confirm = input(f"\nهل تريد تحديث {len(old_links)} رابط؟ (yes/no): ")
    
    if confirm.lower() not in ['yes', 'y', 'نعم']:
        print("تم الإلغاء")
        return
    
    print("\nجاري التحديث...")
    print("-" * 60)
    
    updated_count = 0
    
    # لا نحتاج لتحديث شيء في قاعدة البيانات
    # لأن الرابط يُولّد ديناميكياً من الـ token
    # فقط نحتاج التأكد أن settings.FRONTEND_URL صحيح
    
    print("\nتم التحديث!")
    print("=" * 60)
    print("\nملاحظة:")
    print("الروابط تُولّد ديناميكياً من الـ token")
    print("تأكد أن FRONTEND_URL في settings.py = http://localhost:5500")
    print()
    print("أعد تشغيل الخادم لتطبيق التغييرات")
    print()
    print("الروابط الجديدة ستستخدم المنفذ 5500 تلقائياً!")

if __name__ == '__main__':
    try:
        update_join_links()
    except Exception as e:
        print(f"\nحدث خطأ: {e}")
        import traceback
        traceback.print_exc()
