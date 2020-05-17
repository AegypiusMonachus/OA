from flask import request
from flask_restful import Resource, marshal_with, fields, abort
from flask_restful.reqparse import RequestParser
from sqlalchemy import or_
from werkzeug.datastructures import FileStorage

from app.models import db
from app.models.common.utils import *
from app.models.member_level import MemberLevel
from app.models.message import MessageInbox, MessageOutbox, Notice,Websites, DiscountType, Discount, Carousel, MemberRegistrationMessage,NoticeSet, \
	SenderShow
from app.models.member import Member, MemberPersonalInfo
from app.models.user import User
from app.common.utils import *
from ..common import *
from ..common.utils import *
import json
from sqlalchemy import distinct
from datetime import datetime
from sqlalchemy import and_
# 会员发件
class Messages(Resource):
	def post(self):
		parser = RequestParser(trim=True)
		parser.add_argument('title', type=str, required=True)
		parser.add_argument('content', type=str, required=True)
		parser.add_argument('sendername', type=str, required=True)
		parser.add_argument('receivername', type=str, required=True)
		args = parser.parse_args(strict=True)

		sender = Member.query.filter(Member.username == args['sendername']).first()
		if not sender:
			abort(400)

		receivers = Member.query.filter(Member.id == sender.parent).first()
		if not receivers:
			return make_response(error_message='该人员不存在，请重新发件')
		message = MessageInbox()
		message.title = args['title']
		message.content = args['content']
		message.receivername = receivers.username
		message.senderid = sender.id
		message.sendername = sender.username
		message.time = time_to_value()
		try:
			db.session.add(message)
			db.session.commit()
		except:
			db.session.rollback()
			db.session.remove()
		return {'success': True, "message": '发送成功'}
# 后台收到会员信件
class MessagesInbox(Resource):

	@marshal_with(make_marshal_fields({
		'id': fields.Integer,
		'sendername': fields.String,
		'senderid': fields.Integer,
		'time': fields.Integer,
		'title': fields.String,
		'content': fields.String,
		'read':fields.Integer
	}))
	def get(self):
		parser = RequestParser(trim=True)
		parser.add_argument('page', type=int, default=DEFAULT_PAGE)
		parser.add_argument('pageSize', type=int, default=DEFAULT_PAGE_SIZE)
		parser.add_argument('sendername', type=str)
		parser.add_argument('titleLike', type=str)
		parser.add_argument('contentLike', type=str)
		parser.add_argument('timeLower', type=int)
		parser.add_argument('timeUpper', type=int)
		parser.add_argument('read', type=int)
		parser.add_argument('id', type=int)
		parser.add_argument('senderid', type=int)
		args = parser.parse_args(strict=True)

		criterion = set()
		criterion.add(MessageInbox.receiverid == 0)
		if args['sendername']:
			criterion.add(MessageInbox.sendername.in_(args['sendername'].split(',')))
		if args['titleLike']:
			criterion.add(MessageInbox.title.like("%{}%".format(args['titleLike'])))
		if args['contentLike']:
			criterion.add(MessageInbox.content.like("%{}%".format(args['contentLike'])))
		if args['timeLower']:
			criterion.add(MessageInbox.time >= args['timeLower'])
		if args['timeUpper']:
			criterion.add(MessageInbox.time <= args['timeUpper'] + SECONDS_PER_DAY)
		if args['read'] == 0 or args['read'] == 1:
			criterion.add(MessageInbox.read == args['read'])
		query = db.session.query(
			MessageInbox.sendername,
			MessageInbox.time,
			MessageInbox.title,
			MessageInbox.content,
			MessageInbox.id,
			MessageInbox.senderid,
			MessageInbox.read,
			MessageInbox.receiverid	).order_by(MessageInbox.time.desc())
		pagination = paginate(query, criterion, args['page'], args['pageSize'])
		pagination = convert_pagination(pagination)
		return make_response_from_pagination(pagination)

	def put(self):
		parser = RequestParser(trim=True)
		parser.add_argument('read', type=int)
		parser.add_argument('id', type=str)
		args = parser.parse_args()
		try:
			data = args['id'].split(',')
			for i in data:
				mem = db.session.query(MessageInbox).get(int(i))
				mem.read = args['read']
				db.session.add(mem)
			db.session.commit()
			return {'success': True}
		except:
			db.session.rollback()
			db.session.remove()

	def delete(self):
		parser = RequestParser(trim=True)
		parser.add_argument('id', type=str)
		args = parser.parse_args(strict=True)
		try:
			for id in args['id'].split(','):
				temp = MessageInbox.query.get(int(id))
				db.session.delete(temp)
			db.session.commit()
		except:
			db.session.rollback()
			db.session.remove()
		return {"success":True}
