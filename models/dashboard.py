from flask import g
from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP, Boolean, TEXT, or_
from sqlalchemy.orm import relationship, backref
from models.base import CRUDMixin, db


STATUS = {0: 'Created', 1: 'Case Visualization', 2: 'Ref Tissue Algo Run', 3: 'Control Visualization',
		4: 'Signature Compute', 5: 'Drug Predection In-progress', 6: 'Completed'}

#FEATURES = {1: 'Tissue Type', 2: 'Site', 3: 'Gender', 4: 'Metastatic Site', 5: 'EGFR',
#			6: 'IDH1', 7: 'IDH2', 8: 'TP53', 9: 'Age', 10: 'Tumor Grade', 11: 'Tumor Stage'}

FEATURES = {1: 'Tissue Type', 2: 'Site', 3: 'Gender'} # 4: 'Metastatic Site', 5: 'EGFR',
			#6: 'IDH1', 7: 'IDH2', 8: 'TP53', 9: 'Age', 10: 'Tumor Grade', 11: 'Tumor Stage'}

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
	EGFR = Column(String(10), nullable=False, default='NA')
	IDH1 = Column(String(10), nullable=False, default='NA')
	IDH2 = Column(String(10), nullable=False, default='NA')
	TP53 = Column(String(10), nullable=False, default='NA')
	age_in_year = Column(Integer, nullable=True)
	tumor_grade = Column(String(100), nullable=True)
	tumor_stage = Column(String(100), nullable=True)


class Job(CRUDMixin, db.Model):
	"""
		Job Info created by user
	"""
	id = Column(Integer, primary_key=True, autoincrement=True)
	user_id = Column(Integer, ForeignKey('portaluser.id'), nullable=True)
	name = Column(String(50))
	status = Column(Integer, nullable=False, default=0)
	creationTime = Column(TIMESTAMP, nullable=False)
	description = Column(TEXT, nullable=True)
	is_save = Column(Boolean, default=False)

	userDetails = relationship("User", backref=backref("users"))

	@staticmethod
	def get_new_id():
		try:
			# lastrowid = Job.query.order_by('-id').first().id
			# print lastrowid
			# return lastrowid + 1
			if g.user:
				job = Job(name='new_job', user_id=g.user.id)
			else:
				job = Job(name='new_job')
			job.save()
			jobDetails = JobDetails(job_id=job.id)
			jobDetails.save()
			return job.id
		except Exception as e:
			print str(e)
			return 1


class JobDetails(CRUDMixin, db.Model):
	id = Column(Integer, primary_key=True, autoincrement=True)
	job_id = Column(Integer, ForeignKey('job.id', ondelete='cascade'))
	creationTime = Column(TIMESTAMP, nullable=False)
	disease_name = Column(String(200), nullable=True)
	case_sample_id = Column(TEXT, nullable=True)
	case_tissue_type = Column(String(50), nullable=True)
	case_site = Column(String(50), nullable=True)
	case_gender = Column(String(10), nullable=True)
	case_metastatic_site = Column(String(10), nullable=True)
	case_EGFR = Column(String(10), nullable=True, default='NA')
	case_IDH1 = Column(String(10), nullable=True, default='NA')
	case_IDH2 = Column(String(10), nullable=True, default='NA')
	case_TP53 = Column(String(10), nullable=True, default='NA')
	case_age_in_year = Column(String(50), nullable=True)
	case_tumor_grade = Column(String(100), nullable=True)
	case_tumor_stage = Column(String(100), nullable=True)
	ctrl_sample_id = Column(TEXT, nullable=True)
	ctrl_tissue_type = Column(String(50), nullable=True)
	ctrl_site = Column(String(50), nullable=True)
	ctrl_gender = Column(String(10), nullable=True)
	ctrl_metastatic_site = Column(String(10), nullable=True)
	ctrl_EGFR = Column(String(10), nullable=True, default='NA')
	ctrl_IDH1 = Column(String(10), nullable=True, default='NA')
	ctrl_IDH2 = Column(String(10), nullable=True, default='NA')
	ctrl_TP53 = Column(String(10), nullable=True, default='NA')
	ctrl_age_in_year = Column(String(50), nullable=True)
	ctrl_tumor_grade = Column(String(100), nullable=True)
	ctrl_tumor_stage = Column(String(100), nullable=True)
	de_method = Column(String(50), nullable=True)
	dz_fc_threshold = Column(String(50), nullable=True)
	dz_p_threshold = Column(String(50), nullable=True)
	database = Column(String(50), nullable=True)
	choose_fda_drugs = Column(String(10), nullable=True)
	max_gene_size = Column(String(50), nullable=True)
	landmark = Column(String(50), nullable=True)
	weight_cell_line = Column(String(10), nullable=True)
	debug = Column(String(10), nullable=True)

	jobDetails = relationship("Job", backref=backref("jobs"))


