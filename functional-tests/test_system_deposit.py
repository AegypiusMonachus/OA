import unittest
import requests


class TestCase(unittest.TestCase):
	def setUp(self):
		self.base = 'http://localhost:5000/api/0.1/systemDeposits'
		self.data = [{
			'username': 'twilight',
			'amount': 300,
		}, {
			'username': 'pinkie',
			'amount': 900,
		}, {
			'username': 'apple',
			'amount': 600,
		}]

	def test_system_deposit(self):
		response = requests.post(self.base, json=self.data[0])
		print(response.text)


if __name__ == '__main__':
	suite = unittest.TestSuite()
	suite.addTest(TestCase('test_system_deposit'))

	runner = unittest.TextTestRunner()
	runner.run(suite)
