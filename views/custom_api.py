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
from models.dashboard import FEATURES
from sqlalchemy import or_
from models.base import db
import pandas as pd
import numpy as np
rscript_path = app.config['RSCRIPT_PATH']
rdir_path = app.config['RREPO_PATH']
r_output = app.config['RREPO_OUTPUT']
base_url = app.config['BASE_URL']

apiRoute = Blueprint('api', __name__)


@apiRoute.route('/sample/api1', methods=["GET"])
# @csrf.exempt
def sampleApi1():
	"""
	json of job information
	:return: json object
	"""
	samples = Samples.query.filter().all()
	sampleList = []
	for sample in samples:
		d = [sample.id, sample.id, sample.sample_id, sample.tissue_type, sample.age_in_year, sample.site,
			 sample.gender, sample.metastatic_site, sample.cancer, sample.EGFR, sample.IDH1, sample.IDH2,
			 sample.TP53, sample.tumor_grade, sample.tumor_stage]
		sampleList.append(d)
	return json.dumps({"data": sampleList})


# @apiRoute.route('/sample/control/api', methods=["POST"])
# # @csrf.exempt
# def controlSampleApi():
# 	"""
# 	json of job information
# 	:return: json object
# 	"""
# 	site = ''
# 	sample_list = []
# 	if request.method == 'POST':
# 		data = request.get_json(force=True)
# 		job_id = data['job_id']
# 		job = Job.query.filter(Job.id == job_id).first()
# 		file_name = data['file_name']
# 		if not file_name:
# 			control_ids = [control for control in job.jobs[0].ctrl_sample_id.split(',') if job and job.jobs[0].ctrl_sample_id]
# 			if not control_ids:
# 				control_path = r_output + job_id + '/control_ids.txt'
# 				with open(control_path, "r") as f:
# 					for control in f.readlines():
# 						control_ids.append(control.replace('\n', ''))
# 				f.close()
# 			samples = Samples.query.filter(Samples.sample_id.in_(control_ids)).all()
# 			site = job.jobs[0].ctrl_site
# 		else:
# 			file_path = join(app.config['RREPO_OUTPUT'], str(job_id), file_name)
# 			f = open(file_path, 'r')
# 			lines = f.readlines()
# 			site = lines[0].replace('\n', '')
# 			control_id = [line.replace('\n', '') for line in lines[1:]]
# 			samples = Samples.query.filter(Samples.sample_id.in_(control_id)).all()
# 			job.jobs[0].update(commit=True, ctrl_site=site)
# 		for sample in samples:
# 			d = collections.OrderedDict()
# 			d['id'] = sample.id
# 			d['sample_id'] = sample.sample_id
# 			d['tissue_type'] = sample.tissue_type
# 			d['age_in_year'] = sample.age_in_year
# 			d['site'] = sample.site
# 			d['gender'] = sample.gender
# 			d['metastatic_site'] = sample.metastatic_site
# 			d['cancer'] = sample.cancer
# 			d['egfr'] = 1 if sample.EGFR else 0
# 			d['idh1'] = 1 if sample.IDH1 else 0
# 			d['idh2'] = 1 if sample.IDH2 else 0
# 			d['tp53'] = 1 if sample.TP53 else 0
# 			d['tumor_grade'] = sample.tumor_grade
# 			d['tumor_stage'] = sample.tumor_stage
# 			sample_list.append(d)
# 	data = {"site": site, "samples": sample_list}
# 	return json.dumps(data)


@apiRoute.route('/sample/control/api1', methods=["POST"])
# @csrf.exempt
def controlSampleApi1():
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
						control_ids.append(control.replace('\n', ''))
				f.close()
			samples = Samples.query.filter(Samples.sample_id.in_(control_ids)).all()
			site = job.jobs[0].ctrl_site
		else:
			file_path = join(app.config['RREPO_OUTPUT'], str(job_id), file_name)
			f = open(file_path, 'r')
			lines = f.readlines()
			site = lines[0].replace('\n', '')
			control_id = [line.replace('\n', '') for line in lines[1:]]
                        print control_id
			samples = Samples.query.filter(Samples.sample_id.in_(control_id)).all()
			job.jobs[0].update(commit=True, ctrl_site=site)
		for sample in samples:
			d = [sample.id, sample.id, sample.sample_id, sample.tissue_type, sample.age_in_year, sample.site,
				 sample.gender, sample.metastatic_site, sample.cancer, sample.EGFR, sample.IDH1, sample.IDH2,
				 sample.TP53, sample.tumor_grade, sample.tumor_stage]
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
	jobs = Job.query.filter(Job.user_id == user_id, Job.is_save == True).order_by(Job.creationTime.desc()).all()
	jobs_list = []
	for job in jobs:
		d = dict()
		d['id'] = job.id
		d['job_name'] = job.name
		d['disease'] = job.jobs[0].disease_name
		d['status'] = STATUS[job.status]
		d['creationTime'] = str(job.creationTime)
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
	return json.dumps(outdata)


