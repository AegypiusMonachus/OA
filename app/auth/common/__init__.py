from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth, MultiAuth
basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth()
multi_auth = MultiAuth(basic_auth, token_auth)


from flask import g

from app.models.user import User
from app.models.member import Member


class Object:
	pass


@basic_auth.verify_password
def verify_password(username=None, password=None):
	user = User.query.filter(User.username == username).first()
	g.current_user = None
	if user:
		g.current_user = Object()
		g.current_user.id = user.id
		g.current_user.username = user.username
	return user is not None and user.verify_password(password)


@token_auth.verify_token
def verify_token(token=None):
	from flask import current_app
	if not token:
# 		user = User.query.filter(User.username == 'default').first()
# 		g.current_user = Object()
# 		g.current_user.id = user.id
# 		g.current_user.username = user.username
#  
# 		member = Member.query.filter(Member.username == 'KK').first()
# 		g.current_member = Object()
# 		g.current_member.id = member.id
# 		g.current_member.username = member.username
		return False
	user = User.verify_token(token)
	g.current_user = None
	if user:
		g.current_user = Object()
		g.current_user.id = user.id
		g.current_user.username = user.username

	member = Member.verify_token(token)
	g.current_member = None
	if member:
		g.current_member = Object()
		g.current_member.id = member.id
		g.current_member.username = member.username
		g.current_member.isTsetPLay = member.isTsetPLay
		g.current_member.auto_change = member.auto_change
	return g.current_user is not None or g.current_member is not None