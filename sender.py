from telethon import TelegramClient
import socks
import asyncio
import logging

logging.basicConfig(level=logging.INFO)

class TelegramSender:
    def __init__(self, phone, api_id, api_hash, proxy):
        self.phone = phone
        self.api_id = api_id
        self.api_hash = api_hash
        self.proxy = proxy
        self.client = TelegramClient(phone, api_id, api_hash, proxy=proxy)

    async def start(self):
        await self.client.start(phone=self.phone)

    async def send_message(self, target, message):
        try:
            await self.client.send_message(target, message)
            logging.info(f"Отправлено на {target} с {self.phone}")
        except Exception as e:
            logging.error(f"Ошибка отправки на {target} с {self.phone}: {e}")

    async def stop(self):
        await self.client.disconnect()
