import shutil
import sqlite3


# Класс, в котором будем работать с БД
class SQLighter:

    def __init__(self, database):
        # Устанавливаем connection с созданной new_db
        self.connection = sqlite3.connect(database)
        shutil.copyfile("db.db", "new_db.db")
        self.cursor = self.connection.cursor()

    # Собираем лист всех подписчиков
    def get_subscriptions(self, status=True):
        with self.connection:
            return self.cursor.execute("SELECT * FROM `subscriptions` WHERE `status` = {}".format(status)).fetchall()

    # Проверяем, подписан ли пользователь
    def subscriber_exists(self, user_id):
        with self.connection:
            result = self.cursor.execute('SELECT * FROM `subscriptions` WHERE `user_id` = {}'.format(user_id)).fetchall()
            return bool(len(result))

    # Добавляем пользователя в БД
    def add_subscriber(self, user_id, status=True):
        with self.connection:
            return self.cursor.execute(
                "INSERT INTO `subscriptions` (`user_id`, `status`) VALUES({},{})".format(user_id, status))

    # Обновляем статус подписки
    def update_subscription(self, user_id, status):
        with self.connection:
            return self.cursor.execute(
                "UPDATE `subscriptions` SET `status` = {} WHERE `user_id` = {}".format(status, user_id))

    # Обновляем статус подписки на валюту
    def update_cryptocurrency_subscription(self, user_id, text, status):
        with self.connection:
            return self.cursor.execute(
                "UPDATE `subscriptions` SET `{}` = {} WHERE `user_id` = {}".format(text, status, user_id,))

    # Проверяем наличие подписки на валюту
    def is_subscribed(self, user_id, text):
        with self.connection:
            result = []
            result = self.cursor.execute(
                'SELECT * FROM `subscriptions` WHERE `user_id` = {} AND `{}` = 1'.format(user_id, text,)).fetchall()
            return bool(len(result))

    # Закрываем соединение с БД
    def close(self):
        self.connection.close()
