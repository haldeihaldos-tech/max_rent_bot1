import os
import hmac
import hashlib
import logging
from flask import Flask, request, abort
from bot import MaxRentBot
from storage import Storage

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Читаем из переменных окружения Bothost
TOKEN = os.getenv('ACCESS_TOKEN')
WEBHOOK_SECRET = os.getenv('WEBHOOK_SECRET')
ADMIN_ID = int(os.getenv('ADMIN_USER_ID'))
TARGET_CHANNEL_ID = int(os.getenv('TARGET_CHANNEL_ID'))

bot = MaxRentBot(TOKEN, ADMIN_ID, TARGET_CHANNEL_ID)
storage = Storage()

@app.route('/webhook', methods=['POST'])
def webhook():
    # Проверка секрета для безопасности
    signature = request.headers.get('X-Max-Bot-Api-Secret')
    if not signature or not WEBHOOK_SECRET:
        logger.error("Secret not configured")
        abort(403)

    # Сравнение секретов
    if not hmac.compare_digest(signature, WEBHOOK_SECRET):
        logger.warning("Invalid webhook secret")
        abort(403)

    update = request.json
    if not update:
        abort(400)

    # Обработка обновления
    bot.handle_update(update)
    
    return {"ok": True}

if __name__ == '__main__':
    # Запуск на порту, который требует Bothost (обычно 8080 или 5000)
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))