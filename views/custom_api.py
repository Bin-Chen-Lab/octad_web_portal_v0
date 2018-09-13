import json, os
import collections
from flask import Blueprint, request
from app import app
from models.dashboard import get_diseases, Samples, Job, STATUS
from models.profile import User


apiRoute = Blueprint('api', __name__)


@apiRoute.route('/sample/api', methods=["GET"])
# @csrf.exempt
def sampleApi():
	"""
	json of job information
	:return: json object
	"""
	diseases = ["Brain Lower Grade Glioma","Breast Invasive Ductal Carcinoma","Breast Invasive Lobular Carcinoma","Breast Invasive Carcinoma","Solitary Fibrous Tumor" ]
	samples = Samples.query.filter(Samples.cancer.in_(diseases)).all()
	"""
	sampleList = [[sample.id, sample.sample_id, sample.tissue_type, sample.age_in_year, sample.site,
				   sample.gender, sample.metastatic_site, sample.cancer, 1 if sample.EGFR else 0,
				   1 if sample.IDH1 else 0, 1 if sample.IDH2 else 0, 1 if sample.TP53 else 0,
				   sample.tumor_grade, sample.tumor_stage] for sample in samples]


	sampleList = []
	for sample in samples:
		sampleList.append([sample.id, sample.sample_id, sample.tissue_type, sample.age_in_year, sample.site,
				   sample.gender, sample.metastatic_site, sample.cancer, 1 if sample.EGFR else 0,
				   1 if sample.IDH1 else 0, 1 if sample.IDH2 else 0, 1 if sample.TP53 else 0,
				   sample.tumor_grade, sample.tumor_stage])
	"""
	sampleList = []
	for sample in samples:
		d = collections.OrderedDict()
		d['id'] = sample.id
		d['sample_id'] = sample.sample_id
		d['tissue_type'] = sample.tissue_type
		d['age_in_year'] = sample.age_in_year
		d['site'] = sample.site
		d['gender'] = sample.gender
		d['metastatic_site'] = sample.metastatic_site
		d['cancer'] = sample.cancer
		d['egfr'] = 1 if sample.EGFR else 0
		d['idh1'] = 1 if sample.IDH1 else 0
		d['idh2'] = 1 if sample.IDH2 else 0
		d['tp53'] = 1 if sample.TP53 else 0
		d['tumor_grade'] = sample.tumor_grade
		d['tumor_stage'] = sample.tumor_stage
		sampleList.append(d)

	return json.dumps(sampleList)


@apiRoute.route('/sample/control/api', methods=["POST"])
# @csrf.exempt
def controlSampleApi():
	"""
	json of job information
	:return: json object
	"""
	site = ''
	sample_list = []
	if request.method == 'POST':
		data = request.get_json(force=True)
		file_path = os.path.join(app.config['RREPO_OUTPUT'], str(data['job_id']), data['file_name'])
		f = open(file_path, 'r')
		lines = f.readlines()
		site = lines[0].replace('\n', '')
		control_id = [line.replace('\n', '').replace('-', '.') for line in lines[1:]]
		samples = Samples.query.filter(Samples.sample_id.in_(control_id)).all()
		for sample in samples:
			d = collections.OrderedDict()
			d['id'] = sample.id
			d['sample_id'] = sample.sample_id
			d['tissue_type'] = sample.tissue_type
			d['age_in_year'] = sample.age_in_year
			d['site'] = sample.site
			d['gender'] = sample.gender
			d['metastatic_site'] = sample.metastatic_site
			d['cancer'] = sample.cancer
			d['egfr'] = 1 if sample.EGFR else 0
			d['idh1'] = 1 if sample.IDH1 else 0
			d['idh2'] = 1 if sample.IDH2 else 0
			d['tp53'] = 1 if sample.TP53 else 0
			d['tumor_grade'] = sample.tumor_grade
			d['tumor_stage'] = sample.tumor_stage
			sample_list.append(d)
	data = {"site": site, "samples": sample_list}
	return json.dumps(data)


@apiRoute.route('/diseases', methods=["GET"])
# @csrf.exempt
def diseases():
	diseases = get_diseases()
	return json.dumps(diseases)


@apiRoute.route('/job/api', methods=["GET"])
# @csrf.exempt
def jobApi():
	"""
	json of job information
	:return: json object
	"""
	user_id = User.query.filter_by(username='admin').first().id
	jobs = Job.query.filter(Job.user_id == user_id)
	jobList = []
	for job in jobs:
		jobList.append([job.id, job.name, STATUS[job.status], job.disease_name, job.gdc_project_id,
						job.mutation_gene, job.site, 'details'])
	data = {"data": jobList}
	return json.dumps(data)
