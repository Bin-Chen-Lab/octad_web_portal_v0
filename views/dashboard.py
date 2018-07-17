import subprocess, requests
from datetime import datetime
from os import walk, makedirs, chmod
from os.path import join, splitext, exists, dirname
from app import app, before_request, db
from flask import Blueprint, render_template, request, g, flash, session, url_for, redirect
from flask_login import login_user
from models.dashboard import FEATURES, get_sites, get_metastatics, get_grades, get_stages, Job, STATUS
from models.profile import User, generate_password, check_password
import json
from flask_login import login_required
rscript_path = app.config['RSCRIPT_PATH']
rdir_path = app.config['RREPO_PATH']
r_output = app.config['RREPO_OUTPUT']

dashboardRoute = Blueprint('dashboard', __name__)
dashboardRoute.before_request(before_request)


@dashboardRoute.route('/dataset', methods=["GET"])
# @login_required
def dataset():
    """
    Static page displayed
    """
    return render_template('dashboard/dataset.html')


@dashboardRoute.route('/code', methods=["GET"])
# @login_required
def code():
    """
    Static page displayed
    """
    return render_template('dashboard/code.html')


@dashboardRoute.route('/tutorials', methods=["GET"])
# @login_required
def tutorials():
    """
    Static page displayed
    """
    return render_template('dashboard/tutorials.html')


@dashboardRoute.route('/faq', methods=["GET"])
# @login_required
def faq():
    """
    Static page displayed
    """
    return render_template('dashboard/faq.html')


@dashboardRoute.route('/news', methods=["GET"])
# @login_required
def news():
    """
    Static page displayed
    """
    return render_template('dashboard/news.html')


@dashboardRoute.route('/', methods=["GET"])
# @login_required
def dashboard():
    job_type = request.args.get('rerun', False)
    job_id = request.args.get('job_id', '')
    if job_id and job_type == 'true':
        job = Job.query.filter(Job.id == job_id).first()
    else:
        job = None
    sites = get_sites()
    metastatics = get_metastatics()
    grades = get_grades()
    stages = get_stages()
    return render_template('dashboard/dashboard.html', features=FEATURES, sites=sites,
                           metastatics=metastatics, grades=grades, stages=stages, job=job)


@dashboardRoute.route('/output/<job_id>', methods=["GET"])
@login_required
def job_output(job_id):
    """
    IF job status is complete then only job is displayed else page is not accessible
    :param job_id:
    :return:
    """
    job = Job.query.filter(Job.id == job_id).first()
    file_name = job.name.replace(' ', '_') + '.zip'
    if job.status < 6:
        return redirect(url_for('dashboard.job_history'))
    return render_template('dashboard/output.html', job=job, file_name=file_name)


