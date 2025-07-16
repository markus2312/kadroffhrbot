import asyncio
from utils import get_sheet
from config import SPREADSHEET_ID, GOOGLE_CREDENTIALS_FILE, XRAY_BASE_PORT, MESSAGE_DELAY, CONCURRENT_ACCOUNTS
from xray_manager import XrayManager
from sender import TelegramSender
import socks
import logging

logging.basicConfig(level=logging.INFO)

async def process_account(account, vpn_link, recipients_msgs, socks_port):
    phone, api_id, api_hash = account[:3]
    xray = XrayManager(vpn_link, socks_port)
    xray.start()

    proxy = (socks.SOCKS5, "127.0.0.1", socks_port)
    sender = TelegramSender(phone, int(api_id), api_hash, proxy)
    await sender.start()

    for target, message in recipients_msgs:
        await sender.send_message(target, message)
        await asyncio.sleep(MESSAGE_DELAY)

    await sender.stop()
    xray.stop()

async def main():
    recipients_data = get_sheet(SPREADSHEET_ID, "Рассылка", GOOGLE_CREDENTIALS_FILE)
    vpn_data = get_sheet(SPREADSHEET_ID, "vpn", GOOGLE_CREDENTIALS_FILE)
    accounts_data = get_sheet(SPREADSHEET_ID, "tg acc", GOOGLE_CREDENTIALS_FILE)

    # Берём из Рассылка колонки C и F (начинаем с 1, т.к. 0 - заголовки)
    recipients_msgs = []
    for row in recipients_data[1:]:
        target = row[2] if len(row) > 2 else None
        message = row[5] if len(row) > 5 else None
        if target and message:
            recipients_msgs.append((target, message))

    accounts = [acc for acc in accounts_data[1:] if len(acc) >= 3]
    vpns = [v[0] for v in vpn_data[1:] if len(v) > 0]

    tasks = []
    for i, account in enumerate(accounts):
        vpn_link = vpns[i % len(vpns)]
        socks_port = XRAY_BASE_PORT + i
        tasks.append(process_account(account, vpn_link, recipients_msgs, socks_port))
        if len(tasks) >= CONCURRENT_ACCOUNTS:
            await asyncio.gather(*tasks)
            tasks = []
    if tasks:
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
