from flask import render_template, url_for, flash, redirect, request, send_file
from app import app, db
from app.forms import TimeTrialForm, RunnerForm, TimeTrialResultForm, LoadAttending, LoadResults, LoginForm, PrintTimeTrial
from app.models import TimeTrial, Runner, TimeTrialResult
from src.time_trial import TimeTrialSpreadsheet, TimeTrialUtils
from werkzeug.utils import secure_filename
from werkzeug.exceptions import HTTPException, Forbidden
from flask_login import login_required, current_user, login_user, logout_user
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
import numpy as numpy
import os


@app.route('/')
@app.route('/index')
def index():
    current = TimeTrial.query.all()
    return render_template('index.html', title='Index', current=current)


@app.route('/time_trial', methods=['GET', 'POST'])
def time_trial():
    form = TimeTrialForm()
    if form.validate_on_submit():
        model = TimeTrial()
        form.populate_obj(model)
        db.session.add(model)
        db.session.commit()
        flash('Your changes have been saved.')
    elif request.args.get('remove'):
        tt = TimeTrial.query.filter_by(date=request.args.get('date')).first_or_404()
        db.session.delete(tt)
        db.session.commit()

    current = TimeTrial.query.all()
    breadcrumbs = [
        {'link': url_for('index'), 'text': 'Home', 'visible': True},
        {'text': 'Time Trials'}
    ]
    return render_template(
        'time_trial.html',
        title='Time Trial List',
        form=form,
        current=current,
        tables=[{'name': 'time-trial-list'}],
        breadcrumbs=breadcrumbs,
    )


@app.route('/runner/update/<username>', methods=['GET', 'POST'])
def runner_update(username):
    current_model = Runner.query.filter_by(username=username).first_or_404()
    results = current_model.results.order_by(TimeTrialResult.time_trial_id.asc())
    forms = {}
    if is_sys_admin or (current_user.is_authenticated and current_user.id == current_model.id):
        form_update = RunnerForm(obj=current_model)
        form_update.submit.label.text = 'Update'
        if form_update.validate_on_submit():
            form_update.populate_obj(current_model)
            db.session.commit()
            flash('Your changes have been saved.')
        forms['Update Runner'] = form_update
    # if is_admin:
    #     form_add_result = TimeTrialResultForm()
    #     if form_add_result.time.data and form_add_result.validate_on_submit():
    #         model = TimeTrialResult()
    #         form_add_result.populate_obj(model)
    #         # TODO work out why foreign keys need to be done like this.
    #         model.time_trial_id = model.time_trial_id.id
    #         model.runner_id = model.runner_id.id
    #         db.session.add(model)
    #         db.session.commit()
    #         flash('Your result has been added.')
    #     elif request.method == 'GET':
    #         form_add_result.runner_id.data = current_model
    #     forms['Add Runner Result'] = form_add_result
        breadcrumbs = [
        {'link': url_for('index'), 'text': 'Home', 'visible': True},
        {'link': url_for('runner'), 'text': 'Runners', 'visible': True},
        {'link': url_for('runner_result', username=username), 'text': 'View: '+str(current_model), 'visible': True},
        {'text': 'Update: '+str(current_model)}
    ]
    return render_template(
        'runner_results.html',
        title='Update Runner',
        forms=forms.items(),
        runner=current_model,
        results=results,
        tables=[{'name': 'time-trial-results-list'}],
        breadcrumbs=breadcrumbs,
    )


@app.route('/runner/view/<username>', methods=['GET', 'POST'])
def runner_result(username):
    current_model = Runner.query.filter_by(username=username).first_or_404()
    results = current_model.results.order_by(TimeTrialResult.time_trial_id.asc())
    url = make_graph(username, results)
    visible = current_user.is_authenticated and (current_user.level >= 2 or current_user.id == current_model.id)
    breadcrumbs = [
        {'link': url_for('index'), 'text': 'Home', 'visible': True},
        {'link': url_for('runner'), 'text': 'Runners', 'visible': True},
        {'link': url_for('runner_update', username=username), 'text': 'Update: '+str(current_model), 'visible': visible},
        {'text': 'View: '+str(current_model)}
    ]
    return render_template(
        'runner_results.html',
        title='View Runner',
        runner=current_model,
        results=results,
        tables=[{'name': 'time-trial-results-list'}],
        url=url,
        breadcrumbs=breadcrumbs,
    )


@app.route('/runner/delete/<username>', methods=['GET', 'POST'])
def runner_delete(username):
    current_model = Runner.query.filter_by(username=username).first_or_404()
    db.session.delete(current_model)
    db.session.commit()
    flash('Your changes have been saved.')
    return redirect(url_for('runner'))


