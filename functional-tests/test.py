import unittest
import requests


class TestCase(unittest.TestCase):
	def setUp(self):
		self.base = 'http://sit.devqp.info/api/0.1/links'

	def test(self):
		payload = {
			'memberId': '272, 453',
			'enable': 1
		}
		response = requests.put(self.base, json=payload)
		print(response.text)


if __name__ == '__main__':
	suite = unittest.TestSuite()
	suite.addTest(TestCase('test'))

	runner = unittest.TextTestRunner()
	runner.run(suite)
