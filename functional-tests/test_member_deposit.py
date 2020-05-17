import unittest
import requests


class TestCase(unittest.TestCase):
	def setUp(self):
		self.base = 'http://localhost:5000/api/0.1/'
		self.data = [{
			'username': 'twilight',
			'amount': 1000,
			'systemBankAccountId': 5,
		}, {
			'username': 'pinkie',
			'amount': 1000,
			'systemBankAccountId': 6,
		}, {
			'username': 'apple',
			'amount': 1000,
			'systemBankAccountId': 7,
		}]

	def test_member_deposit(self):
		response = requests.post(self.base + 'memberDeposits', json=self.data[2])
		print(response.text)


if __name__ == '__main__':
	suite = unittest.TestSuite()
	suite.addTest(TestCase('test_member_deposit'))

	runner = unittest.TextTestRunner()
	runner.run(suite)
