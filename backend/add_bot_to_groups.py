"""
Script لإضافة البوت إلى القروبات المُنشأة
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


async def add_bot_to_groups(api_id, api_hash, phone_number, groups_data, bot_username):
    """إضافة البوت إلى القروبات"""
    
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
        print(f"[OK] Connected to Telegram")
        
        for i, group in enumerate(groups_data):
            group_name = group['group_name']
            chat_id = group['chat_id']
            
            print(f"\n[{i+1}/{len(groups_data)}] Adding bot to: {group_name}")
            
            try:
                # إضافة البوت
                await client.add_chat_members(
                    chat_id=chat_id,
                    user_ids=[f"@{bot_username}"]
                )
                
                print(f"   [OK] Bot @{bot_username} added successfully")
                
                # ترقية البوت إلى مدير
                try:
                    await client.promote_chat_member(
                        chat_id=chat_id,
                        user_id=f"@{bot_username}",
                        privileges={
                            'can_manage_chat': True,
                            'can_delete_messages': True,
                            'can_manage_video_chats': True,
                            'can_restrict_members': True,
                            'can_promote_members': False,
                            'can_change_info': True,
                            'can_invite_users': True,
                            'can_pin_messages': True
                        }
                    )
                    print(f"   [OK] Bot promoted to admin")
                except Exception as e:
                    print(f"   [WARN] Could not promote bot: {e}")
                
                results.append({
                    'success': True,
                    'group_name': group_name,
                    'chat_id': chat_id
                })
                
                # تأخير
                if i < len(groups_data) - 1:
                    print(f"   [WAIT] Waiting 3 seconds...")
                    await asyncio.sleep(3)
                    
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
        sys.exit(1)
    
    with open(groups_file, 'r', encoding='utf-8') as f:
        groups_data = json.load(f)
    
    # Credentials
    api_id = settings.TELEGRAM_API_ID
    api_hash = settings.TELEGRAM_API_HASH
    phone_number = "+966558048004"  # رقمك
    
    # اسم البوت
    bot_username = input("Enter bot username (without @): ").strip()
    
    if not bot_username:
        print("[ERROR] Bot username is required")
        sys.exit(1)
    
    print(f"\n[*] Adding bot @{bot_username} to {len(groups_data)} groups...\n")
    
    # تشغيل
    results = asyncio.run(add_bot_to_groups(
        api_id, api_hash, phone_number, 
        groups_data, bot_username
    ))
    
    # عرض ملخص
    success_count = sum(1 for r in results if r['success'])
    print(f"\n{'='*50}")
    print(f"[RESULT] Final result: {success_count}/{len(results)} succeeded")
    print(f"{'='*50}\n")
