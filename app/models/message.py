from . import db

class MessageOutbox(db.Model):
	__tablename__ = 'blast_message_send'

	id = db.Column( db.Integer, primary_key=True)
	sendername = db.Column(db.Integer)
	receivername = db.Column(db.String)
	receiverid = db.Column(db.Integer)
	title = db.Column(db.String)
	content = db.Column(db.String)
	time = db.Column(db.Integer)
	senderShowid = db.Column(db.Integer)

class MessageInbox(db.Model):
	__tablename__ = 'blast_message_receive'

	id = db.Column(db.Integer, primary_key=True)
	sendername = db.Column( db.String)
	senderid = db.Column(db.Integer)
	receivername = db.Column(db.String)
	read = db.Column( db.Integer, default=0)
	title = db.Column(db.String)
	content = db.Column(db.String)
	time = db.Column(db.Integer)
	receiverid = db.Column(db.Integer)

class Notice(db.Model):
	__tablename__ = 'blast_content'

	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String)
	createTime = db.Column('addTime', db.Integer)
	updateTime = db.Column(db.Integer)
	title = db.Column(db.String)
	content = db.Column(db.String)
	sort = db.Column(db.Integer, default=0)
	device = db.Column(db.Integer, default=0)
	forMember = db.Column(db.Integer, default=0)
	status = db.Column('enable', db.Integer, default=1)

class DiscountType(db.Model):
	__tablename__ = 'tb_discount_types'

	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String)
	websiteid = db.Column(db.Integer)
	sort = db.Column(db.Integer)
	device = db.Column(db.Integer, default=0)

class Discount(db.Model):
	__tablename__ = 'tb_discounts'

	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String)
	content = db.Column(db.String)
	type = db.Column(db.Integer)
	sort = db.Column(db.Integer)
	status = db.Column(db.Integer, default=1)
	validTimeLower = db.Column(db.Integer)
	validTimeUpper = db.Column(db.Integer)
	device = db.Column(db.Integer)
	bannerAddress = db.Column(db.String)

class Carousel(db.Model):
	__tablename__ = 'tb_carousels'

	id = db.Column(db.Integer, primary_key=True)
	address = db.Column(db.String)
	sort = db.Column(db.Integer, default=0)
	device = db.Column(db.Integer, default=0)
	url = db.Column(db.String)

class MemberRegistrationMessage(db.Model):
	__tablename__ = 'tb_member_registration_messages'

	id = db.Column(db.Integer, primary_key=True)
	content = db.Column(db.String, default='')
	forPC = db.Column(db.Integer, default=1)

class Websites(db.Model):
	__tablename__ = 'tb_website'

	id = db.Column(db.Integer, primary_key=True)
	webname = db.Column(db.String)
	weburl = db.Column(db.String)
	remark = db.Column(db.String)

# 公告管理-设定表
class NoticeSet(db.Model):
	__tablename__  = 'blast_content_setting'

	id = db.Column(db.Integer, primary_key=True)
	change = db.Column(db.Integer,default=0)
	frequency = db.Column(db.Integer,default=0)
	refresh = db.Column(db.Integer,default=0)
	title = db.Column(db.String)

class SenderShow(db.Model):
	__tablename__ = 'blast_massage_sendShow'

	id = db.Column(db.Integer, primary_key=True)
	time = db.Column(db.Integer)
	title = db.Column(db.String)
	content = db.Column(db.String)
	senderName = db.Column(db.String, )
	countMember = db.Column(db.Integer)
	receiveAllName = db.Column(db.String)


