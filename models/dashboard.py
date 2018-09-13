from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP, Boolean
from models.base import CRUDMixin, db


STATUS = {0: 'Created', 1: 'Started', 2: 'In-progress', 3: 'Completed', 4:'Close', 5:'Deleted'}

FEATURES = {1: 'Tissue Type', 2: 'Site', 3: 'Gender', 4: 'Metastatic Site', 5: 'EGFR',
			6: 'IDH1', 7: 'IDH2', 8: 'TP53', 9: 'Age', 10: 'Tumor Grade', 11: 'Tumor Stage'}


class Samples(CRUDMixin, db.Model):
	"""
		Sample info is nothing but predefined data by application
	"""
	id = Column(Integer, primary_key=True, autoincrement=True)
	sample_id = Column(String(100), nullable=False)
	tissue_type = Column(String(50), nullable=False)
	site = Column(String(50), nullable=False)
	gender = Column(String(10), nullable=False)
	metastatic_site = Column(String(10), nullable=False)
	cancer = Column(String(100), nullable=False)
	EGFR = Column(Boolean, nullable=False)
	IDH1 = Column(Boolean, nullable=False)
	IDH2 = Column(Boolean, nullable=False)
	TP53 = Column(Boolean, nullable=False)
	age_in_year = Column(Integer, nullable=True)
	tumor_grade = Column(String(100), nullable=True)
	tumor_stage = Column(String(100), nullable=True)


class Job(CRUDMixin, db.Model):
	"""
		Job Info created by user
	"""
	id = Column(Integer, primary_key=True, autoincrement=True)
	user_id = Column(Integer, ForeignKey('portalUser.id'))
	name = Column(String(50), unique=True)
	status = Column(Integer, nullable=False, default=0)
	creationTime = Column(TIMESTAMP, nullable=False, server_default=str(datetime.now()))
	sample_id = Column(Integer, ForeignKey('samples.id', ondelete='cascade'))

	@staticmethod
	def get_new_id():
		try:
			lastrowid = Job.query().filter().last.id
			print lastrowid
			return lastrowid + 1
		except Exception as e:
			print str(e)
			return 1


class JobDetails(CRUDMixin, db.Model):
	id = Column(Integer, primary_key=True, autoincrement=True)
	job_id = Column(Integer, ForeignKey('job.id', ondelete='cascade'))
	out_file = Column(String(50), nullable=False)
	creationTime = Column(TIMESTAMP, nullable=False, server_default=str(datetime.now()))


def get_sites():
	sites = db.session.query(Samples.site).distinct().all()
	return [s[0] for s in sites]


def get_metastatics():
	metastatics = db.session.query(Samples.metastatic_site).distinct().all()
	return [m[0] for m in metastatics]


def get_grades():
	grades = db.session.query(Samples.tumor_grade).distinct().all()
	return [g[0] for g in grades]


def get_stages():
	stages = db.session.query(Samples.tumor_stage).distinct().all()
	return [s[0] for s in stages]


def get_diseases():
	diseases = db.session.query(Samples.cancer).distinct().all()
	return [d[0] for d in diseases]
