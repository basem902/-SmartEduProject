"""
Script لتطبيق صلاحيات read-only على القروبات الموجودة
"""
import os
import sys
import django
import asyncio
import json

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# إعداد Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.conf import settings
from pyrogram import Client
from pyrogram.types import ChatPermissions


async def set_permissions(api_id, api_hash, phone_number, groups_data):
    """تطبيق صلاحيات read-only على القروبات"""
    
    # Session path
    session_dir = os.path.join(os.path.dirname(__file__), 'sessions')
    session_name = f"smartedu_{phone_number.replace('+', '').replace(' ', '')}"
    session_path = os.path.join(session_dir, session_name)
    
    # Client
    client = Client(
        session_path,
        api_id=api_id,
        api_hash=api_hash,
        phone_number=phone_number
    )
    
    results = []
    
    try:
        await client.start()
        print(f"[OK] Connected to Telegram\n")
        
        for i, group in enumerate(groups_data):
            group_name = group['group_name']
            chat_id = group['chat_id']
            
            print(f"[{i+1}/{len(groups_data)}] Setting permissions for: {group_name}")
            
            try:
                # تطبيق صلاحيات مقيدة
                await client.set_chat_permissions(
                    chat_id=chat_id,
                    permissions=ChatPermissions(
                        can_send_messages=False,
                        can_send_media_messages=False,
                        can_send_polls=False,
                        can_send_other_messages=False,
                        can_add_web_page_previews=False,
                        can_change_info=False,
                        can_invite_users=True,  # يمكنهم دعوة أعضاء فقط
                        can_pin_messages=False
                    )
                )
                
                print(f"   [OK] Permissions applied (read-only for members)")
                
                results.append({
                    'success': True,
                    'group_name': group_name,
                    'chat_id': chat_id
                })
                
                # تأخير قصير
                if i < len(groups_data) - 1:
                    await asyncio.sleep(1)
                    
            except Exception as e:
                results.append({
                    'success': False,
                    'group_name': group_name,
                    'chat_id': chat_id,
                    'error': str(e)
                })
                print(f"   [FAIL] Error: {e}")
        
    finally:
        await client.stop()
    
    return results


if __name__ == '__main__':
    # قراءة القروبات من الملف
    groups_file = 'telegram_groups_results.json'
    
    if not os.path.exists(groups_file):
        print(f"[ERROR] File not found: {groups_file}")
        print(f"[INFO] Please create groups first using create_groups_standalone.py")
        sys.exit(1)
    
    with open(groups_file, 'r', encoding='utf-8') as f:
        groups_data = json.load(f)
    
    # Credentials
    api_id = settings.TELEGRAM_API_ID
    api_hash = settings.TELEGRAM_API_HASH
    phone_number = "+966558048004"  # رقمك
    
    print(f"[*] Found {len(groups_data)} groups in {groups_file}")
    print(f"[*] Applying read-only permissions...\n")
    
    # تشغيل
    results = asyncio.run(set_permissions(
        api_id, api_hash, phone_number, groups_data
    ))
    
    # عرض ملخص
    success_count = sum(1 for r in results if r['success'])
    print(f"\n{'='*50}")
    print(f"[RESULT] Final result: {success_count}/{len(results)} succeeded")
    print(f"{'='*50}\n")
    
    if success_count == len(results):
        print("[SUCCESS] All groups now have read-only permissions!")
        print("[INFO] Only you and bot can send messages")
    else:
        print("[WARNING] Some groups failed. Check the output above.")
