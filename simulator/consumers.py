# consumers.py
from channels.generic.websocket import AsyncWebsocketConsumer
import json
from .analytics import NeuroAnalytics
import asyncio

class AnalyticsConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        self.emotion = 'relax'
        asyncio.create_task(self.send_analytics_data())
    
    async def send_analytics_data(self):
        while True:
            try:
                plot_html, explanation = NeuroAnalytics.create_plots(self.emotion)
                await self.send(json.dumps({
                    'plot_html': plot_html,
                    'explanation': explanation
                }))
                await asyncio.sleep(2)  # Обновление каждые 2 секунды
            except Exception as e:
                print(f"Error: {str(e)}")
                break