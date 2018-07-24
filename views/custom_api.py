import json, subprocess
from os import walk, makedirs
from os.path import join, splitext, exists, relpath, dirname
import collections
from datetime import datetime
from flask import Blueprint, request, render_template, url_for
from app import app
from models.dashboard import get_diseases, Samples, Job, STATUS, get_sites, get_metastatics, get_grades, get_stages, get_tissue_types, get_gender, get_EGFR, get_IDH1, get_IDH2, get_TP53
from zipfile import ZipFile, ZIP_DEFLATED
from custom_email import send_email
from sqlalchemy import or_
rscript_path = app.config['RSCRIPT_PATH']
rdir_path = app.config['RREPO_PATH']
r_output = app.config['RREPO_OUTPUT']
base_url = app.config['BASE_URL']

apiRoute = Blueprint('api', __name__)


@apiRoute.route('/sample/api', methods=["POST"])
# @csrf.exempt
def sampleApi():
	"""
	json of job information
	:return: json object
	"""
	filter_str = []
	if request.method == 'POST':
		data = request.get_json(force=True)
		job_id = data.get('job_id', None)
		if job_id:
			job = Job.query.filter(Job.id==job_id).first()
			case_ids = [case for case in job.jobs[0].case_sample_id.split(',') if job and job.jobs[0].case_sample_id]
			if not case_ids:
				case_path = r_output + job_id + '/case_ids.txt'
				with open(case_path, "r") as f:
					for case in f.readlines():
						case_ids.append(case.replace('-', '.').replace('\n', ''))
				f.close()
			filter_str.append(Samples.sample_id.in_(case_ids))
		else:
			for feature in data:
				if feature == 'disease_name':
					disease_name = data['disease_name'].strip()
					filter_str.append(Samples.cancer == disease_name)
				elif feature == 'tissue_type':
					tissue_type = data['tissue_type'] # ['primary', 'secoundry']
					filter_str.append(or_(Samples.tissue_type.in_(tissue_type)))
				elif feature == 'site':
					site = data['site']
					filter_str.append(Samples.site == site)
				elif feature == 'gender':
					gender = data['gender']
					filter_str.append(Samples.gender == gender)
				elif feature == 'metastatic':
					metastatic = data['metastatic']
					filter_str.append(Samples.metastatic_site == metastatic)
				elif feature == 'EGFR':
					EGFR = data['EGFR']
					if not EGFR:
						filter_str.append(or_(Samples.EGFR == EGFR, Samples.EGFR == 'NA'))
					else:
						filter_str.append(Samples.EGFR == EGFR)
				elif feature == 'IDH1':
					IDH1 = data['IDH1']
					if not IDH1:
						filter_str.append(or_(Samples.IDH1 == IDH1, Samples.IDH1 == 'NA'))
					else:
						filter_str.append(Samples.IDH1 == IDH1)
				elif feature == 'IDH2':
					IDH2 = data['IDH2']
					if not IDH2:
						filter_str.append(or_(Samples.IDH2 == IDH2, Samples.IDH2 == 'NA'))
					else:
						filter_str.append(Samples.IDH2 == IDH2)
				elif feature == 'TP53':
					TP53 = data['TP53']
					if not TP53:
						filter_str.append(or_(Samples.TP53 == TP53, Samples.TP53 == 'NA'))
					else:
						filter_str.append(Samples.TP53 == TP53)
				elif feature == 'age':
					age_range = data['age'].split('-')
					start = int(age_range[0].strip())
					end = int(age_range[1].strip())
					filter_str.append(Samples.age_in_year.between(start, end))
				elif feature == 'tumour_geade':
					tumor_grade = data['tumour_geade']
					filter_str.append(Samples.tumor_grade == tumor_grade)
				elif feature == 'tumour_stage':
					tumour_stage = data['tumour_stage']
					filter_str.append(or_(Samples.tumor_stage.in_(tumour_stage)))

	# print "$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$", filter_str
	samples = Samples.query.filter(*filter_str).all()
	# samples = Samples.query.filter().all()[:10]
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
		d['egfr'] = sample.EGFR
		d['idh1'] = sample.IDH1
		d['idh2'] = sample.IDH2
		d['tp53'] = sample.TP53
		d['tumor_grade'] = sample.tumor_grade
		d['tumor_stage'] = sample.tumor_stage
		sampleList.append(d)
	print "SSSSSSSSSSSSSSSSS", len(sampleList)
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
		job_id = data['job_id']
		job = Job.query.filter(Job.id == job_id).first()
		file_name = data['file_name']
		if not file_name:
			control_ids = [control for control in job.jobs[0].ctrl_sample_id.split(',') if job and job.jobs[0].ctrl_sample_id]
			if not control_ids:
				control_path = r_output + job_id + '/control_ids.txt'
				with open(control_path, "r") as f:
					for control in f.readlines():
						control_ids.append(control.replace('-', '.').replace('\n', ''))
				f.close()
			samples = Samples.query.filter(Samples.sample_id.in_(control_ids)).all()
			site = job.jobs[0].ctrl_site

		else:
			file_path = join(app.config['RREPO_OUTPUT'], str(job_id), file_name)
			f = open(file_path, 'r')
			lines = f.readlines()
			site = lines[0].replace('\n', '')
			control_id = [line.replace('\n', '') for line in lines[1:]] #remove .replace('-', '.')...new format of id
			samples = Samples.query.filter(Samples.sample_id.in_(control_id)).all()
			#site = site.split("-")[0].replace(' ', '').upper()
			job.jobs[0].update(commit=True, ctrl_site=site)


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