#后台回复会员信件
class MessagesOutbox(Resource):
	@marshal_with(make_marshal_fields({
		'id': fields.Integer,
		'senderName':fields.String,
		'time': fields.Integer,
		'title': fields.String,
		'content': fields.String,
		'countMember':fields.Integer
	}))
	def get(self):
		parser = RequestParser(trim=True)
		parser.add_argument('page', type=int, default=DEFAULT_PAGE)
		parser.add_argument('pageSize', type=int, default=DEFAULT_PAGE_SIZE)
		parser.add_argument('sendername', type=str)
		parser.add_argument('receivername', type=str)
		parser.add_argument('titleLike', type=str)
		parser.add_argument('contentLike', type=str)
		parser.add_argument('timeLower', type=int)
		parser.add_argument('timeUpper', type=int)
		args = parser.parse_args(strict=True)

		criterion = set()
		if args['sendername']:
			criterion.add(SenderShow.senderName.in_(args['sendername'].split(',')))
		if args['receivername']:
			a = args["receivername"].split(',')
			b = []
			for i in a:
				c = '%{}%'.format(i)
				b.append(c)
			criterion.add(or_(*[SenderShow.receiveAllName.like(w) for w in b]))
		if args['titleLike']:
			criterion.add(SenderShow.title.like("%{}%".format(args['titleLike'])))
		if args['contentLike']:
			criterion.add(SenderShow.content.like("%{}%".format(args['contentLike'])))
		if args['timeLower']:
			criterion.add(SenderShow.time >= args['timeLower'])
		if args['timeUpper']:
			criterion.add(SenderShow.time <= args['timeUpper'] + SECONDS_PER_DAY)

		pagination = paginate(SenderShow.query.order_by(SenderShow.time.desc()), criterion, args['page'], args['pageSize'])
		return make_response_from_pagination(pagination)

	def post(self):
		parser = RequestParser(trim=True)
		parser.add_argument('title', type=str, required=True)
		parser.add_argument('content', type=str, required=True)
		parser.add_argument('sendername', type=str, required=True)
		parser.add_argument('receivername', type=str, required=True)
		args = parser.parse_args(strict=True)
		try:
			sender = User.query.filter(User.username == args['sendername']).first()
			if not sender:
				abort(500)
			if args['receivername'] is not None:
				nameall = args['receivername'].split(",")
			else:
				return {"errorMsg": "收件人不能为空"}
			truename = []
			for i in nameall:
				if i is not "":
					truename.append(i)
			count=len(truename)
			receivers = db.session.query(Member.username).filter(Member.type==0).all()
			for name in truename:
				name = (name,)
				if name not in receivers:
					return {"errorMsg": "您输入的收件人中有非会员，请检查重新输入"}


			sendershow = SenderShow()
			if args['title'] is not None:
				sendershow.title = args['title']
			else:
				return {"errorMsg": "信件标题不能为空"}
			sendershow.senderName = args['sendername']
			if args['content'] is not None:
				sendershow.content = args['content']
			else:
				return {"errorMsg": "信件内容不能为空"}
			sendershow.time = time_to_value()
			sendershow.countMember = count
			sendershow.receiveAllName = args['receivername']

			db.session.add(sendershow)
			# db.session.commit()
			db.session.flush()

			members = Member.query.filter(Member.username.in_(args['receivername'].split(','))).all()
			for member in members:
				message = MessageOutbox()
				message.receivername = member.username
				message.receiverid = member.id
				message.title = args['title']
				message.content = args['content']
				message.sendername = sender.username
				message.time = time_to_value()
				message.senderShowid = sendershow.id
				db.session.add(message)
			db.session.commit()
			return {"success": True, "message": "发信成功"}
		except:
			db.session.rollback()
			db.session.remove()
			return {"success":True,"errorMsg":"发信失败"}

	def delete(self):
		parser = RequestParser(trim=True)
		parser.add_argument('id', type=str)
		args = parser.parse_args(strict=True)
		try:
			for id in args['id'].split(','):
				temp = SenderShow.query.get(id)
				db.session.delete(temp)
				db.session.commit()
				temp1 = MessageOutbox.query.filter(MessageOutbox.senderShowid == id).all()
				for i in temp1:
					temp2 = MessageOutbox.query.get(i.id)
					db.session.delete(temp2)
					db.session.commit()
		except:
			db.session.rollback()
			db.session.remove()
		return {"success":True}

