import unittest
import requests


class TestCase(unittest.TestCase):
	def setUp(self):
		self.url = 'http://localhost:5000/api/0.1/memberBatchCreateLogs'

	def test(self):
		payload = {
			'original': open('/home/yc/桌面/ImportMemberCreateTemplate.xlsx', 'rb')
		}
		response = requests.post(self.url, files=payload)
		print(response.text)


if __name__ == '__main__':
	suite = unittest.TestSuite()
	suite.addTest(TestCase('test'))

	runner = unittest.TextTestRunner()
	runner.run(suite)