@apiRoute.route('/job/api/<user_id>', methods=["GET"])
# @csrf.exempt
def userJobApi(user_id):
	"""
	json of job information
	:return: json object
	"""
	jobs = Job.query.filter(Job.user_id == user_id, Job.is_save == True).order_by(Job.id.desc()).all()
	jobs_list = []
	for job in jobs:
		d = dict()
		d['id'] = job.id
		d['job_name'] = job.name
		d['disease'] = job.jobs[0].disease_name
		d['status'] = STATUS[job.status]
		jobs_list.append(d)
	return json.dumps(jobs_list)


@apiRoute.route('/job/status', methods=["GET"])
# @csrf.exempt
def jobStatus():
	"""
	json of job information
	:return: json object
	"""

	jobs = Job.query.filter(Job.status <= 5).all()
	# jobs = Job.query.filter(Job.status == 6).all()
	for job in jobs:
		job_id = job.id
		if job.status <= 5 and (job.is_save == 0 or not job.is_save) and job.creationTime.date() < datetime.utcnow().date():
			# Removed unwanted jobs
			if job.jobs: job.jobs[0].delete(commit=True)
			job.delete(commit=True)
		elif check_pdf(job_id):
			job.update(commit=True, status=6)
			file_folder = join(app.config['RREPO_OUTPUT'], str(job.id))
			file_name = job.name.replace(' ', '_') + '.zip'
			file_path = join(file_folder, file_name)
			if not exists(file_path):
				fantasy_zip = ZipFile(file_path, 'w')
				for folder, subfolders, files in walk(file_folder):
					for file in files:
						if file.endswith('.pdf') or file.endswith('.csv'):
							fantasy_zip.write(join(folder, file),
											  relpath(join(folder, file), file_folder),
											  compress_type=ZIP_DEFLATED)
				fantasy_zip.close()
				job_url = base_url + url_for('dashboard.job_output', job_id=job.id)
				subject = "OCTAD: %s Status" % job.name
				text = ""
				html = render_template('emails/job_status.html', job=job, job_url=job_url)
				send_email(job.userDetails.username, subject, text, html)

	return json.dumps("script completed")


def check_pdf(job_id):
	stat_path = app.config['APPLICATION_ROOT'] + '/static/data/' + str(job_id) + '/'
	flag = False
	for root, dirs, files in walk(stat_path):
		for file in files:
			if file.startswith("drug_enriched"):
				flag = True
	return flag


