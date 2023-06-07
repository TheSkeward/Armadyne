import sqlite3


class DBHandler:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)
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
        return self.cursor.fetchone()