# 获取用户等级
class GetMemLevel(Resource):
	@marshal_with(make_marshal_fields({
		'id': fields.Integer,
		'levelName': fields.String

	}))

	def get(self):
		query = db.session.query(
			MemberLevel.id,
			MemberLevel.levelName).all()
		result = []
		for i in query:
			data = {}
			data["id"] = i.id
			data['levelName'] = i.levelName
			result.append(data)

		return make_response(result)

#给全部会员发信，或者按照会员等级发信
class MessageAll(Resource):
	def post(self):
		data = request.get_json()
		# 获取请求数据中的data
		array = data['data']
		if 'id' in array:
			id = array['id']
			try:
				count = db.session.query(Member).filter(Member.isTsetPLay != 1, Member.type == 0,
														Member.levelConfig == id).count()
				allname = db.session.query(Member).filter(Member.type == 0,Member.isTsetPLay != 1,
														Member.levelConfig == id).all()
				sendershow = SenderShow()
				if 'title' in array:
					if array['title'] is not None:
						sendershow.title = array['title']
					else:
						return {"errorMsg": "信件标题不能为空"}
				if 'sendername' in array:
					sendershow.senderName = array['sendername']
				if 'content' in array:
					if array['content'] is not None:
						sendershow.content = array['content']
					else:
						return {"errorMsg": "信件内容不能为空"}

				sendershow.time = time_to_value()
				sendershow.countMember = count
				name = db.session.query(Member.username).filter(Member.type == 0, Member.isTsetPLay != 1,
														  Member.levelConfig == id).all()
				result = []
				for i in name:
					a = list(i)
					b = (' '.join(a))
					result.append(b)
				c = json.dumps(result)
				sendershow.receiveAllName = c

				db.session.add(sendershow)
				db.session.commit()

				for member in allname:
					message = MessageOutbox()
					message.receivername = member.username
					message.receiverid = member.id
					if 'title' in array:
						message.title = array['title']
					if 'content' in array:
						message.content = array['content']
					if 'sendername' in array:
						message.sendername = array["sendername"]
					message.time = time_to_value()
					message.senderShowid = sendershow.id
					db.session.add(message)
				db.session.commit()
				return {"success": True, "message": "发信成功"}
			except:
				db.session.rollback()
				db.session.remove()
				return {"success": False, "errorMsg": "发信失败"}

		else:
			try:
				if 'receivername' in array is not None:
					count = db.session.query(Member).filter(Member.isTsetPLay != 1, Member.type == 0).count()
					allname = db.session.query(Member).filter(Member.type == 0, Member.isTsetPLay != 1).all()
					sendershow = SenderShow()
					if 'title' in array:
						if array['title'] is not None:
							sendershow.title = array['title']
						else:
							return {"errorMsg": "信件标题不能为空"}
					if 'sendername' in array:
							sendershow.senderName = array['sendername']
					if 'content' in array:
						if array['content'] is not None:
							sendershow.content = array['content']
						else:
							return {"errorMsg": "信件内容不能为空"}

					sendershow.time = time_to_value()
					sendershow.countMember = count
					name = db.session.query(Member.username).filter(Member.type == 0, Member.isTsetPLay != 1).all()
					result = []
					for i in name:
						a = list(i)
						b = (' '.join(a))
						result.append(b)
					c = json.dumps(result)
					sendershow.receiveAllName = c

					db.session.add(sendershow)
					db.session.commit()

					for member in allname:
						message = MessageOutbox()
						message.receivername = member.username
						message.receiverid = member.id
						if 'title' in array:
							message.title = array['title']
						if 'content' in array:
							message.content = array['content']
						message.sendername = array['sendername']
						message.time = time_to_value()
						message.senderShowid = sendershow.id
						db.session.add(message)
					db.session.commit()
				return {"success": True, "message": "发信成功"}
			except:
				db.session.rollback()
				db.session.remove()
				return {"success": False, "errorMsg": "发信失败"}