def get_sites(disease=None, tissue_type=None, gender=None, metastatic=None,
			  egfr=None, idh1=None, idh2=None, tp53=None, age=None,
			  tumor_grade=None, tumor_stage=None):
	filter_str = []
	if disease:
		filter_str.append(Samples.cancer == disease)
	if tissue_type:
		filter_str.append(or_(Samples.tissue_type.in_(tissue_type)))
	if gender:
		filter_str.append(Samples.gender == gender)
	if metastatic:
		filter_str.append(Samples.metastatic_site == metastatic)
	if egfr:
		filter_str.append(Samples.EGFR == egfr)
	if idh1:
		filter_str.append(Samples.IDH1 == idh1)
	if idh2:
		filter_str.append(Samples.IDH2 == idh2)
	if tp53:
		filter_str.append(Samples.TP53 == tp53)
	if age:
		age_range = age.split('-')
		start = int(age_range[0].strip())
		end = int(age_range[1].strip())
		filter_str.append(Samples.age_in_year.between(start, end))
	if tumor_grade:
		filter_str.append(Samples.tumor_grade == tumor_grade)
	if tumor_stage:
		filter_str.append(or_(Samples.tumor_stage.in_(tumor_stage)))

	sites = db.session.query(Samples.site).filter(*filter_str).order_by(Samples.site.asc()).distinct().all()

	return [s[0] for s in sites if s[0] and s[0] != '<NOT PROVIDED>']


def get_metastatics(disease=None, tissue_type=None, site=None, gender=None, egfr=None, idh1=None, idh2=None, tp53=None,
					age=None, tumor_grade=None, tumor_stage=None):
	filter_str = []
	if disease:
		filter_str.append(Samples.cancer == disease)
	if tissue_type:
		filter_str.append(or_(Samples.tissue_type.in_(tissue_type)))
	if gender:
		filter_str.append(Samples.gender == gender)
	if site:
		filter_str.append(Samples.site == site)
	if egfr:
		filter_str.append(Samples.EGFR == egfr)
	if idh1:
		filter_str.append(Samples.IDH1 == idh1)
	if idh2:
		filter_str.append(Samples.IDH2 == idh2)
	if tp53:
		filter_str.append(Samples.TP53 == tp53)
	if age:
		age_range = age.split('-')
		start = int(age_range[0].strip())
		end = int(age_range[1].strip())
		filter_str.append(Samples.age_in_year.between(start, end))
	if tumor_grade:
		filter_str.append(Samples.tumor_grade == tumor_grade)
	if tumor_stage:
		filter_str.append(or_(Samples.tumor_stage.in_(tumor_stage)))

	metastatics = db.session.query(Samples.metastatic_site).filter(*filter_str).order_by(Samples.metastatic_site.asc()).distinct().all()

	return [m[0] for m in metastatics if m[0]]


def get_grades(disease=None, tissue_type=None, site=None, gender=None, metastatic=None,
			   egfr=None, idh1=None, idh2=None, tp53=None, age=None, tumor_stage=None):
	filter_str = []
	if disease:
		filter_str.append(Samples.cancer == disease)
	if tissue_type:
		filter_str.append(or_(Samples.tissue_type.in_(tissue_type)))
	if gender:
		filter_str.append(Samples.gender == gender)
	if site:
		filter_str.append(Samples.site == site)
	if egfr:
		filter_str.append(Samples.EGFR == egfr)
	if idh1:
		filter_str.append(Samples.IDH1 == idh1)
	if idh2:
		filter_str.append(Samples.IDH2 == idh2)
	if tp53:
		filter_str.append(Samples.TP53 == tp53)
	if age:
		age_range = age.split('-')
		start = int(age_range[0].strip())
		end = int(age_range[1].strip())
		filter_str.append(Samples.age_in_year.between(start, end))
	if metastatic:
		filter_str.append(Samples.metastatic_site == metastatic)
	if tumor_stage:
		filter_str.append(or_(Samples.tumor_stage.in_(tumor_stage)))

	grades = db.session.query(Samples.tumor_grade).filter(*filter_str).order_by(Samples.tumor_grade.asc()).distinct().all()

	return [g[0] for g in grades if g[0]]