@apiRoute.route('/case_plot', methods=["POST"])
# @csrf.exempt
def case_plot():
	data = request.get_json(force=True)
	case_str = data.get('cases', None)
	if case_str:
		case_ids = [i for i in case_str.split(',')]
	else:
		case_ids = []
	csv_file = app.config['APPLICATION_ROOT'] + '/static/data_files/tsne_3d.csv'
	df = pd.read_csv(csv_file)
	others = {
		"x": list(df.X.values),
		"y": list(df.Y.values),
		"mode": 'markers',
		"type": 'scatter',
		"name": 'Other',
		"text": list(df.name.values)
	}
	if case_ids:
		odf = df.loc[df['Unnamed: 0'].isin(case_ids)]
		x = list(odf.X.values)
		y = list(odf.Y.values)
		texts = list(odf.name.values)
	else:
		x = []
		y = []
		texts = []
	cases = {
		"x": x,
		"y": y,
		"mode": 'markers',
		"type": 'scatter',
		"name": 'Case',
		"text": texts
	}
	layout = {"title": 'Case Visualization', "showlegend": True}
	graph_data = [others, cases]
	return json.dumps(dict(graph_data=graph_data, layout=layout))


@apiRoute.route('/control_plot', methods=["POST"])
# @csrf.exempt
def control_plot():
	data = request.get_json(force=True)
	case_str = data.get('cases', None)
	control_str = data.get('controls', None)
	if case_str:
		case_ids = [i for i in case_str.split(',')]
	else:
		case_ids = []
	if control_str:
		control_ids = [j for j in control_str.split(',')]
	else:
		control_ids = []
	csv_file = app.config['APPLICATION_ROOT'] + '/static/data_files/tsne_3d.csv'
	df = pd.read_csv(csv_file)
	others = {
		"x": list(df.X.values),
		"y": list(df.Y.values),
		"mode": 'markers',
		"type": 'scatter',
		"name": 'Other',
		"text": list(df.name.values)
	}
	if case_ids:
		odf = df.loc[df['Unnamed: 0'].isin(case_ids)]
		cx = list(odf.X.values)
		cy = list(odf.Y.values)
		ctexts = list(odf.name.values)
	else:
		cx = []
		cy = []
		ctexts = []
	if control_ids:
		odf = df.loc[df['Unnamed: 0'].isin(control_ids)]
		ctx = list(odf.X.values)
		cty = list(odf.Y.values)
		cttexts = list(odf.name.values)
	else:
		ctx = []
		cty = []
		cttexts = []
	cases = {
		"x": cx,
		"y": cy,
		"mode": 'markers',
		"type": 'scatter',
		"name": 'Case',
		"text": ctexts
	}
	controls = {
		"x": ctx,
		"y": cty,
		"mode": 'markers',
		"type": 'scatter',
		"name": 'Control',
		"text": cttexts
	}
	layout = {"title": 'Case Control Visualization', "showlegend": True}
	graph_data = [others, cases, controls]
	return json.dumps(dict(graph_data=graph_data, layout=layout))


@apiRoute.route('/output/drug_hit/<job_id>', methods=['GET'])
# @csrf.exempt
def drug_hit(job_id):
	"""
	On the basis of job_id drug_hits data in json format
	:param job_id:
	:return: list of csv data
	"""
	job = Job.query.filter(Job.id == job_id).first() if job_id else None
	drug_hits_csv_data = []
	if job:
		file_path = '/static/data/' + job_id + '/'
		pdf_path = app.config['APPLICATION_ROOT'] + file_path
		drug_hits_csv_file = "".join([pdf_path, 'sRGES_drug.csv'])
		if exists(drug_hits_csv_file):
			df = pd.read_csv(drug_hits_csv_file, index_col=False, dtype={"sRGES": str})
			csv_df = df[["pert_iname", "clinical_phase", "moa", "target", "sRGES"]]
			csv_df1 = csv_df.replace(np.nan, '', regex=True)
			drug_hits_csv_data = csv_df1.values.tolist()
	return json.dumps({"data": drug_hits_csv_data})


@apiRoute.route('/output/dz_predict/<job_id>', methods=['GET'])
# @csrf.exempt
def disease_predict(job_id):
	"""
	On the basis of job_id drug_hits data in json format
	:param job_id:
	:return: list of csv data
	"""
	job = Job.query.filter(Job.id == job_id).first() if job_id else None
	disease_predict_csv_data = []
	if job:
		file_path = '/static/data/' + job_id + '/'
		pdf_path = app.config['APPLICATION_ROOT'] + file_path
		disease_predict_csv_file = "".join([pdf_path, 'dz_sig.csv'])
		if exists(disease_predict_csv_file):
			df = pd.read_csv(disease_predict_csv_file, index_col=False)
			csv_df = df[["identifier", "gene", "GeneID", "log2FoldChange", "padj", "name"]]
			csv_df1 = csv_df.replace(np.nan, '', regex=True)
			disease_predict_csv_data = csv_df1.values.tolist()
	return json.dumps({"data": disease_predict_csv_data})