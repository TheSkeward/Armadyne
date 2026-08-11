import sqlite3
from datetime import datetime


class DBHandler:
    def __init__(self, db_name, tz):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self.tz = tz

    def create_tables(self, schema_file):
        with open(schema_file) as file:
            self.cursor.executescript(file.read())
            self.conn.commit()

    def add_user(self, user_id):
        self.cursor.execute(
            "INSERT INTO sunset_reminder (user_id) VALUES (?);", (user_id,)
        )
        self.conn.commit()

    def remove_user(self, user_id):
        self.cursor.execute(
            "DELETE FROM sunset_reminder WHERE user_id = ?;", (user_id,)
        )
        self.conn.commit()

    def get_users(self):
        self.cursor.execute("SELECT user_id FROM sunset_reminder;")
        return self.cursor.fetchall()

    def is_user_opted_in(self, user_id):
        self.cursor.execute(
            "SELECT user_id FROM sunset_reminder WHERE user_id = ?;", (user_id,)
        )
        return self.cursor.fetchone() is not None

    def set_rent_paid(self, rent_paid):
        now = datetime.now(self.tz)
        self.cursor.execute(
            "INSERT OR REPLACE INTO rent_status (year, month, rent_paid) VALUES (?, ?, ?);",
            (now.year, now.month, rent_paid),
        )
        self.conn.commit()

    def is_rent_paid(self):
        now = datetime.now(self.tz)
        self.cursor.execute(
            "SELECT rent_paid FROM rent_status WHERE year = ? AND month = ?;",
            (now.year, now.month),
        )
        row = self.cursor.fetchone()
        return row is not None and bool(row["rent_paid"])

    def reminder_sent_today(self):
        today = datetime.now(self.tz).date()
        self.cursor.execute(
            "SELECT * FROM rent_reminders WHERE date = ?;", (today.isoformat(),)
        )
        return self.cursor.fetchone() is not None

    def log_reminder_sent(self):
        today = datetime.now(self.tz).date()
        self.cursor.execute(
            "INSERT INTO rent_reminders (date) VALUES (?);", (today.isoformat(),)
        )
        self.conn.commit()