# 根据countMember来查询对应的会员名称和会员ｉｄ
class MessageReceivers(Resource):
	@marshal_with(make_marshal_fields({
		'receiverid': fields.Integer,
		'receivername' : fields.String
	}))
	def get(self):
		parser = RequestParser(trim=True)
		parser.add_argument('id', type=int)
		args = parser.parse_args(strict=True)

		outboxs = MessageOutbox.query.filter(MessageOutbox.senderShowid == args['id']).all()
		return make_response(outboxs)


class Notices(Resource):
	@marshal_with(make_marshal_fields({
		'id': fields.Integer,
		'username': fields.String,
		'createTime': fields.Integer,
		'updateTime': fields.Integer,
		'title': fields.String,
		'content': fields.String,
		'status': fields.Integer,
		'sort': fields.Integer,
		'device': fields.Integer,
		'forMember': fields.Integer,
	}))

	def get(self):
		m_arg = Notice.query.with_entities(Notice.id, Notice.username, Notice.createTime, Notice.updateTime,
										   Notice.title, Notice.status, Notice.sort, Notice.device, Notice.forMember).all()
		result = []
		for mm_arg in m_arg:
			args = {}
			args["id"] = mm_arg.id
			args["username"] = mm_arg.username
			args["createTime"] = mm_arg.createTime
			args["updateTime"] = mm_arg.updateTime
			args["title"] = mm_arg.title
			args["status"] = mm_arg.status
			args["sort"] = mm_arg.sort
			args["device"] = mm_arg.device
			args["forMember"] = mm_arg.forMember
			result.append(args)
		m_args = json.dumps(result)
		arg = json.loads(m_args)
		return make_response(arg)


	def post(self):
		data = request.get_json()
		#获取请求数据中的data
		array = data['data']
		try:
			# 遍历请求数据
			for operation in array:
				# 获取请求数据中的data请求list
				m_dataArray = operation['data']
				device = operation['device']
				if device == 0:
					for data in m_dataArray:
						# 通过id判断是否有移动操作
						if 'id' in data:
							id = data['id']
							del data['id']
							args = {key: value for key, value in data.items() if value is not None}
							try:
								Notice.query.filter(Notice.id == id).update(args)
							except:
								db.session.rollback()
								db.session.remove()

						# 通过copy判断是否有复制操作
						else:
							if 'copy' in data:
								copy = data['copy']
								del data['copy']
								notice = Notice.query.filter(Notice.id == copy).first()
								m_args = {}
								m_args['sort'] = notice.sort
								m_args['title'] = notice.title
								m_args['device'] = notice.device
								m_args['device'] = 1
								m_args['status'] = notice.status
								m_args['updateTime'] = notice.updateTime
								m_args['forMember'] = notice.forMember
								m_args['createTime'] = notice.createTime
								m_args['content'] = notice.content
								m_args['username'] = notice.username
								m_res = Notice(**m_args)
								try:
									db.session.add(m_res)
								except:
									db.session.rollback()
									db.session.remove()


							# 没有id和copy就是新增操作
							elif 'id' and 'copy'  not in data:
								args = {key: value for key, value in data.items() if value is not None}
								notice = Notice(**args)
								try:
									db.session.add(notice)
								except:
									db.session.rollback()
									db.session.remove()

					# 删除公告操作
					if 'remove' in operation:
						remove = operation['remove']
						try:
							for id in remove:
								notice = Notice.query.filter(Notice.id == id).first()
								db.session.delete(notice)
						except:
							db.session.rollback()
							db.session.remove()
				else:
					for data in m_dataArray:
						# 通过id判断是否有移动操作
						if 'id' in data:
							id = data['id']
							del data['id']
							args = {key: value for key, value in data.items() if value is not None}
							try:
								Notice.query.filter(Notice.id == id).update(args)
							except:
								db.session.rollback()
								db.session.remove()

						# 通过copy判断是否有复制操作
						else:
							if 'copy' in data:
								copy = data['copy']
								del data['copy']
								notice = Notice.query.filter(Notice.id == copy).first()
								m_args = {}
								m_args['sort'] = notice.sort
								m_args['title'] = notice.title
								m_args['device'] = notice.device
								m_args['device'] = 0
								m_args['status'] = notice.status
								m_args['updateTime'] = notice.updateTime
								m_args['forMember'] = notice.forMember
								m_args['createTime'] = notice.createTime
								m_args['content'] = notice.content
								m_args['username'] = notice.username
								m_res = Notice(**m_args)
								try:
									db.session.add(m_res)
								except:
									db.session.rollback()
									db.session.remove()


							# 没有id和copy就是新增操作
							elif 'id' and 'copy' not in data:
								args = {key: value for key, value in data.items() if value is not None}
								notice = Notice(**args)
								try:
									db.session.add(notice)
								except:
									db.session.rollback()
									db.session.remove()

					# 删除公告操作
					if 'remove' in operation:
						remove = operation['remove']
						try:
							for id in remove:
								notice = Notice.query.filter(Notice.id == id).first()
								db.session.delete(notice)
								db.session.commit()
						except:
							db.session.rollback()
							db.session.remove()
			db.session.commit()
		except:
			db.session.rollback()
			db.session.remove()
		return {'success':True,'messages':'操作成功'}