@app.route('/runner', methods=['GET', 'POST'])
def runner():
    form = RunnerForm()
    form.active.data = 1
    form.gender.data = 'O'
    current = Runner.query.all()
    if form.validate_on_submit():
        model = Runner()
        form.populate_obj(model)
        username = model.first_name + '_' + model.last_name
        model.username = username.replace(' ', '_').lower()
        model.level = 1
        db.session.add(model)
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('runner'))

    breadcrumbs = [
        {'link': url_for('index'), 'text': 'Home', 'visible': True},
        {'text': 'Runners'}
    ]
    return render_template(
        'runner.html',
        title='Runners',
        form=form,
        current=current,
        tables = [{'name': 'runner-list'}],
        breadcrumbs=breadcrumbs,
    )


@app.route('/time_trial/view/<date>', methods=['GET', 'POST'])
def time_trial_result(date):
    current_model = TimeTrial.query.filter_by(date=date).first_or_404()
    form = TimeTrialResultForm()
    if form.validate_on_submit():
        model = TimeTrialResult()
        form.populate_obj(model)
        # TODO work out why foreign keys need to be done like this.
        model.time_trial_id = model.time_trial_id.id
        model.runner_id = model.runner_id.id
        db.session.add(model)
        db.session.commit()
    elif request.method == 'GET':
        form.time_trial_id.data = current_model

    results = current_model.results.join(TimeTrialResult.runner).order_by(Runner.first_name.asc())
    breadcrumbs = [
        {'link': url_for('index'), 'text': 'Home', 'visible': True},
        {'link': url_for('time_trial'), 'text': 'Time Trials', 'visible': True},
        {'text': 'View Time Trial: '+str(current_model)}
    ]
    return render_template(
        'time_trial_results.html',
        form=form,
        time_trial=current_model,
        results=results,
        tables=[{'name': 'time-trial-results-list'}],
        breadcrumbs=breadcrumbs,
    )


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = Runner.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('index'))
    return render_template('auth/login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/admin')
@login_required
def admin():
    if not is_admin():
        raise Forbidden
    return render_template(
        'admin/admin.html',
        title="Admin",
    )


@app.route('/delete_data')
@login_required
def delete_data():
    if not is_sys_admin():
        raise Forbidden
    # TODO delete all except admins
    Runner.query.delete()
    TimeTrial.query.delete()
    TimeTrialResult.query.delete()
    flash('Data Deleted')
    return render_template(
        'admin/admin.html',
        title="Admin",
    )


@app.route('/parse_spreadsheet', methods=['GET', 'POST'])
@login_required
def parse_spreadsheet():
    if not is_sys_admin():
        raise Forbidden
    form = LoadResults()
    response = ''
    if form.validate_on_submit():
        f = form.attending.data
        path = False
        if f:
            filename = secure_filename(f.filename)
            path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            f.save(path)

        Runner.query.delete()
        TimeTrial.query.delete()
        TimeTrialResult.query.delete()
        sheet = TimeTrialSpreadsheet(path)

        data_runners = sheet.get_runners_from()
        for k, v in data_runners.items():
            current_runner = Runner()
            username = v['first_name']+'_'+v['last_name']
            username = username.replace(' ', '_').lower()
            level = 1
            if username == 'tv_' or username == 'daniel_jitnah' :
                level = 2
            elif username == 'rosemary_waghorn':
                level = 3
            current_runner.active = v['active']
            current_runner.level = level
            current_runner.gender = v['gender']
            current_runner.first_name = v['first_name']
            current_runner.last_name = v['last_name']
            current_runner.username = username
            current_runner.set_password('test123')
            db.session.add(current_runner)

        data_trials = sheet.get_time_trials_from()
        for k, v in data_trials.items():
            current_time_trial = TimeTrial()
            current_time_trial.date = v['date']
            db.session.add(current_time_trial)
        db.session.commit()

        results = sheet.get_time_trials_results_from()
        errors = []
        for v in results:
            current_runner = Runner.query.filter_by(first_name=v['first_name'],last_name=v['last_name']).first()
            current_time_trial = TimeTrial.query.filter_by(date=v['time_trial_date'].date()).first()

            result = TimeTrialResult()
            result.runner_id = current_runner.id
            result.time_trial_id = current_time_trial.id
            result.time = v['time']
            db.session.add(result)
        db.session.commit()

        response = str(len(data_runners)) + " runner records added, " \
            + str(len(data_trials)) + " time trial records added, " \
            + str(len(results)) + " time trial result records added" \
            + ', '.join(errors)

    return render_template(
        'admin/spreadsheet.html',
        title="Parse Spreadsheet",
        form=form,
        message=response
    )


