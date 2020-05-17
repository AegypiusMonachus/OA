'''
from flask_socketio import SocketIO, disconnect
socketio = SocketIO(async_mode=None)


@socketio.on('connect')
def connect():
	from app.auth.common import token_auth
	from app.models.user import User
	auth = token_auth.get_auth()
	token = auth.get('token')
	if not token or not User.verify_token(token):
		return False


@socketio.on('disconnect')
def disconnect():
	pass


from gevent.queue import Queue
queue = Queue()


def background_task():
	while True:
		socketio.emit('foo response', {'data': queue.get()}, namespace='/foo')
		socketio.sleep(3)
'''

from flask_bcrypt import Bcrypt
bcrypt = Bcrypt()


from flask_login import LoginManager
login_manager = LoginManager()


login_manager.session_protection = 'strong'
login_manager.login_view = ''
login_manager.login_message = ''
login_manager.login_message_category = ''


@login_manager.user_loader
def user_loader(id):
	from .models.user import User
	return User.query.get(id)


from flask_principal import Principal
principals = Principal()