class NoticesPut(Resource):
	@marshal_with(make_marshal_fields({
		'id': fields.Integer,
		'username': fields.String,
		'createTime': fields.Integer,
		'updateTime': fields.Integer,
		'title': fields.String,
		'content': fields.String,
		'status': fields.Integer,
		'sort': fields.Integer,
		'device': fields.Integer,
		'forMember': fields.Integer,
	}))

	def get(self, announcementid):
		m_arg = Notice.query.filter(Notice.id == announcementid).all()
		return make_response(m_arg)

	def put(self,announcementid):
		parser = RequestParser(trim=True)
		parser.add_argument('title', type=str)
		parser.add_argument('content', type=str)
		parser.add_argument('status', type=int)
		parser.add_argument('sort', type=int)
		parser.add_argument('device', type=int)
		parser.add_argument('forMember', type=int)
		parser.add_argument('updateTime', type=int)
		args = parser.parse_args(strict=True)
		args = {key: value for key, value in args.items() if value is not None}

		try:
			Notice.query.filter(Notice.id == announcementid).update(args)
			db.session.commit()
		except:
			db.session.rollback()
			db.session.remove()
		return make_response({'success':True})


class WebsiteAll(Resource):

	@marshal_with(make_marshal_fields({
		'id': fields.Integer,
		'webname': fields.String,
		'weburl':fields.String,
		'remark':fields.String
	}))
	def get(self):
		return make_response(Websites.query.all())

	def put(self, id):
		parser = RequestParser(trim=True)
		parser.add_argument('webname', type=str)
		parser.add_argument('weburl', type=str)
		parser.add_argument('remark', type=str)
		args = parser.parse_args(strict=True)
		args = {key: value for key, value in args.items() if value is not None}

		try:
			Websites.query.filter(Websites.id == id).update(args)
			db.session.commit()
		except:
			db.session.rollback()
			db.session.remove()
		return {'success':True}


class DiscountTypes(Resource):
	def get(self, websiteid):
		m_arg = DiscountType.query.filter(DiscountType.websiteid == websiteid).all()
		results = []
		for mm_arg in m_arg:
			result = []
			result_args = {}
			m_args = Discount.query.with_entities(Discount.id,Discount.sort,Discount.title,Discount.status,Discount.validTimeUpper,Discount.validTimeLower,Discount.device).filter(Discount.type == mm_arg.id).all()

			for mm_args in m_args:
				args = {}
				args["id"] = mm_args.id
				args["sort"] = mm_args.sort
				args["title"] = mm_args.title
				args["status"] = mm_args.status
				args["validTimeUpper"] = mm_args.validTimeUpper
				args["validTimeLower"] = mm_args.validTimeLower
				args["device"] = mm_args.device
				result.append(args)
			result = result
			result_args["promiselist"] = result
			result_args["id"] = mm_arg.id
			result_args["name"] = mm_arg.name
			result_args["websiteid"] = mm_arg.websiteid
			result_args["sort"] = mm_arg.sort
			results.append(result_args)
		results_s = json.dumps(results)
		results_s = json.loads(results_s)
		return make_response(results_s)

	def post(self, websiteid):
		parser = RequestParser(trim=True)
		parser.add_argument('name', type=str, required=True)
		parser.add_argument('sort', type=int, required=True)
		parser.add_argument('websiteid', type=int)
		args = parser.parse_args(strict=True)
		args = {key: value for key, value in args.items() if value is not None}
		try:
			db.session.add(DiscountType(**args))
			db.session.commit()
		except:
			db.session.rollback()
			db.session.remove()
			abort(500)
		return make_response([])

	def put(self, websiteid=None):
		data = request.get_json()
		m_args = data['data']
		try:
			for args in m_args:
				id = args['id']
				del args['id']
				try:
					DiscountType.query.filter(DiscountType.id == id).update(args)
				except:
					db.session.rollback()
					db.session.remove()
			db.session.commit()
		except:
			db.session.rollback()
			db.session.remove()
		return make_response({'success': True})

	def delete(self, websiteid,id):
		try:
			temp = DiscountType.query.get(id)
			if temp:
				db.session.delete(temp)
				db.session.commit()
			temp1 = Discount.query.filter(Discount.type == id).all()
			if temp1 is not None:
				db.session.delete(temp1)
				db.session.commit()
		except:
			db.session.rollback()
			db.session.remove()
		return {'success':True}