@dashboardRoute.route('/job/save', methods=["POST"])
# @login_required
def save_job():
    job_id = request.form.get('job_id', None)
    if job_id < 0 or job_id == '':
        job_id = Job.get_new_id()
    job = Job.query.filter(Job.id == job_id).first()
    if job:
        job_name = request.form.get('jobName', None)
        description = request.form.get('description', None)
        disease_name = request.form.get('case_disease_name', None)
        case_sample_id = request.form.get('case_samples', None)
        case_tissue_type = request.form.getlist('case_type', None)
        case_tissue_type = ','.join(case_tissue_type) if case_tissue_type else ''
        case_site = request.form.get('case_site', None)
        case_gender = request.form.get('case_gender', None)
        case_metastatic_site = request.form.get('case_metastatic', None)
        case_EGFR = request.form.get('case_EGFR', None)
        case_IDH1 = request.form.get('case_IDH1', None)
        case_IDH2 = request.form.get('case_IDH2', None)
        case_TP53 = request.form.get('case_TP53', None)
        ctrl_sample_id = request.form.get('control_samples', None)
        case_age_in_year = request.form.get('case_age', None)
        case_tumor_grade = request.form.get('case_tumor_grade', None)
        case_tumor_stage = request.form.getlist('case_tumor_stage', None)
        case_tumor_stage = ','.join(case_tumor_stage) if case_tumor_stage else ''
        ctrl_tissue_type = request.form.getlist('control_type', None)
        ctrl_tissue_type = ','.join(ctrl_tissue_type) if ctrl_tissue_type else ''
        ctrl_site = request.form.get('control_site', None)
        ctrl_gender = request.form.get('control_gender', None)
        ctrl_metastatic_site = request.form.get('control_metastatic', None)
        ctrl_EGFR = request.form.get('control_EGFR', None)
        ctrl_IDH1 = request.form.get('control_IDH1', None)
        ctrl_IDH2 = request.form.get('control_IDH2', None)
        ctrl_TP53 = request.form.get('control_TP53', None)
        ctrl_age_in_year = request.form.get('control_age', None)
        ctrl_tumor_grade = request.form.get('control_tumor_grade', None)
        ctrl_tumor_stage = request.form.getlist('control_tumor_stage', None)
        ctrl_tumor_stage = ','.join(ctrl_tumor_stage) if ctrl_tumor_stage else ''
        de_method = request.form.get('de_method', None)
        dz_fc_threshold = request.form.get('dz_fc_threshold', None)
        dz_p_threshold = request.form.get('dz_p_threshold', None)
        database = request.form.get('database', None)
        choose_fda_drugs = request.form.get('choose_fda_drugs', 'T')
        if database == 'lincs_db':
            max_gene_size = request.form.get('lincs_max_genes', 50)
        else:
            max_gene_size = request.form.get('cmap_max_genes', 150)
        landmark = request.form.get('landmark', 1)
        weight_cell_line = request.form.get('weight_cell_line', 'F')
        debug = request.form.get('debug', 'T')
        finishInfo = request.form.get('finishInfo', None)
        next_url = request.form.get('next_url', None)
        jobDetails = job.jobs[0]
        if not g.user:
            username = request.form['email']
            password = request.form['password']
            registered_user = User.query.filter_by(username=username).first()
            if registered_user is None:
                hashedPasswd = generate_password(password)
                registered_user = User(username, hashedPasswd, 0, True)
                registered_user.save()
            elif not check_password(registered_user.password, password):
                result = {"message": "Invalid credentials", "category": "error"}
                return json.dumps(result)
            if login_user(registered_user, remember=True):
                session['user_id'] = registered_user.id
                registered_user.update(commit=False, loginTime=datetime.utcnow())
                g.user = registered_user
                job.update(commit=False, user_id=registered_user.id, name=job_name, description=description, is_save=True)
                db.session.commit()
            else:
                result = {"message": "User is unable to logged in so can't create job", "category": "error"}
                return json.dumps(result)
        else:
            job.update(commit=False, name=job_name, description=description, is_save=True)
            db.session.commit()
        result = {"message": "Job saved successfully", "category": "success", "finishInfo": finishInfo}
        # Storing Job details
        jobDetails.update(commit=True, disease_name=disease_name, case_tissue_type=case_tissue_type,
                          case_site=case_site, case_gender=case_gender, case_metastatic_site=case_metastatic_site,
                          case_EGFR=case_EGFR if case_EGFR else None, case_IDH1=case_IDH1 if case_IDH1 else None,
                          case_IDH2=case_IDH2 if case_IDH2 else None, case_TP53=case_TP53 if case_TP53 else None,
                          case_age_in_year=case_age_in_year, case_tumor_grade=case_tumor_grade,
                          case_tumor_stage=case_tumor_stage, ctrl_tissue_type=ctrl_tissue_type,
                          ctrl_site=ctrl_site, ctrl_gender=ctrl_gender, ctrl_metastatic_site=ctrl_metastatic_site,
                          ctrl_EGFR=ctrl_EGFR if ctrl_EGFR else None, ctrl_IDH1=ctrl_IDH1 if ctrl_IDH1 else None,
                          ctrl_IDH2=ctrl_IDH2 if ctrl_IDH2 else None, ctrl_TP53=ctrl_TP53 if ctrl_TP53 else None,
                          ctrl_age_in_year=ctrl_age_in_year, ctrl_tumor_grade=ctrl_tumor_grade,
                          ctrl_tumor_stage=ctrl_tumor_stage, de_method=de_method, dz_fc_threshold=dz_fc_threshold,
                          dz_p_threshold=dz_p_threshold, database=database, choose_fda_drugs=choose_fda_drugs,
                          max_gene_size=max_gene_size, landmark=landmark, weight_cell_line=weight_cell_line,
                          debug=debug, case_sample_id=case_sample_id, ctrl_sample_id=ctrl_sample_id)
        if finishInfo == 'true':
            # Added following because it is not working fine with ui field
            choose_fda_drugs = 'T'
            max_gene_size = 50
            landmark = 1
            weight_cell_line = 'F'
            debug = 'T'
            if job.status < 4 and not de_method:
                result = {"message": "Invalid DE method. Please select on signature page", "category": "error"}
                return json.dumps(result)
            elif job.status == 4:
                cmd = [rscript_path, rdir_path + 'drug_predict.R', str(job_id), choose_fda_drugs, str(max_gene_size),
                       str(landmark), weight_cell_line, debug]
            elif job.status == 3:
                cmd = [rscript_path, rdir_path + 'compute_drug_predict.R', str(job_id), choose_fda_drugs,
                       str(max_gene_size), str(landmark), weight_cell_line, debug, de_method, dz_fc_threshold,
                       dz_p_threshold]
            else:
                result = {"message": "Please try again. Unable to create job", "category": "error"}
                return json.dumps(result)
            print cmd
            try:
                x = subprocess.Popen(cmd)
                job.update(commit=False, status=5)
                db.session.commit()
            except Exception as e:
                pass
        result.update(next_url=next_url)
        return json.dumps(result)
    else:
        result = {"message": "Invalid data please generate job again", "category": "error"}
        return json.dumps(result)


