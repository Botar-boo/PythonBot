import unittest

from random import randrange
from sqlighter import SQLighter

import crypto


class TestBot(unittest.TestCase):

    def test_get_request(self):  # проверка подключения к сайту
        cr = crypto.Crypto()
        self.assertEqual(cr.response.ok, True)

    def test_check_sub(self):  # проверка работы подписки
        user_id = randrange(100000)
        db = SQLighter()
        db.add_subscriber(user_id)
        self.assertEqual(db.subscriber_exists(user_id), True)