def get_stages(disease=None, tissue_type=None, site=None, gender=None, metastatic=None,
			   egfr=None, idh1=None, idh2=None, tp53=None, age=None, tumor_grade=None):
	filter_str = []
	if disease:
		filter_str.append(Samples.cancer == disease)
	if tissue_type:
		filter_str.append(or_(Samples.tissue_type.in_(tissue_type)))
	if gender:
		filter_str.append(Samples.gender == gender)
	if site:
		filter_str.append(Samples.site == site)
	if egfr:
		filter_str.append(Samples.EGFR == egfr)
	if idh1:
		filter_str.append(Samples.IDH1 == idh1)
	if idh2:
		filter_str.append(Samples.IDH2 == idh2)
	if tp53:
		filter_str.append(Samples.TP53 == tp53)
	if age:
		age_range = age.split('-')
		start = int(age_range[0].strip())
		end = int(age_range[1].strip())
		filter_str.append(Samples.age_in_year.between(start, end))
	if tumor_grade:
		filter_str.append(Samples.tumor_grade == tumor_grade)
	if metastatic:
		filter_str.append(Samples.metastatic_site == metastatic)

	stages = db.session.query(Samples.tumor_stage).filter(*filter_str).order_by(Samples.tumor_stage.asc()).distinct().all()

	return [s[0] for s in stages if s[0]]


def get_diseases():
	diseases = db.session.query(Samples.cancer).order_by(Samples.cancer.asc()).distinct().all()
	return [d[0] for d in diseases if d[0]]


def get_tissue_types(disease=None, site=None, gender=None, metastatic=None, egfr=None, idh1=None,
					 idh2=None, tp53=None, age=None, tumor_grade=None, tumor_stage=None):
	filter_str = []
	if disease:
		filter_str.append(Samples.cancer == disease)
	if gender:
		filter_str.append(Samples.gender == gender)
	if site:
		filter_str.append(Samples.site == site)
	if egfr:
		filter_str.append(Samples.EGFR == egfr)
	if idh1:
		filter_str.append(Samples.IDH1 == idh1)
	if idh2:
		filter_str.append(Samples.IDH2 == idh2)
	if tp53:
		filter_str.append(Samples.TP53 == tp53)
	if age:
		age_range = age.split('-')
		start = int(age_range[0].strip())
		end = int(age_range[1].strip())
		filter_str.append(Samples.age_in_year.between(start, end))
	if tumor_grade:
		filter_str.append(Samples.tumor_grade == tumor_grade)
	if metastatic:
		filter_str.append(Samples.metastatic_site == metastatic)
	if tumor_stage:
		filter_str.append(or_(Samples.tumor_stage.in_(tumor_stage)))

	tissue_types = db.session.query(Samples.tissue_type).filter(Samples.cancer == disease).order_by(Samples.tissue_type.asc()).distinct().all()

	return [s[0] for s in tissue_types if s[0]]



def get_gender(disease=None, tissue_type=None, site=None, metastatic=None, egfr=None, idh1=None, idh2=None,
			   tp53=None, age=None, tumor_grade=None, tumor_stage=None):
	filter_str = []
	if disease:
		filter_str.append(Samples.cancer == disease)
	if tissue_type:
		filter_str.append(or_(Samples.tissue_type.in_(tissue_type)))
	if metastatic:
		filter_str.append(Samples.metastatic_site == metastatic)
	if site:
		filter_str.append(Samples.site == site)
	if egfr:
		filter_str.append(Samples.EGFR == egfr)
	if idh1:
		filter_str.append(Samples.IDH1 == idh1)
	if idh2:
		filter_str.append(Samples.IDH2 == idh2)
	if tp53:
		filter_str.append(Samples.TP53 == tp53)
	if age:
		age_range = age.split('-')
		start = int(age_range[0].strip())
		end = int(age_range[1].strip())
		filter_str.append(Samples.age_in_year.between(start, end))
	if tumor_grade:
		filter_str.append(Samples.tumor_grade == tumor_grade)
	if tumor_stage:
		filter_str.append(or_(Samples.tumor_stage.in_(tumor_stage)))

	gender = db.session.query(Samples.gender).filter(*filter_str).order_by(Samples.gender.asc()).distinct().all()

	return [s[0] for s in gender if s[0]]


def get_EGFR(disease=None, tissue_type=None, site=None, gender=None, metastatic=None, idh1=None, idh2=None, tp53=None, age=None, tumor_grade=None, tumor_stage=None):
	filter_str = []
	if disease:
		filter_str.append(Samples.cancer == disease)
	if tissue_type:
		filter_str.append(or_(Samples.tissue_type.in_(tissue_type)))
	if metastatic:
		filter_str.append(Samples.metastatic_site == metastatic)
	if site:
		filter_str.append(Samples.site == site)
	if gender:
		filter_str.append(Samples.gender == gender)
	if idh1:
		filter_str.append(Samples.IDH1 == idh1)
	if idh2:
		filter_str.append(Samples.IDH2 == idh2)
	if tp53:
		filter_str.append(Samples.TP53 == tp53)
	if age:
		age_range = age.split('-')
		start = int(age_range[0].strip())
		end = int(age_range[1].strip())
		filter_str.append(Samples.age_in_year.between(start, end))
	if tumor_grade:
		filter_str.append(Samples.tumor_grade == tumor_grade)
	if tumor_stage:
		filter_str.append(or_(Samples.tumor_stage.in_(tumor_stage)))

	egfr = db.session.query(Samples.EGFR).filter(*filter_str).order_by(Samples.EGFR.asc()).distinct().all()

	return [s[0] for s in egfr if s[0]]


