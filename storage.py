import os
import sqlite3
from datetime import datetime, date

class Storage:
    def __init__(self, db_path='data/bot.db'):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                consent BOOLEAN DEFAULT 0,
                state TEXT DEFAULT 'start',
                last_ad_date DATE
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                q1 TEXT, q2 TEXT, q3 TEXT, q4 TEXT, q5 TEXT, q6 TEXT, q7 TEXT,
                photo TEXT,
                submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(user_id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')
        
        # Set default limit if not exists
        cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('daily_limit', '2')")
        
        conn.commit()
        conn.close()

    def set_user_consent(self, user_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO users (user_id, consent) VALUES (?, 1)", (user_id,))
        conn.commit()
        conn.close()

    def has_user_consented(self, user_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT consent FROM users WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        return row and row[0] == 1

    def set_user_state(self, user_id, state):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO users (user_id, state) VALUES (?, ?)", (user_id, state))
        conn.commit()
        conn.close()

    def get_user_state(self, user_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT state FROM users WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else 'start'

    def record_ad_submission(self, user_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        today = date.today().isoformat()
        cursor.execute("UPDATE users SET last_ad_date = ? WHERE user_id = ?", (today, user_id))
        conn.commit()
        conn.close()

    def get_ads_today_count(self, user_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        today = date.today().isoformat()
        cursor.execute("SELECT COUNT(*) FROM ads WHERE user_id = ? AND date(submitted_at) = ?", (user_id, today))
        count = cursor.fetchone()[0]
        conn.close()
        return count

    def get_daily_limit(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM settings WHERE key = 'daily_limit'")
        limit = int(cursor.fetchone()[0])
        conn.close()
        return limit

    def set_daily_limit(self, limit):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('daily_limit', ?)", (str(limit),))
        conn.commit()
        conn.close()

    def get_stats(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(DISTINCT user_id) FROM users")
        users = cursor.fetchone()[0]
        
        today = date.today().isoformat()
        cursor.execute("SELECT COUNT(*) FROM ads WHERE date(submitted_at) = ?", (today,))
        ads_today = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM ads")
        ads_total = cursor.fetchone()[0]
        
        conn.close()
        return {'users': users, 'ads_today': ads_today, 'ads_total': ads_total}

    def save_ad_draft(self, user_id, data):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO ads (user_id, q1, q2, q3, q4, q5, q6, q7, photo)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id, data.get('q1'), data.get('q2'), data.get('q3'), data.get('q4'),
            data.get('q5'), data.get('q6'), data.get('q7'), data.get('photo')
        ))
        conn.commit()
        conn.close()

    def clear_user_data(self, user_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM ads WHERE user_id = ?", (user_id,))
        cursor.execute("UPDATE users SET state = 'start' WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()