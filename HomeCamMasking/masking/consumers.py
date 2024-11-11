# masking/consumers.py

from channels.generic.websocket import WebsocketConsumer

class MaskConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()  # WebSocket 연결 수락

    def disconnect(self, close_code):
        pass

    def receive(self, text_data=None, bytes_data=None):
        self.send(text_data="Message received")  # 간단한 테스트 응답