def get_IDH1(disease=None, tissue_type=None, site=None, gender=None, metastatic=None, egfr=None, idh2=None, tp53=None, age=None, tumor_grade=None, tumor_stage=None):
	filter_str = []
	if disease:
		filter_str.append(Samples.cancer == disease)
	if tissue_type:
		filter_str.append(or_(Samples.tissue_type.in_(tissue_type)))
	if metastatic:
		filter_str.append(Samples.metastatic_site == metastatic)
	if site:
		filter_str.append(Samples.site == site)
	if egfr:
		filter_str.append(Samples.EGFR == egfr)
	if gender:
		filter_str.append(Samples.gender == gender)
	if idh2:
		filter_str.append(Samples.IDH2 == idh2)
	if tp53:
		filter_str.append(Samples.TP53 == tp53)
	if age:
		age_range = age.split('-')
		start = int(age_range[0].strip())
		end = int(age_range[1].strip())
		filter_str.append(Samples.age_in_year.between(start, end))
	if tumor_grade:
		filter_str.append(Samples.tumor_grade == tumor_grade)
	if tumor_stage:
		filter_str.append(or_(Samples.tumor_stage.in_(tumor_stage)))

	idh1 = db.session.query(Samples.IDH1).filter(*filter_str).order_by(Samples.IDH1.asc()).distinct().all()

	return [s[0] for s in idh1 if s[0]]


def get_IDH2(disease=None, tissue_type=None, site=None, gender=None, metastatic=None, egfr=None, idh1=None, tp53=None, age=None, tumor_grade=None, tumor_stage=None):
	filter_str = []
	if disease:
		filter_str.append(Samples.cancer == disease)
	if tissue_type:
		filter_str.append(or_(Samples.tissue_type.in_(tissue_type)))
	if metastatic:
		filter_str.append(Samples.metastatic_site == metastatic)
	if site:
		filter_str.append(Samples.site == site)
	if egfr:
		filter_str.append(Samples.EGFR == egfr)
	if idh1:
		filter_str.append(Samples.IDH1 == idh1)
	if gender:
		filter_str.append(Samples.gender == gender)
	if tp53:
		filter_str.append(Samples.TP53 == tp53)
	if age:
		age_range = age.split('-')
		start = int(age_range[0].strip())
		end = int(age_range[1].strip())
		filter_str.append(Samples.age_in_year.between(start, end))
	if tumor_grade:
		filter_str.append(Samples.tumor_grade == tumor_grade)
	if tumor_stage:
		filter_str.append(or_(Samples.tumor_stage.in_(tumor_stage)))

	idh2 = db.session.query(Samples.IDH2).filter(*filter_str).order_by(Samples.IDH2.asc()).distinct().all()

	return [s[0] for s in idh2 if s[0]]


def get_TP53(disease=None, tissue_type=None, site=None, gender=None, metastatic=None, egfr=None, idh1=None, idh2=None, age=None, tumor_grade=None, tumor_stage=None):
	filter_str = []
	if disease:
		filter_str.append(Samples.cancer == disease)
	if tissue_type:
		filter_str.append(or_(Samples.tissue_type.in_(tissue_type)))
	if metastatic:
		filter_str.append(Samples.metastatic_site == metastatic)
	if site:
		filter_str.append(Samples.site == site)
	if egfr:
		filter_str.append(Samples.EGFR == egfr)
	if idh1:
		filter_str.append(Samples.IDH1 == idh1)
	if idh2:
		filter_str.append(Samples.IDH2 == idh2)
	if gender:
		filter_str.append(Samples.gender == gender)
	if age:
		age_range = age.split('-')
		start = int(age_range[0].strip())
		end = int(age_range[1].strip())
		filter_str.append(Samples.age_in_year.between(start, end))
	if tumor_grade:
		filter_str.append(Samples.tumor_grade == tumor_grade)
	if tumor_stage:
		filter_str.append(or_(Samples.tumor_stage.in_(tumor_stage)))

	tp53 = db.session.query(Samples.TP53).filter(*filter_str).order_by(Samples.TP53.asc()).distinct().all()

	return [s[0] for s in tp53 if s[0]]

