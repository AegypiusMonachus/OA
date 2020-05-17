import time

from flask import request, current_app
from flask.views import MethodView
from flask.json import jsonify


class Upload(MethodView):
	from app.auth.common import token_auth
	decorators = [token_auth.login_required]

	def post(self):
		import os
		path = os.path.abspath(current_app.config['STATIC_FOLDER'])

		response = []
		for key in request.files.keys():
			storage = request.files.get(key)

			import hashlib
			filename = hashlib.md5(storage.read()).hexdigest() + os.path.splitext(storage.filename)[1]
			try:
				storage.stream.seek(0)
				storage.save(os.path.join(path, filename))

				response.append({
					'originalFilename': storage.filename,
					'filename': filename
				})
			except:
				pass
		return jsonify(response), 201


from app.models.user import User
from app.models.message import (
	Notice,
	Discount,
	Carousel
)


def get_default_token():
	user = User.query.filter(User.username == 'default').first()
	return User.generate_token(user)


class GuestNotices(MethodView):
	def get(self):
		mobile = request.args.get('mobile')
		token = get_default_token()

		criterion = set()
		criterion.add(Notice.status == 1)

		if mobile == 'true':
			criterion.add(Notice.device == 1)
		else:
			criterion.add(Notice.device == 0)

		notices = Notice.query.filter(*criterion).order_by(Notice.sort).all()
		result = []
		for notice in notices:
			timeArray = time.localtime(notice.updateTime)
			result.append({
				'title': notice.title,
				'content': notice.content,
				'updateTime' :time.strftime("%Y-%m-%d", timeArray),
				'formember':notice.forMember
			})
		return jsonify(result)


class GuestDiscounts(MethodView):
	def get(self):
		mobile = request.args.get('mobile')
		token = get_default_token()

		criterion = set()
		criterion.add(Discount.status == 1)

		if mobile == 'true':
			criterion.add(Discount.device == 1)
		else:
			criterion.add(Discount.device == 1)

		discounts = Discount.query.filter(*criterion).order_by(Discount.sort).all()
		result = []
		for discount in discounts:
			result.append({
				'title': discount.title,
				'content': discount.content,
				'type': discount.type,
				'bannerAddress': discount.bannerAddress + '?token=' + token if discount.bannerAddress else None
			})
		return jsonify(result)


class GuestCarousels(MethodView):
	def get(self):
		mobile = request.args.get('mobile')
		token = get_default_token()

		criterion = set()

		if mobile == 'true':
			criterion.add(Carousel.device == 1)
		else:
			criterion.add(Carousel.device == 0)

		carousels = Carousel.query.filter(*criterion).all()
		result = []
		for carousel in carousels:
			result.append({
				'address': carousel.address + '?token=' + token,
				'url': carousel.url
			})
		return jsonify(result)


'''
class Touch(MethodView):
	def get(self):
		import random
		element = random.choice([{
			'orderId': random.randint(900, 999),
			'orderType': 100001,
		}, {
			'orderId': random.randint(900, 999),
			'orderType': 100002,
		}, {
			'orderId': random.randint(900, 999),
			'orderType': 200001,
		}])

		from app.extensions import queue
		queue.put(element)
		return jsonify(element)


class WebSocketDemo(MethodView):
	def get(self):
		from flask import render_template
		return render_template('demo.html')
'''
