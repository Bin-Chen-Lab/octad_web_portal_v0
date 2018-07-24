from flask_login import UserMixin
from app import db
from models.base import CRUDMixin
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, TIMESTAMP, text
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


class User(UserMixin, CRUDMixin, db.Model):
	"""
	This table stores User Info w. r. t. roles
	List of Roles
		Admin
		General
	"""
	__tablename__ = "portaluser"
	id = Column(Integer, primary_key=True, autoincrement=True)
	username = Column(String(50), unique=True)
	password = Column(String(128), nullable=False)
	role = Column(String(15), nullable=False, default='GENERAL')
	organization = Column(String(50), nullable=True)
	isActivated = Column(Boolean, default=False)
	loginTime = Column(TIMESTAMP, nullable=True)

	def __init__(self, username, passeword, role, isActivated):
		self.username = username
		self.password = passeword
		self.role = role
		self.isActivated = isActivated
		self.loginTime = datetime.now()

	def __repr__(self):
		return "Username: %s " % self.username

	def get_id(self):
		return unicode(self.id)


def generate_password(raw_passwd):
	password = generate_password_hash(raw_passwd)
	return password


def check_password(password, raw_passwd):
	return check_password_hash(password, raw_passwd)
