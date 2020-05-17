import unittest
import requests


class TestCase(unittest.TestCase):
	def setUp(self):
		self.base = 'http://localhost:5000/api/auth/'

	def test_can_get_token_of_user(self):
		payload = {
			'username': 'default',
			'password': 'default',
		}
		response = requests.post(self.base + 'userLogin', json=payload)
		self.assertIsNotNone(response.json()['token'])
		print(response.text)

	def test_can_get_token_of_member(self):
		import hashlib
		payload = {
			'username': 'twilight',
			'password': hashlib.md5('twilight'.encode()).hexdigest()
		}
		response = requests.post(self.base + 'memberLogin', json=payload)
		self.assertIsNotNone(response.json()['token'])
		print(response.text)

	def test_can_not_logout_without_token(self):
		response = requests.get(self.base + 'userLogout')
		print(response.text)

	def test_can_logout_with_token(self):
		payload = {
			'username': 'default',
			'password': 'default',
		}
		response = requests.post(self.base + 'userLogin', json=payload)
		token = response.json()['token']

		headers = {
			'Authorization': 'Bearer ' + token
		}
		response = requests.get(self.base + 'userLogout', headers=headers)
		print(response.text)


if __name__ == '__main__':
	suite = unittest.TestSuite()
	suite.addTest(TestCase('test_can_get_token_of_user'))
	suite.addTest(TestCase('test_can_get_token_of_member'))
	suite.addTest(TestCase('test_can_not_logout_without_token'))
	suite.addTest(TestCase('test_can_logout_with_token'))

	runner = unittest.TextTestRunner()
	runner.run(suite)
