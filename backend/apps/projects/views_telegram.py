import requests
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Project
from apps.sections.models import TelegramGroup


def _tg_api(token, method, params=None):
    url = f"https://api.telegram.org/bot{token}/{method}"
    try:
        resp = requests.get(url, params=params or {}, timeout=10)
        return resp.json()
    except Exception as e:
        return {"ok": False, "error": str(e)}


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_bot_status(request, project_id):
    token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
    if not token:
        return Response({
            'success': False,
            'error': 'TELEGRAM_BOT_TOKEN not configured'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    try:
        project = Project.objects.get(id=project_id, teacher__user=request.user)
    except Project.DoesNotExist:
        return Response({'error': 'المشروع غير موجود'}, status=status.HTTP_404_NOT_FOUND)

    me = _tg_api(token, 'getMe')
    if not me.get('ok'):
        return Response({'error': 'فشل getMe', 'details': me}, status=status.HTTP_502_BAD_GATEWAY)
    bot_id = me['result']['id']

    results = []
    ok_count = 0
    admin_count = 0
    missing_count = 0

    for section in project.sections.all():
        item = {
            'section_id': section.id,
            'section_name': section.section_name,
            'chat_id': None,
            'invite_link': None,
            'is_bot_added': False,
            'is_bot_admin': False,
            'bot_member_status': None,
            'members_count': None,
            'error': None,
        }
        tg = getattr(section, 'telegram_group', None)
        if not tg or not tg.chat_id:
            item['error'] = 'لا يوجد TelegramGroup أو chat_id'
            results.append(item)
            missing_count += 1
            continue

        item['chat_id'] = tg.chat_id
        item['invite_link'] = tg.invite_link

        member = _tg_api(token, 'getChatMember', {
            'chat_id': tg.chat_id,
            'user_id': bot_id
        })
        if member.get('ok'):
            m = member['result']
            status_text = m.get('status')
            item['bot_member_status'] = status_text
            is_added = status_text not in ['left', 'kicked']
            is_admin = status_text in ['administrator', 'creator']
            item['is_bot_added'] = is_added
            item['is_bot_admin'] = is_admin
            if is_added:
                ok_count += 1
            if is_admin:
                admin_count += 1

            perms = {}
            for k, v in m.items():
                if k.startswith('can_'):
                    perms[k] = v
            tg.is_bot_added = is_added
            tg.is_bot_admin = is_admin
            tg.bot_permissions = perms
        else:
            item['error'] = member

        count = _tg_api(token, 'getChatMemberCount', {
            'chat_id': tg.chat_id
        })
        if count.get('ok'):
            item['members_count'] = count['result']
            tg.members_count = count['result']
        tg.save(update_fields=['is_bot_added', 'is_bot_admin', 'bot_permissions', 'members_count', 'updated_at'])

        results.append(item)

    summary = {
        'total_sections': project.sections.count(),
        'with_group': len([r for r in results if r['chat_id'] is not None]),
        'bot_added': ok_count,
        'bot_admin': admin_count,
        'missing_group': missing_count,
    }

    return Response({
        'success': True,
        'project_id': project.id,
        'bot_id': bot_id,
        'summary': summary,
        'results': results
    }, status=status.HTTP_200_OK)
