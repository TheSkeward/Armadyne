import sqlite3
from datetime import datetime


class DBHandler:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

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
        year, month = datetime.now().year, datetime.now().month
        self.cursor.execute(
            "INSERT OR REPLACE INTO rent_status (year, month, rent_paid) VALUES (?, ?, ?);",
            (year, month, rent_paid),
        )
        self.conn.commit()

    def is_rent_paid(self):
        year, month = datetime.now().year, datetime.now().month
        self.cursor.execute(
            "SELECT rent_paid FROM rent_status WHERE year = ? AND month = ?;",
            (year, month),
        )
        row = self.cursor.fetchone()
        return row and row["rent_paid"]