@apiRoute.route('/job/rerun', methods=["GET"])
# @csrf.exempt
def jobRerun():
	"""
	json of job information
	:return: json object
	"""

	jobs = Job.query.filter(Job.status == 5).all()
	for job in jobs:
		cmd = [rscript_path, rdir_path + 'drug_predict.R', str(job.id), 'T', str(50), str(1), 'F', 'T']
		x = subprocess.Popen(cmd)


@apiRoute.route('/job/signature', methods=['POST'])
# @csrf.exempt
def signatureData():
	"""
	On the basis of job_id signature related files given in list
	:param job_id:
	:return: list of file names
	"""
	outdata = {}
	data = request.get_json(force=True)
	job_id = data.get('job_id', None)
	job = Job.query.filter(Job.id == job_id).first() if job_id else None
	if job:
		file_path = '/static/data/' + job_id + '/'
		pdf_path = app.config['APPLICATION_ROOT'] + file_path
		pdfs = []
		for dirPath, dirNames, fileNames in walk(pdf_path):
			pdfs.extend([join(file_path, fileName) for fileName in fileNames if fileName.startswith('dz_enriched_')
						 and splitext(fileName)[1].lower() in ['.pdf']])
		outdata = {'signature': file_path + 'signature.pdf',
				'enricher': pdfs}
	return json.dumps(outdata)


@apiRoute.route('/get_casefeature_by_disease', methods=["POST"])
# @csrf.exempt
def get_casefeature_by_disease():
	data = request.get_json(force=True)
	print data
	disease = data.get('disease', None)
	tissue_type = data.get('tissue_type', None)
	site = data.get('site', None)
	gender = data.get('gender', None)
	metastatic = data.get('metastatic', None)
	egfr = data.get('egfr', None)
	idh1 = data.get('idh1', None)
	idh2 = data.get('idh2', None)
	tp53 = data.get('tp53', None)
	age = data.get('tp53', None)
	tumor_grade = data.get('tumor_grade', None)
	tumor_stage = data.get('tumor_stage', None)
	print disease
	sites_list = get_sites(disease, tissue_type, gender, metastatic, egfr, idh1, idh2, tp53, age, tumor_grade, tumor_stage)
	metastatics_list = get_metastatics(disease, tissue_type, site, gender, egfr, idh1, idh2, tp53, age, tumor_grade, tumor_stage)
	grades_list = get_grades(disease, tissue_type, site, gender, metastatic, egfr, idh1, idh2, tp53, age, tumor_stage)
	stages_list = get_stages(disease, tissue_type, site, gender, metastatic, egfr, idh1, idh2, tp53, age, tumor_grade)
	tissue_types_list = get_tissue_types(disease, site, gender, metastatic, egfr, idh1, idh2, tp53, age, tumor_grade, tumor_stage)
	gender_list = get_gender(disease, tissue_type, site, metastatic, egfr, idh1, idh2, tp53, age, tumor_grade, tumor_stage)
	egfr_list = get_EGFR(disease, tissue_type, site, gender, metastatic, idh1, idh2, tp53, age, tumor_grade, tumor_stage)
	idh1_list = get_IDH1(disease, tissue_type, site, gender, metastatic, egfr, idh2, tp53, age, tumor_grade, tumor_stage)
	idh2_list = get_IDH2(disease, tissue_type, site, gender, metastatic, egfr, idh1, tp53, age, tumor_grade, tumor_stage)
	tp53_list = get_TP53(disease, tissue_type, site, gender, metastatic, egfr, idh1, idh2, age, tumor_grade, tumor_stage)
	outdata = dict(sites=sites_list, metastatics=metastatics_list, grades=grades_list, stages=stages_list, tissue_types=tissue_types_list, gender=gender_list, 
		egfr=egfr_list, idh1=idh1_list, idh2=idh2_list, tp53=tp53_list)
	print outdata
	return json.dumps(outdata)
