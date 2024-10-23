import telethon
from telethon import TelegramClient, events
import asyncio
import json
from datetime import datetime
from admin_config import API_ID, API_HASH, SESSION_NAME, TARGET_CHAT_ID, PROXY_BOT_USERNAME


class AdminBot:
    def __init__(self):
        self.client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
        self.keywords = self.read_keywords('keywords.txt')
        self.blacklist_words = self.read_blacklist('blacklist_words.txt')
        self.blacklist_users = self.read_blacklist('blacklist_users.txt')
        self.whitelist = self.read_whitelist('whitelist.txt')

    @staticmethod
    def read_file(file_path, default=None):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            with open(file_path, 'w', encoding='utf-8') as f:
                if default:
                    for item in default:
                        f.write(f"{item}\n")
            return default or []

    def read_keywords(self, file_path):
        return self.read_file(file_path, ['default_keyword'])

    def read_blacklist(self, file_path):
        return self.read_file(file_path, [])

    def read_whitelist(self, file_path):
        return self.read_file(file_path, ['your_admin_id'])

    @staticmethod
    def write_to_file(file_path, items):
        with open(file_path, 'w', encoding='utf-8') as f:
            for item in items:
                f.write(f"{item}\n")

    async def setup_handlers(self):
        @self.client.on(events.NewMessage(chats=TARGET_CHAT_ID))
        async def command_handler(event):
            if not event.message or not event.message.text:
                return

            text = event.message.text

            if "sent command:" in text:
                command_text = text.split("sent command:")[-1].strip()

                if command_text.startswith('/add_keyword'):
                    keyword = command_text.replace('/add_keyword', '').strip()
                    if keyword:
                        self.keywords.append(keyword)
                        self.write_to_file('keywords.txt', self.keywords)
                        await event.respond(f'Keyword "{keyword}" added successfully.')

                elif command_text.startswith('/remove_keyword'):
                    keyword = command_text.replace('/remove_keyword', '').strip()
                    if keyword in self.keywords:
                        self.keywords.remove(keyword)
                        self.write_to_file('keywords.txt', self.keywords)
                        await event.respond(f'Keyword "{keyword}" removed successfully.')
                    else:
                        await event.respond(f'Keyword "{keyword}" not found.')

                elif command_text.startswith('/list_keywords'):
                    keywords_list = '\n'.join(self.keywords)
                    await event.respond(f'Current keywords:\n{keywords_list}')

            elif "Message from" in text:
                message_text = text.split(":")[-1].strip()

                if any(keyword.lower() in message_text.lower() for keyword in self.keywords):
                    message_data = {
                        'timestamp': datetime.now().isoformat(),
                        'message': message_text,
                        'matched_keywords': [k for k in self.keywords if k.lower() in message_text.lower()]
                    }
                    try:
                        with open('saved_messages.json', 'r', encoding='utf-8') as f:
                            messages = json.load(f)
                    except (FileNotFoundError, json.JSONDecodeError):
                        messages = []

                    messages.append(message_data)

                    with open('saved_messages.json', 'w', encoding='utf-8') as f:
                        json.dump(messages, f, ensure_ascii=False, indent=2)

                    await event.respond(f"Message saved with keywords: {', '.join(message_data['matched_keywords'])}")

    async def start(self):
        print("Starting admin bot...")
        await self.client.start()
        await self.setup_handlers()
        print("Admin bot started successfully.")
        await self.client.run_until_disconnected()


if __name__ == "__main__":
    bot = AdminBot()
    asyncio.run(bot.start())