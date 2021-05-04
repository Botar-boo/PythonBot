import sqlite3
import shutil


class SQLighter:

    def __init__(self, database):
        self.connection = sqlite3.connect(database)
        shutil.copyfile("db.db", "new_db.db")
        self.cursor = self.connection.cursor()

    def get_subscriptions(self, status=True):
        with self.connection:
            return self.cursor.execute("SELECT * FROM `subscriptions` WHERE `status` = ?", (status,)).fetchall()

    def subscriber_exists(self, user_id):
        with self.connection:
            result = self.cursor.execute('SELECT * FROM `subscriptions` WHERE `user_id` = ?', (user_id,)).fetchall()
            return bool(len(result))

    def add_subscriber(self, user_id, status=True):
        with self.connection:
            return self.cursor.execute("INSERT INTO `subscriptions` (`user_id`, `status`) VALUES(?,?)", (user_id, status))

    def update_subscription(self, user_id, status):
        with self.connection:
            return self.cursor.execute("UPDATE `subscriptions` SET `status` = ? WHERE `user_id` = ?", (status, user_id))

    def update_cryptocurrency_subscription(self, user_id, text, status):
        with self.connection:
            if text == 'bitcoin':
                return self.cursor.execute("UPDATE `subscriptions` SET `bitcoin` = ? WHERE `user_id` = ?", (status, user_id))
            if text == 'xrp':
                return self.cursor.execute("UPDATE `subscriptions` SET `xrp` = ? WHERE `user_id` = ?", (status, user_id))
            if text == 'ethereum':
                return self.cursor.execute("UPDATE `subscriptions` SET `ethereum` = ? WHERE `user_id` = ?", (status, user_id))
            if text == 'cardano':
                return self.cursor.execute("UPDATE `subscriptions` SET `cardano` = ? WHERE `user_id` = ?", (status, user_id))
            if text == 'tether':
                return self.cursor.execute("UPDATE `subscriptions` SET `tether` = ? WHERE `user_id` = ?", (status, user_id))

    def is_subscribed(self, user_id, text):
        with self.connection:
            result = []
            if text == 'bitcoin':
                result = self.cursor.execute('SELECT * FROM `subscriptions` WHERE `user_id` = ? AND `bitcoin` = 1', (user_id,)).fetchall()
            if text == 'xrp':
                result = self.cursor.execute('SELECT * FROM `subscriptions` WHERE `user_id` = ? AND `xrp` = 1', (user_id,)).fetchall()
            if text == 'ethereum':
                result = self.cursor.execute('SELECT * FROM `subscriptions` WHERE `user_id` = ? AND `ethereum` = 1', (user_id,)).fetchall()
            if text == 'cardano':
                result = self.cursor.execute('SELECT * FROM `subscriptions` WHERE `user_id` = ? AND `cardano` = 1', (user_id,)).fetchall()
            if text == 'tether':
                result = self.cursor.execute('SELECT * FROM `subscriptions` WHERE `user_id` = ? AND `tether` = 1', (user_id,)).fetchall()
            return bool(len(result))

    def close(self):
        """Закрываем соединение с БД"""
        self.connection.close()
