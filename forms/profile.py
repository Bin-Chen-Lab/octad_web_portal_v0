from flask_wtf import FlaskForm
from wtforms.fields import StringField
from wtforms.validators import DataRequired


# login form
class LoginForm(FlaskForm):
	class Meta:
		csrf_time_limit = 60  # seconds
	username = StringField('username', [DataRequired()])
	password = StringField('password', [DataRequired()])
