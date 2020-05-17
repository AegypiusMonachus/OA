from flask import Blueprint
auth_blueprint = Blueprint('auth', __name__)


@auth_blueprint.before_request
def before_request():
	pass


@auth_blueprint.after_request
def after_request(response):
	return response


from . import errors


from .views import (
	UserLogin,
	UserLogout,
	UserPasswordVerification,
	MemberLogin,
	ChatroomLogin
)
auth_blueprint.add_url_rule('/userLogin', view_func=UserLogin.as_view('userLogin'))
auth_blueprint.add_url_rule('/userLogout', view_func=UserLogout.as_view('userLogout'))
auth_blueprint.add_url_rule('/userPasswordVerification', view_func=UserPasswordVerification.as_view('userPasswordVerification'))
auth_blueprint.add_url_rule('/memberLogin', view_func=MemberLogin.as_view('memberLogin'))
auth_blueprint.add_url_rule('/chatroomLogin', view_func=ChatroomLogin.as_view('chatroomLogin'))