@dashboardRoute.route('/job_history', methods=["GET"])
@login_required
def job_history():
    # Do some stuff
    return render_template('dashboard/job.html')


@dashboardRoute.route('/chart', methods=["GET"])
# @login_required
def chart():
    filename = app.config['APPLICATION_ROOT'] + '/static/js/rc_two_cats.txt'
    upload_url = 'http://amp.pharm.mssm.edu/clustergrammer/matrix_upload/'
    r = requests.post(upload_url, files={'file': open(filename, 'rb')})
    link = r.text

    return render_template('dashboard/chart.html', xw=link)


@dashboardRoute.route('/job/case/<disease>', methods=["POST"])
# @login_required
def job_case(disease):
    """
    Running R script for job
    :return: json object
    """
    data = request.get_json(force=True)
    print data
    job_id = data.get('job_id', None)
    if not job_id:
        job_id = str(Job.get_new_id())
    cmd = [rscript_path, rdir_path + 'case.R', job_id, disease]
    print cmd
    # check_output will run the command and store to result
    try:
        x = subprocess.check_output(cmd, universal_newlines=True)
        job = Job.query.filter(Job.id == job_id).first()
        job.update(commit=True, status=2)
        file_name = x.replace('[1] "', '')
        file_name = file_name.replace('"', '')
        file_name = file_name.replace('\n', '')
    except Exception as e:
        print e
        return json.dumps(dict(job_id=job_id, file_name="fail"))
    print 'The maximum of the numbers is:', file_name
    return json.dumps(dict(job_id=job_id, file_name=file_name))


@dashboardRoute.route('/job/compute', methods=["POST"])
# @login_required
def job_compute():
    """
    Running R script for job control visualization
    :return: json object
    """
    if request.method == 'POST':
        data = request.get_json(force=True)
        try:
            job_id = data.get('job_id')
            de_method = data.get('de_method')
            dz_p_threshold = data.get('dz_p_threshold', 0.001)
            dz_fc_threshold = data.get('dz_fc_threshold', 2)
            case_str = data.get('case_str', '')
            control_str = data.get('control_str', '')
            job = Job.query.filter(Job.id == job_id).first()
            job.jobs[0].update(commit=True, de_method=de_method, dz_fc_threshold=dz_fc_threshold,
                               dz_p_threshold=dz_p_threshold, case_sample_id=case_str, ctrl_sample_id=control_str)
        except Exception as e:
            print e
            return json.dumps("fail")
        case_path = r_output + job_id + '/case_ids.txt'
        control_path = r_output + job_id + '/control_ids.txt'
        case_ids = case_str.split(',')
        control_ids = control_str.split(',')
        print len(case_ids)
        if not exists(dirname(case_path)):
            try:
                makedirs(dirname(case_path))
            except OSError as exc:  # Guard against race condition
                print str(exc)
                return "fail"
        with open(case_path, "w") as f:
            for case in case_ids:
                f.write(case.replace('.', '-') + '\n')
            f.close()
        with open(control_path, "w") as f:
            for control in control_ids:
                f.write(control.replace('.', '-') + '\n')
            f.close()
        cmd = [rscript_path, rdir_path + 'compute.R', job_id, case_path, control_path, de_method, dz_fc_threshold,
               dz_p_threshold]
        print cmd
        # check_output will run the command and store to result
        try:
            x = subprocess.check_output(cmd, universal_newlines=True)
            file_path = '/static/data/' + job_id + '/'
            pdf_path = app.config['APPLICATION_ROOT'] + file_path
            pdfs = []
            for dirPath, dirNames, fileNames in walk(pdf_path):
                pdfs.extend([join(file_path, fileName) for fileName in fileNames if fileName.startswith('dz_enriched_')
                             and splitext(fileName)[1].lower() in ['.pdf']])
            job.update(commit=True, status=4)
            data = {'signature': file_path + 'signature.pdf',
                    'enricher': pdfs}
        except Exception as e:
            print e
            return json.dumps("fail")
        return json.dumps(data)

