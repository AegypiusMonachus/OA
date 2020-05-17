from flask import Blueprint
common_blueprint = Blueprint('common', __name__)


@common_blueprint.before_request
def before_request():
	pass


@common_blueprint.after_request
def after_request(response):
	return response


from .views import Upload
common_blueprint.add_url_rule('/upload', view_func=Upload.as_view('upload'))


from .views import (
	GuestNotices,
	GuestDiscounts,
	GuestCarousels,
)
common_blueprint.add_url_rule('/guestNotices', view_func=GuestNotices.as_view('guestNotices'))
common_blueprint.add_url_rule('/guestDiscounts', view_func=GuestDiscounts.as_view('guestDiscounts'))
common_blueprint.add_url_rule('/guestCarousels', view_func=GuestCarousels.as_view('guestCarousels'))


'''
from .views import Touch, WebSocketDemo
common_blueprint.add_url_rule('/touch', view_func=Touch.as_view('touch'))
common_blueprint.add_url_rule('/demo', view_func=WebSocketDemo.as_view('demo'))
'''
