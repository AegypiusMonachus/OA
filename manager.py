import os
import time
from app import create_app
app = create_app(os.getenv('KRAKEN_CONFIG_NAME', default='TESTING'))


if __name__ == '__main__':
	from flask_script import Manager, Server
	manager = Manager(app)

	# from app.schedule import scheduler
	# scheduler.init_app(app)  # 定时任务
	# scheduler.start()

	# 	manager.add_command("runserver", Server(use_debugger=False))
	@manager.shell
	def _make_context():
		from app.models import db
		return dict(app=app)

	@manager.command
	def test():
		import unittest
		loader = unittest.TestLoader()
		runner = unittest.TextTestRunner()

	'''
	@manager.option('-h', '--host', dest='host', default=None)
	@manager.option('-p', '--port', dest='port', default=None)
	def runserver(host, port):
		from app.extensions import socketio
		socketio.run(app, host=host, port=port)
	'''

	@manager.command
	def create_default_member():
		from app.models import db
		from app.models.member import Member
		member = Member()
		member.type =9
		member.username = 'root'
		member.password = 'root'
		try:
			db.session.add(member)
			db.session.commit()
		except:
			db.session.rollback()
			db.session.remove()

	@manager.command
	def create_default_user():
		from app.models import db
		from app.models.user import User
		user = User()
		user.username = 'default'
		user.password = 'default'
		try:
			db.session.add(user)
			db.session.commit()
		except:
			db.session.rollback()
			db.session.remove()

	@manager.command
	def create_menu():
		from app.models import db
		from app.models.user import Menu

		try:
			parent = Menu(name='首页')
			db.session.add(parent)
			db.session.commit()
		except:
			db.session.rollback()
			db.session.remove()

		try:
			parent = Menu(name='会员与代理')
			db.session.add(parent)
			db.session.commit()

			names = ['会员查询', '会员创建', '会员汇入', '代理查询', '代理创建', '代理审核']
			for name in names:
				db.session.add(Menu(name=name, parent=parent.id))
			db.session.commit()
		except:
			db.session.rollback()
			db.session.remove()

		try:
			parent = Menu(name='财务管理')
			db.session.add(parent)
			db.session.commit()

			names = ['公司入款审核', '线上支付看板', '取款申请审核', '交易记录查询', '返水计算', '佣金计算', '优惠汇入', '存取款汇出']
			for name in names:
				db.session.add(Menu(name=name, parent=parent.id))
			db.session.commit()
		except:
			db.session.rollback()
			db.session.remove()

		try:
			parent = Menu(name='系统管理')
			db.session.add(parent)
			db.session.commit()

			names = [
				'会员等级管理', '公司入款账户管理', '线上支付商户管理',
				'会员端设定', '返水设定', '佣金设定', '娱乐城管理', '站内信',
				'前台管理', '优惠管理', '子账号管理', '站台系统值设置', '国别阻挡管理',
			]
			for name in names:
				db.session.add(Menu(name=name, parent=parent.id))
			db.session.commit()
		except:
			db.session.rollback()
			db.session.remove()

		try:
			parent = Menu(name='彩票记录')
			db.session.add(parent)
			db.session.commit()

			names = [
				'彩票投注记录', '六合投注记录', '彩票开奖结果', '系统彩开奖结果',
				'彩票管理', '彩票玩法大类设置', '彩票赔率设置', '六合赔率设置',
			]
			for name in names:
				db.session.add(Menu(name=name, parent=parent.id))
			db.session.commit()
		except:
			db.session.rollback()
			db.session.remove()

		try:
			parent = Menu(name='各式报表')
			db.session.add(parent)
			db.session.commit()

			names = ['统计报表', '投注记录查询', '历史投注记录查询', '登入记录查询']
			for name in names:
				db.session.add(Menu(name=name, parent=parent.id))
			db.session.commit()
		except:
			db.session.rollback()
			db.session.remove()

		try:
			parent = Menu(name='个人信息')
			db.session.add(parent)
			db.session.commit()

			names = ['变更密码', '变更手机号', '变更电子邮箱']
			for name in names:
				db.session.add(Menu(name=name, parent=parent.id))
			db.session.commit()
		except:
			db.session.rollback()
			db.session.remove()

	manager.run()
