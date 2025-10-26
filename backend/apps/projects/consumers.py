"""
WebSocket Consumer for Telegram Send Progress
"""
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async


class TelegramSendConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time telegram sending progress"""
    
    async def connect(self):
        """Handle WebSocket connection"""
        self.project_id = self.scope['url_route']['kwargs']['project_id']
        self.room_group_name = f'telegram_send_{self.project_id}'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send connection confirmation
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': 'تم الاتصال بنجاح'
        }))
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        """Receive message from WebSocket"""
        try:
            data = json.loads(text_data)
            command = data.get('command')
            
            if command == 'start_sending':
                # Trigger sending process
                await self.start_sending_process(data.get('sections', []))
                
        except Exception as e:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': str(e)
            }))
    
    async def start_sending_process(self, section_ids):
        """Start the telegram sending process"""
        from apps.projects.models import Project
        from apps.projects.telegram_sender import send_project_with_progress
        
        try:
            project = await database_sync_to_async(Project.objects.get)(id=self.project_id)
            
            # Send initial status
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'send_progress',
                    'data': {
                        'type': 'started',
                        'message': f'📡 بدء إرسال المشروع: {project.title}'
                    }
                }
            )
            
            # Execute sending with progress updates
            await send_project_with_progress(project, self.room_group_name, section_ids)
            
        except Exception as e:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'send_progress',
                    'data': {
                        'type': 'error',
                        'message': f'❌ خطأ: {str(e)}'
                    }
                }
            )
    
    async def send_progress(self, event):
        """Send progress update to WebSocket"""
        await self.send(text_data=json.dumps(event['data']))
