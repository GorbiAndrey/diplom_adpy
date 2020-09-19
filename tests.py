import unittest
import vkinder as app
from unittest.mock import patch


class Testmain(unittest.TestCase):
    token = '958eb5d439726565e9333aa30e50e0f937ee432e927f0dbd541c541887d919a7c56f95c04217915c32008'
    user = app.User(360847139)

    def test_get_list_top10_users(self):
        user_input = ["geter", "30", "35"]
        with patch('builtins.input', side_effect=user_input):
            list_top10_users = self.user.get_list_top10_users()
            self.assertIsInstance(list_top10_users, list)
            self.assertLessEqual(len(list_top10_users), 10)
            for user in list_top10_users:
                self.assertLessEqual(len(user['photos_top3']), 3)
                self.assertEqual(len(set(list(user.keys())).difference(
                    {"id", "weight", "photos_top3"})), 0)


if __name__ == '__main__':
    unittest.main()