@app.route('/parse_attending', methods=['GET', 'POST'])
@login_required
def parse_attending():
    if not is_admin():
        raise Forbidden
    form = LoadAttending()
    message = ''
    if form.validate_on_submit():
        f = form.attending.data
        filename = secure_filename(f.filename)
        path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        f.save(path)

        for item in Runner.query.all():
            item.active = 0
        db.session.commit()

        names = TimeTrialUtils.make_active(path)
        missing = []
        for v in names:
            item = Runner.query.filter_by(first_name=v['first_name'],last_name=v['last_name']).first()
            if item:
                item.active = 1
            else:
                missing.append(v)
        db.session.commit()
        message = 'Attendance file uploaded'
        message += 'The following were not found'
        message += str(missing)

        flash('Attendance file uploaded')

    return render_template(
        'admin/attending.html',
        title="Parse Attending",
        form=form,
        message=message
    )


@app.route('/printed_timesheet', methods=['GET', 'POST'])
@login_required
def create_printed_timesheet():
    if not is_admin():
        raise Forbidden
    form = PrintTimeTrial()
    if form.validate_on_submit():
        sheet = TimeTrialSpreadsheet(False)
        current_time_trial = form.time_trial_id.data
        date = current_time_trial.date.strftime('%Y_%m_%d')
        filename = 'time_trial_'+date+'.xlsx'
        path = 'app/static/time_trials/' + filename
        path_read = 'static/time_trials/' + filename
        active_runners = [
            [str(k), k.get_pb()]
            for k in Runner.query.order_by(Runner.first_name.asc()).filter_by(active=1)
        ]

        template = sheet.get_template_from(active_runners, current_time_trial.date, path)

        return send_file(
            path_read,
            mimetype='application/vnd.ms-excel',
            as_attachment=True,
            attachment_filename=filename
        )

    return render_template(
        'admin/print_timesheet.html',
        title="Print TimeSheet",
        form=form,
    )


@app.route('/export_results', methods=['GET', 'POST'])
@login_required
def export_results():
    if not is_admin():
        raise Forbidden
    form = PrintTimeTrial()
    if form.validate_on_submit():
        sheet = TimeTrialSpreadsheet(False)
        current_time_trial = form.time_trial_id.data
        date = current_time_trial.date.strftime('%Y_%m_%d')
        filename = 'time_trial_results_'+date+'.xlsx'
        path = 'app/static/time_trials/' + filename
        path_read = 'static/time_trials/' + filename
        results = [
            [str(k.runner), k.runner.get_latest_result(), k.runner.get_pb(), k.get_is_pb(), k.get_is_first_time()]
            for k in current_time_trial.results
        ]
        sheet.export(results, current_time_trial.date, path)

        return send_file(
            path_read,
            mimetype='application/vnd.ms-excel',
            as_attachment=True,
            attachment_filename=filename
        )
    return render_template(
        'admin/export_results.html',
        title="Export Results",
        form=form,
    )


def is_admin():
    return current_user.is_authenticated and current_user.level >= 2


def is_sys_admin():
    return current_user.is_authenticated and current_user.level >= 3


def make_graph(username, results):
    times = [v.time for v in results]
    time_trial_dates = [v.time_trial.date.strftime('%b %Y') for v in results]
    #for item in results:
    #    times.append(item/)
    #lnprice = numpy.log(times)
    # .strftime('%M:%S')
    ax = plt.plot(time_trial_dates, times)
    plt.xticks(rotation=30)
    plt.xlabel('Time Trial')
    plt.ylabel('Time')
    #plt.gca().yaxis.set_major_formatter(dates2.DateFormatter('%M:%S'))
    #plt.gca().yaxis.set_major_formatter(ticker.FuncFormatter(major_formatter))
    #plt.gca().yaxis.set_major_formatter( mdates.DateFormatter('%Y-%m-%d'))


    #plt.axis(dates)
    #plt.axes()
    #plt.set_formatter(dates.DateFormatter('%H:%M'))
    filename = 'images/runner_'+username+'.png'
    path = 'app/static/' + filename
    plt.savefig(path)
    plt.clf()
    return url_for('static', filename=filename)


# Func formatter
def major_formatter(x, pos):
    #time = datetime64
    return type(x) #x.strftime('%M:%S')