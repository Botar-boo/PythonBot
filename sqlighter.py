import psycopg2

import config

# Класс, в котором будем работать с БД
class SQLighter:


    def __init__(self):
        # Устанавливаем connection с созданной new_db
        self.connection = psycopg2.connect(
                                  host=config.HOST,
                                  dbname=config.DB_NAME,
                                  user=config.USER_NAME,
                                  password=config.PASSWORD)
        self.cursor = self.connection.cursor()

    # Собираем лист всех подписчиков
    def create_table(self):
        with self.connection:
            self.cursor.execute(
                "CREATE TABLE subscriptions (id integer,"
                "user_id integer,"
                "status boolean,"
                "bitcoin boolean,"
                "xrp boolean,"
                "ethereum boolean,"
                "cardano boolean,"
                "tether boolean);")

    def get_subscriptions(self, status=True):
        with self.connection:
            self.cursor.execute(
                "SELECT * FROM subscriptions WHERE status = {}".format(status))
            return self.cursor.fetchall()

    # Проверяем, подписан ли пользователь
    def subscriber_exists(self, user_id):
        with self.connection:
            self.cursor.execute(
                'SELECT * FROM subscriptions WHERE user_id = {}'.format(user_id))
            result = self.cursor.fetchall()
            return bool(len(result))

    # Добавляем пользователя в БД
    def add_subscriber(self, user_id, status=True):
        with self.connection:
            return self.cursor.execute(
                "INSERT INTO subscriptions (user_id, status) VALUES({},{})".format(user_id, status))

    # Обновляем статус подписки
    def update_subscription(self, user_id, status):
        with self.connection:
            return self.cursor.execute(
                "UPDATE subscriptions SET status = {} WHERE user_id = {}".format(status, user_id))

    # Обновляем статус подписки на валюту
    def update_cryptocurrency_subscription(self, user_id, text, status):
        with self.connection:
            return self.cursor.execute(
                "UPDATE subscriptions SET {} = {} WHERE user_id = {}".format(text, bool(status), user_id,))

    # Проверяем наличие подписки на валюту
    def is_subscribed(self, user_id, text):
        with self.connection:
            result = []
            self.cursor.execute(
                'SELECT * FROM subscriptions WHERE user_id = {} AND {} = TRUE'.format(user_id, text,))
            result = self.cursor.fetchall()
            return bool(len(result))

    # Закрываем соединение с БД
    def close(self):
        self.connection.close()