class Discounts(Resource):

	@marshal_with(make_marshal_fields({
		'id': fields.Integer,
		'title': fields.String,
		'content': fields.String,
		'type': fields.Integer,
		'sort': fields.Integer,
		'status': fields.Integer,
		'validTimeLower': fields.Integer,
		'validTimeUpper': fields.Integer,
		'bannerAddress': fields.String
	}))


	def get(self, discountid):
		m_arg = Discount.query.filter(Discount.id == discountid).all()
		return make_response(m_arg)


	def post(self,discountid):
		parser = RequestParser(trim=True)
		parser.add_argument('title', type=str, required=True)
		parser.add_argument('content', type=str, required=True)
		parser.add_argument('type', type=int)
		parser.add_argument('sort', type=int)
		parser.add_argument('status', type=int)
		parser.add_argument('validTimeLower', type=int)
		parser.add_argument('validTimeUpper', type=int)
		parser.add_argument('forPC', type=int)
		parser.add_argument('forMobile', type=int)
		parser.add_argument('bannerAddress', type=str)
		args = parser.parse_args(strict=True)
		args = {key: value for key, value in args.items() if value is not None}

		try:
			db.session.add(Discount(**args))
			db.session.commit()
		except:
			db.session.rollback()
			db.session.remove()
			abort(500)
		return make_response([])

	def put(self, discountid):
		parser = RequestParser(trim=True)
		parser.add_argument('title', type=str)
		parser.add_argument('content', type=str)
		parser.add_argument('type', type=int)
		parser.add_argument('sort', type=int)
		parser.add_argument('status', type=int)
		parser.add_argument('validTimeLower', type=int)
		parser.add_argument('validTimeUpper', type=int)
		parser.add_argument('forPC', type=int)
		parser.add_argument('forMobile', type=int)
		parser.add_argument('bannerAddress', type=str)
		args = parser.parse_args(strict=True)
		args = {key: value for key, value in args.items() if value is not None}
		try:
			Discount.query.filter(Discount.id == discountid).update(args)
			db.session.commit()
		except:
			db.session.rollback()
			db.session.remove()
			abort(500)
		return make_response([])

	def delete(self):
		parser = RequestParser(trim=True)
		parser.add_argument('id', type=str, required=True)
		args = parser.parse_args(strict=True)
		try:
			for id in args['id'].split(','):
				temp = Discount.query.get(int(id))
				if temp:
					db.session.delete(temp)
			db.session.commit()
		except:
			db.session.rollback()
			db.session.remove()
			abort(500)
		return make_response([])


