import unittest
import requests


class TestCase(unittest.TestCase):
	def setUp(self):
		self.url = 'http://localhost:5000/api/0.1/importMembers'

	def test(self):
		payload = {
			'original': open('MemberBatchSearch.xlsx', 'rb')
		}
		response = requests.post(self.url, files=payload)
		print(response.text)


if __name__ == '__main__':
	suite = unittest.TestSuite()
	suite.addTest(TestCase('test'))

	runner = unittest.TextTestRunner()
	runner.run(suite)
