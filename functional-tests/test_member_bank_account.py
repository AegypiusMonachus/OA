import unittest
import requests
import random


def get_member_id(username):
	response = requests.get('http://localhost:5000/api/0.1/members?username=' + username)
	return response.json()['data'][0]['id']


class TestCase(unittest.TestCase):
	def setUp(self):
		self.base = 'http://localhost:5000/api/0.1/memberBankAccounts'
		self.data = [{
			'memberId': get_member_id('twilight'),
			'bankId': 1,
			'accountNumber': str(random.randint(0000, 9999)) + ' ' + str(random.randint(0000, 9999)),
			'accountName': 'Twilight Sparkle',
			'subbranchName': 'Subbranch of ICBC',
			'province': 'BeiJing',
			'city': 'BeiJing',
		}, {
			'memberId': get_member_id('pinkie'),
			'bankId': 1,
			'accountNumber': str(random.randint(0000, 9999)) + ' ' + str(random.randint(0000, 9999)),
			'accountName': 'Pinkie Pie',
			'subbranchName': 'Subbranch of ICBC',
			'province': 'GuangDong',
			'city': 'GuangZhou',
		}, {
			'memberId': get_member_id('apple'),
			'bankId': 6,
			'accountNumber': str(random.randint(0000, 9999)) + ' ' + str(random.randint(0000, 9999)),
			'accountName': 'Apple Jack',
			'subbranchName': 'Subbranch of CCB',
			'province': 'ChengDu',
			'city': 'ChengDu',
		}]

	def test_create_member_bank_account(self):
		response = requests.post(self.base, json=self.data[2])
		print(response.text)


if __name__ == '__main__':
	suite = unittest.TestSuite()
	suite.addTest(TestCase('test_create_member_bank_account'))

	runner = unittest.TextTestRunner()
	runner.run(suite)