class Storage(Resource):
	def post(self, websiteid):
		data = request.get_json()
		#获取请求数据中的data
		array = data['data']
		try:
			# 遍历请求数据
			for operation in array:
				# 获取请求数据中的data请求list
				m_dataArray = operation['data']
				for data in m_dataArray:
					# 通过id判断是否有移动操作
					if 'id' in data:
						id = data['id']
						del data['id']
						args = {key: value for key, value in data.items() if value is not None}
						try:
							Discount.query.filter(Discount.id == id).update(args)
						except:
							db.session.rollback()
							db.session.remove()
					# 通过copy判断是否有复制操作
					else:
						if 'copy' in data:
							copy = data['copy']
							del data['copy']
							discount = Discount.query.filter(Discount.id == copy).first()
							m_args = {}
							m_args['status'] = discount.status
							m_args['title'] = discount.title
							m_args['device'] = discount.device
							m_args['validTimeUpper'] = discount.validTimeUpper
							m_args['validTimeLower'] = discount.validTimeLower
							m_args['content'] = discount.content
							m_args['type'] = discount.type
							m_args['bannerAddress'] = discount.bannerAddress
							m_args['sort'] = discount.sort
							m_res = Discount(**m_args)
							try:
								db.session.add(m_res)
							except:
								db.session.rollback()
								db.session.remove()
						# 没有id和copy就是新增操作
						elif 'id' and 'copy'  not in data:
							args = {key: value for key, value in data.items() if value is not None}
							discount = Discount(**args)
							try:
								db.session.add(discount)
							except:
								db.session.rollback()
								db.session.remove()
				# 删除优惠操作
				if 'remove' in operation:
					remove = operation['remove']
					try:
						for id in remove:
							discount = Discount.query.filter(Discount.id == id).first()
							db.session.delete(discount)
					except:
						db.session.rollback()
						db.session.remove()

			db.session.commit()
		except:
			db.session.rollback()
			db.session.remove()
		return {'success':True,'messages':'操作成功'}

class Carousels(Resource):

	@marshal_with(make_marshal_fields({
		'id': fields.Integer,
		'address': fields.String,
		'sort': fields.Integer,
		'device': fields.Integer,
		'url':fields.String
	}))
	def get(self):
		m_arg = Carousel.query.all()
		return make_response(m_arg)

	def post(self):
		data = request.get_json()
		#获取请求数据中的data
		array = data['data']
		try:
			# 遍历请求数据
			for operation in array:
				# 获取请求数据中的data请求list
				m_dataArray = operation['data']
				device = operation['device']
				if device == 0:
					for data in m_dataArray:
						# 通过id判断是否有移动操作
						if 'id' in data:
							id = data['id']
							del data['id']
							args = {key: value for key, value in data.items() if value is not None}
							try:
								Carousel.query.filter(Carousel.id == id).update(args)
							except:
								db.session.rollback()
								db.session.remove()

						# 通过copy判断是否有复制操作
						else:
							if 'copy' in data:
								copy = data['copy']
								del data['copy']
								carousel = Carousel.query.filter(Carousel.id == copy).first()
								m_args = {}
								m_args['url'] = carousel.url
								m_args['address'] = carousel.address
								m_args['sort'] = carousel.sort
								m_args['device'] = carousel.device
								m_args['device'] = 1
								m_res = Carousel(**m_args)
								try:
									db.session.add(m_res)
								except:
									db.session.rollback()
									db.session.remove()


							# 没有id和copy就是新增操作
							elif 'id' and 'copy'  not in data:
								args = {key: value for key, value in data.items() if value is not None}
								carousel = Carousel(**args)
								try:
									db.session.add(carousel)
								except:
									db.session.rollback()
									db.session.remove()

					# 删除图片操作
					if 'remove' in operation:
						remove = operation['remove']
						try:
							for id in remove:
								carousel = Carousel.query.filter(Carousel.id == id).first()
								db.session.delete(carousel)
						except:
							db.session.rollback()
							db.session.remove()
				else:
					for data in m_dataArray:
						# 通过id判断是否有移动操作
						if 'id' in data:
							id = data['id']
							del data['id']
							args = {key: value for key, value in data.items() if value is not None}
							try:
								Carousel.query.filter(Carousel.id == id).update(args)
							except:
								db.session.rollback()
								db.session.remove()

						# 通过copy判断是否有复制操作
						else:
							if 'copy' in data:
								copy = data['copy']
								del data['copy']
								carousel = Carousel.query.filter(Carousel.id == copy).first()
								m_args = {}
								m_args['address'] = carousel.address
								m_args['url'] = carousel.url
								m_args['sort'] = carousel.sort
								m_args['device'] = carousel.device
								m_args['device'] = 0
								m_res = Carousel(**m_args)
								try:
									db.session.add(m_res)
								except:
									db.session.rollback()
									db.session.remove()


							# 没有id和copy就是新增操作
							elif 'id' and 'copy' not in data:
								args = {key: value for key, value in data.items() if value is not None}
								carousel = Carousel(**args)
								try:
									db.session.add(carousel)
								except:
									db.session.rollback()
									db.session.remove()

					# 删除图片操作
					if 'remove' in operation:
						remove = operation['remove']
						try:
							for id in remove:
								carousel = Carousel.query.filter(Carousel.id == id).first()
								db.session.delete(carousel)
						except:
							db.session.rollback()
							db.session.remove()
			db.session.commit()
		except:
			db.session.rollback()
			db.session.remove()
		return {'success':True,'messages':'操作成功'}


