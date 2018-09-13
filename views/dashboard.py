import subprocess, requests
from os import walk, makedirs
from os.path import join, splitext, exists, dirname
from app import app, before_request
from flask import Blueprint, render_template, request
from models.dashboard import FEATURES, get_sites, get_metastatics, get_grades, get_stages, Job
import json

dashboardRoute = Blueprint('dashboard', __name__)
dashboardRoute.before_request(before_request)


@dashboardRoute.route('/', methods=["GET"])
# @login_required
def dashboard():
    sites = get_sites()
    metastatics = get_metastatics()
    grades = get_grades()
    stages = get_stages()
    return render_template('dashboard/dashboard.html', features=FEATURES, sites=sites,
                           metastatics=metastatics, grades=grades, stages=stages)


@dashboardRoute.route('/output', methods=["GET"])
# @login_required
def job_output():

    return render_template('dashboard/output.html')


@dashboardRoute.route('/job', methods=["GET"])
# @login_required
def job():
    # Do some stuff
    return render_template('dashboard/dashboard_old.html')


@dashboardRoute.route('/job_history', methods=["GET"])
# @login_required
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


@dashboardRoute.route('/job/case/<job_id>/<disease>', methods=["GET"])
# @login_required
def job_case(job_id, disease):
    """
    Running R script for job
    :return: json object
    """
    rscript_path = app.config['RSCRIPT_PATH']
    rdir_path = app.config['RREPO_PATH']
    cmd = [rscript_path, rdir_path + 'case.R', job_id, disease]
    print cmd
    # check_output will run the command and store to result
    try:
        x = subprocess.check_output(cmd, universal_newlines=True)
        file_name = x.replace('[1] "', '')
        file_name = file_name.replace('"', '')
        file_name = file_name.replace('\n', '')
    except Exception as e:
        print e
        return "fail"
    print 'The maximum of the numbers is:', file_name
    return file_name


@dashboardRoute.route('/job/case/visualization', methods=["POST"])
# @login_required
def job_case_visualize():
    """
    Running R script for job case visualization
    :return: json object
    """
    if request.method == 'POST':
        data = request.get_json(force=True)
        job_id = data.get('job_id', None)
        job_id = job_id if job_id else str(Job.get_new_id())
        case_path = app.config['RREPO_OUTPUT'] + '' + job_id + '/case_ids.txt'
        rscript_path = app.config['RSCRIPT_PATH']
        rdir_path = app.config['RREPO_PATH']
        case_str = data['case_id']
        case_ids = case_str.split(',')
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
        cmd = [rscript_path, rdir_path + 'case_visualize.R', job_id, case_path]
        print cmd
        # check_output will run the command and store to result
        try:
            x = subprocess.check_output(cmd, universal_newlines=True)
            print x
        except Exception as e:
            print e
            return json.dumps([job_id, "fail"])
        return json.dumps([job_id, '/static/data/' + job_id + '/case.pdf'])


@dashboardRoute.route('/job/control/visualization', methods=["POST"])
# @login_required
def job_control_visualize():
    """
    Running R script for job control visualization
    :return: json object
    """
    if request.method == 'POST':
        data = request.get_json(force=True)
        try:
            job_id = data.get('job_id')
        except Exception as e:
            print e
            return json.dumps("fail")
        case_path = app.config['RREPO_OUTPUT'] + '' + job_id + '/case_ids.txt'
        control_path = app.config['RREPO_OUTPUT'] + '' + job_id + '/control_ids.txt'
        rscript_path = app.config['RSCRIPT_PATH']
        rdir_path = app.config['RREPO_PATH']
        control_str = data['control_id']
        control_ids = control_str.split(',')
        if not exists(dirname(control_path)):
            try:
                makedirs(dirname(control_path))
            except OSError as exc:  # Guard against race condition
                print str(exc)
                return "fail"
        with open(control_path, "w") as f:
            for control in control_ids:
                f.write(control.replace('.', '-') + '\n')
            f.close()
        cmd = [rscript_path, rdir_path + 'control_visualize.R', job_id, case_path, control_path]
        print cmd
        # check_output will run the command and store to result
        try:
            x = subprocess.check_output(cmd, universal_newlines=True)
            print x
        except Exception as e:
            print e
            return json.dumps("fail")
        return json.dumps('/static/data/' + job_id + '/case_control.pdf')


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
        except Exception as e:
            print e
            return json.dumps("fail")
        case_path = app.config['RREPO_OUTPUT'] + '' + job_id + '/case_ids.txt'
        control_path = app.config['RREPO_OUTPUT'] + '' + job_id + '/control_ids.txt'
        rscript_path = app.config['RSCRIPT_PATH']
        rdir_path = app.config['RREPO_PATH']
        cmd = [rscript_path, rdir_path + 'compute.R', job_id, case_path, control_path, de_method]
        print cmd
        # check_output will run the command and store to result
        try:
            # x = subprocess.check_output(cmd, universal_newlines=True)
            # print x
            pdf_path = app.config['APPLICATION_ROOT'] + '/static/data/' + job_id + '/'
            pdfs = []
            for dirPath, dirNames, fileNames in walk(pdf_path):
                pdfs.extend([join(dirPath, fileName) for fileName in fileNames if fileName.startswith('dz_enriched_') and splitext(fileName)[1].lower() in ['.pdf']])
        except Exception as e:
            print e
            return json.dumps("fail")
        data = {'signature': '/static/data/' + job_id + '/signature.pdf',
                'enricher': pdfs}
        return json.dumps(data)

