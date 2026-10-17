import os
import logging
from maxapi import Bot as MaxClient
from storage import Storage
from texts import TEXTS

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MaxRentBot:
    def __init__(self, token, admin_id, target_channel_id):
        self.token = token
        self.admin_id = admin_id
        self.target_channel_id = target_channel_id
        self.client = MaxClient(token)
        self.storage = Storage()
        self.current_step = {}
        self.user_ads = {}

    async def start(self, user_id, username):
        if not self.storage.has_user_consented(user_id):
            await self.client.send_message(user_id, TEXTS['legal_warning'])
            self.storage.set_user_state(user_id, 'awaiting_consent')
            return

        self.storage.set_user_state(user_id, 'awaiting_question_1')
        await self.client.send_message(user_id, TEXTS['q1'])

    async def handle_message(self, user_id, text):
        state = self.storage.get_user_state(user_id)
        if state == 'awaiting_consent':
            if text.lower() == 'да':
                self.storage.set_user_consent(user_id)
                self.storage.set_user_state(user_id, 'awaiting_question_1')
                await self.client.send_message(user_id, TEXTS['q1'])
            else:
                await self.client.send_message(user_id, TEXTS['consent_denied'])
            return

        if state.startswith('awaiting_question'):
            q_num = int(state.split('_')[-1])
            self.user_ads[user_id] = self.user_ads.get(user_id, {})
            self.user_ads[user_id][f'q{q_num}'] = text
            if q_num < 7:
                next_state = f'awaiting_question_{q_num + 1}'
                self.storage.set_user_state(user_id, next_state)
                await self.client.send_message(user_id, TEXTS[f'q{q_num + 1}'])
            else:
                self.storage.set_user_state(user_id, 'awaiting_photo')
                self.client.send_message(user_id, TEXTS['photo_request'])
            return
        if state == 'awaiting_photo':
            self.user_ads[user_id]['photo'] = text
            self.storage.set_user_state(user_id, 'awaiting_review')
            self._send_for_review(user_id)
            return

    async def _send_for_review(self, user_id):
        ad = self.user_ads[user_id]
        review_text = (
            f"📝 Новое объявление на модерацию:\n\n"
            f"1. {ad['q1']}\n"
            f"2. {ad['q2']}\n"
            f"3. {ad['q3']}\n"
            f"4. {ad['q4']}\n"
            f"5. {ad['q5']}\n"
            f"6. {ad['q6']}\n"
            f"7. {ad['q7']}\n"
            f"Фото: {ad['photo']}\n\n"
            f"👤 Пользователь: {user_id}\n"
            f"🔗 Профиль: https://max.ru/u{user_id}"
        )
        await self.client.send_message(self.admin_id, review_text)
        await self.client.send_message(user_id, TEXTS['awaiting_approval'])

    def admin_approve(self, user_id):
        ad = self.user_ads.get(user_id)
        if not ad:
            self.client.send_message(self.admin_id, "❌ Объявление не найдено.")
            return
        self.client.send_message(self.admin_id, f"✅ Объявление пользователя {user_id} одобрено.")
        self.client.send_message(user_id, TEXTS['approved'])
        self.storage.record_ad_submission(user_id)

    def admin_reject(self, user_id, reason="Не указано"):
        self.client.send_message(self.admin_id, f"❌ Объявление пользователя {user_id} отклонено. Причина: {reason}")
        self.client.send_message(user_id, TEXTS['rejected'].format(reason=reason))
        self.storage.clear_user_data(user_id)

    def admin_stats(self):
        stats = self.storage.get_stats()
        msg = (
            f"📊 Статистика бота:\n"
            f"👥 Пользователей: {stats['users']}\n"
            f"📄 Объявлений сегодня: {stats['ads_today']}\n"
            f"📄 Всего объявлений: {stats['ads_total']}"
        )
        self.client.send_message(self.admin_id, msg)

    def admin_set_limit(self, limit):
        self.storage.set_daily_limit(limit)
        self.client.send_message(self.admin_id, f"✅ Лимит объявлений установлен: {limit} в день.")