class MemberRegistrationMessages(Resource):

	@marshal_with(make_marshal_fields({
		'content': fields.String,
		'forPC': fields.Integer,
	}))
	def get(self):
		parser = RequestParser()
		parser.add_argument('forPC', type=int, default=1)
		args = parser.parse_args(strict=True)

		result = MemberRegistrationMessage.query.filter(MemberRegistrationMessage.forPC == args['forPC']).first()
		if not result:
			result = MemberRegistrationMessage(forPC=args['forPC'])
			try:
				db.session.add(result)
				db.session.commit()
			except:
				db.session.rollback()
				db.session.remove()
				abort(500)
		return make_response([result])

	def put(self):
		parser = RequestParser()
		parser.add_argument('forPC', type=int, default=1)
		parser.add_argument('content', type=str)
		args = parser.parse_args(strict=True)

		result = MemberRegistrationMessage.query.filter(MemberRegistrationMessage.forPC == args['forPC']).first()
		if not result:
			result = MemberRegistrationMessage(forPC=args['forPC'])
			try:
				db.session.add(result)
				db.session.commit()
			except:
				db.session.rollback()
				db.session.remove()
				abort(500)

		result.content = args['content']
		try:
			db.session.add(result)
			db.session.commit()
		except:
			db.session.rollback()
			db.session.remove()
			abort(500)
		return make_response([])

class ImportTemplates(Resource):
	def get(self):
		return {
			'success': True,
			'memberSearch': 'ImportMemberSearchTemplate.xlsx',
			'memberCreate': 'ImportMemberCreateTemplate.xlsx',
			'discount': 'ImportDiscountTemplate.xlsx'
		}
# 公告管理--设定
class NoticeSetting(Resource):
	@marshal_with(make_marshal_fields({
		'id': fields.Integer,
		'change': fields.Integer,
		'frequency': fields.Integer,
		'refresh': fields.Integer,
		'title':fields.String
	}))

	def get(self):
		setting = NoticeSet.query.all()
		return make_response(setting)

	def put(self, id):
		parser = RequestParser(trim=True)
		parser.add_argument('change', type=int)
		parser.add_argument('frequency', type=int)
		parser.add_argument('refresh', type=int)
		parser.add_argument('title', type=str)
		args = parser.parse_args(strict=True)
		args = {key: value for key, value in args.items() if value is not None}

		try:
			NoticeSet.query.filter(NoticeSet.id == id).update(args)
			db.session.commit()
		except:
			db.session.rollback()
			db.session.remove()
		return {'success':True}

# 站内信收件夹模糊搜索
class Searchname(Resource):

	def get(self):
		parser = RequestParser()
		parser.add_argument('sender', type=str)
		parser.add_argument('receiver', type=str)
		args = parser.parse_args(strict=True)
		# 发件人
		if args["sender"]:
			sender = args["sender"]
			query = db.session.query(distinct(MessageInbox.sendername)).filter(MessageInbox.sendername.like("%{}%".format(sender))).all()
		# 收件人
		if args["receiver"]:
			receiver = args["receiver"]
			query = db.session.query(distinct(MessageInbox.receivername)).filter(MessageInbox.receivername.like("%{}%".format(receiver))).all()

		return 	make_response(query)
# 站内信寄件夹模糊搜索
class SearchUname(Resource):

	def get(self):
		parser = RequestParser()
		parser.add_argument('sender', type=str)
		parser.add_argument('receiver', type=str)
		args = parser.parse_args(strict=True)
		# 发件人
		if args["sender"]:
			sender = args["sender"]
			query = db.session.query(distinct(MessageOutbox.sendername)).filter(MessageOutbox.sendername.like("%{}%".format(sender))).all()
		# 收件人
		if args["receiver"]:
			receiver = args["receiver"]
			query = db.session.query(distinct(MessageOutbox.receivername)).filter(MessageOutbox.receivername.like("%{}%".format(receiver),)).all()

		return 	make_response(query)