import unittest
import requests
import random


class TestCase(unittest.TestCase):
	def setUp(self):
		self.base = 'http://sit.devqp.info/api/0.1/'
		self.data = [{
			'username': 'twilight',
			'password': 'twilight',
			'parentUsername': 'root',
			'rebateRate': 20,
			'name': 'Twilight Sparkle',
			'phone': random.randint(13800000000, 13899999999),
			'email': 'TwilightSparkle@ponyville.net',
		}, {
			'username': 'pinkie',
			'password': 'pinkie',
			'parentUsername': 'root',
			'rebateRate': 20,
			'name': 'Pinkie Pie',
			'phone': random.randint(13900000000, 13999999999),
			'email': 'PinkiePie@ponyville.net',
		}, {
			'username': 'apple',
			'password': 'apple',
			'parentUsername': 'celestia',
			'rebateRate': 20,
			'name': 'Apple Jack',
			'phone': random.randint(15800000000, 15899999999),
			'email': 'AppleJack@ponyville.net',
		}, {
			'username': 'rainbow',
			'password': 'rainbow',
			'parentUsername': 'celestia',
			'rebateRate': 20,
			'name': 'Rainbow Dash',
			'phone': random.randint(13600000000, 13699999999),
			'email': 'RainbowDash@ponyville.net',
		}, {
			'username': 'celestia',
			'password': 'celestia',
			'parentUsername': 'root',
			'rebateRate': 20,
			'commissionConfig': 1,
			'defaultRebateConfig': 1,
			'defaultLevelConfig': 1,
			'name': 'Princess Celestia',
			'phone': random.randint(15500000000, 15599999999),
			'email': 'PrincessCelestia@ponyville.net',
		}, {
			'username': 'luna',
			'password': 'luna',
			'parentUsername': 'celestia',
			'rebateRate': 20,
			'commissionConfig': 1,
			'defaultRebateConfig': 1,
			'defaultLevelConfig': 1,
			'name': 'Princess Luna',
			'phone': random.randint(15500000000, 15599999999),
			'email': 'PrincessLuna@ponyville.net',
		}, {
			'username': 'cadenza',
			'password': 'cadenza',
			'parentUsername': 'celestia',
			'rebateRate': 20,
			'commissionConfig': 1,
			'defaultRebateConfig': 1,
			'defaultLevelConfig': 1,
			'name': 'Mi Amore Cadenza',
			'phone': random.randint(15500000000, 15599999999),
			'email': 'MiAmoreCadenza@ponyville.net',
		}]

	def get_member_id(self, username):
		response = requests.get(self.base + 'members?username=' + username)
		return response.json()['data'][0]['id']

	def test_create_member(self):
		response = requests.post(self.base + 'members', json=self.data[1])
		print(response.text)
		response = requests.post(self.base + 'members', json=self.data[2])
		print(response.text)
		response = requests.post(self.base + 'members', json=self.data[3])
		print(response.text)

	def test_create_agent(self):
		response = requests.post(self.base + 'agents', json=self.data[4])
		print(response.text)
		response = requests.post(self.base + 'agents', json=self.data[5])
		print(response.text)
		response = requests.post(self.base + 'agents', json=self.data[6])
		print(response.text)

	def test_update_member(self):
		payload = {
			'memberId': [
				str(get_member_id('twilight')),
				str(get_member_id('pinkie')),
			],
			'status': 0
		}
		response = requests.put(self.base + 'members', json=payload)
		print(response.text)


if __name__ == '__main__':
	suite = unittest.TestSuite()
	suite.addTest(TestCase('test_create_member'))
	suite.addTest(TestCase('test_create_agent'))
	suite.addTest(TestCase('test_update_member'))

	runner = unittest.TextTestRunner()
	runner.run(suite)
