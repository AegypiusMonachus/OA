import unittest
import requests


class TestCase(unittest.TestCase):
	def setUp(self):
		self.base = 'http://localhost:5000/api/0.1/memberWithdrawals'
		self.data = [{
			'username': 'twilight',
			'amount': '100',
		}, {
			'username': 'pinkie',
			'amount': '100',
		}, {
			'username': 'apple',
			'amount': '100',
		}]

	def test_member_withdrawal(self):
		response = requests.post(self.base, json=self.data[0])
		print(response.text)


if __name__ == '__main__':
	suite = unittest.TestSuite()
	suite.addTest(TestCase('test_member_withdrawal'))

	runner = unittest.TextTestRunner()
	runner.run(suite)
