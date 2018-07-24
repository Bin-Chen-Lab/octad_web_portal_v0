from flask import Flask, g, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import import_string
from flask_login import LoginManager


app = Flask(__name__)
app.config.from_envvar('APP_CONFIG_FILE')

# Database Connection via sqlalchemy
db = SQLAlchemy(app)

# flask initialization
login_manager = LoginManager(app)
login_manager.login_view = "profile.login"


@login_manager.user_loader
def load_user(user_id):
	from models.profile import User
	return User.query.filter_by(id=int(user_id)).first()


def before_request():
	"""pull user info from the database based on session id"""

	from models.profile import User
	g.user = None
	if 'user_id' in session:
		try:
			try:
				g.user = User.query.get(session['user_id'])
			except TypeError:  # session probably expired
				pass
		except KeyError:
			pass


class NoBlueprintException(Exception):
	pass


def _get_imported_stuff_by_path(path):
	module_name, object_name = path.rsplit('.', 1)
	module = import_string(module_name)

	return module, object_name


def _register_blueprints():
	for blueprint_path in app.config.get('BLUEPRINTS', []):
		module, b_name = _get_imported_stuff_by_path(blueprint_path)
		if hasattr(module, b_name):
			app.register_blueprint(getattr(module, b_name))
		else:
			raise NoBlueprintException('No {bp_name} blueprint found'.format(bp_name=b_name))


_register_blueprints()


if __name__ == '__main__':
	app.run()
