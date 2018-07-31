from flask import render_template, url_for, flash, redirect, request
from app import app, db
from app.forms import AddTimeTrial, AddRunner, AddResult, LoadAttending, LoadResults, LoginForm
from app.models import TimeTrial, Runner, TimeTrialResult
from src.time_trial import TimeTrialSpreadsheet, TimeTrialUtils
from werkzeug.utils import secure_filename
from werkzeug.exceptions import HTTPException, Forbidden
from flask_login import login_required, current_user, login_user, logout_user
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
    form = AddTimeTrial()
    current = TimeTrial.query.all()
    if form.validate_on_submit():
        model = TimeTrial(
            date=form.date.data,
            description=form.description.data
        )
        db.session.add(model)
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('time_trial'))
    elif request.args.get('remove'):
        tt = TimeTrial.query.filter_by(date=request.args.get('date')).first_or_404()
        db.session.delete(tt)
        db.session.commit()
        current = TimeTrial.query.all()
    return render_template('time_trial.html', title='Add', form=form, current=current, tables=['time-trial-list'])


@app.route('/runner/update/<id>', methods=['GET', 'POST'])
def runner_update(id):
    current = Runner.query.all()
    tt = Runner.query.filter_by(id=id).first_or_404()
    form = AddRunner()
    form.populate_obj(tt)
    if form.validate_on_submit():
        tt.first_name=form.first_name.data
        tt.last_name=form.last_name.data
        tt.gender=form.gender.data
        tt.active=form.active.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('runner_result', id=id))
    return render_template(
        'runner.html',
        title='Runners',
        form=form,
        runner=runner,
        current=current,
        next_url=None,
        prev_url=None,
    )


@app.route('/runner/delete/<id>', methods=['GET', 'POST'])
def runner_delete(id):
    tt = Runner.query.filter_by(id=request.args.get('id')).first_or_404()
    db.session.delete(tt)
    db.session.commit()
    return redirect(url_for('runner'))


@app.route('/runner', methods=['GET', 'POST'])
def runner():
    form = AddRunner()
    current = Runner.query.all()
    if form.validate_on_submit():
        model = Runner(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            gender=form.gender.data,
            active=form.active.data
        )
        db.session.add(model)
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('runner'))
    elif request.args.get('remove'):
        tt = Runner.query.filter_by(id=request.args.get('id')).first_or_404()
        db.session.delete(tt)
        db.session.commit()
        current = Runner.query.all()
    return render_template(
        'runner.html',
        title='Runners',
        form=form,
        runner=runner,
        current=current,
        tables=['runner-list']
    )


@app.route('/time_trial_result/<date>', methods=['GET', 'POST'])
def time_trial_result(date):
    tt = TimeTrial.query.filter_by(date=date).first_or_404()
    form = AddResult()
    if form.validate_on_submit():
        model = TimeTrialResult(
            time_trial_id=form.time_trial_id.data.id,
            runner_id=form.runner_id.data.id,
            time=form.time.data,
            comment=form.comment.data
        )
        db.session.add(model)
        db.session.commit()
    elif request.method == 'GET':
        form.time_trial_id.data = tt

    results = tt.results.order_by(TimeTrialResult.runner_id.asc())
    return render_template(
        'time_trial_results.html',
        form=form,
        time_trial=tt,
        results=results,
        tables=['time-trial-results-list']
    )


@app.route('/runner_result/<id>', methods=['GET', 'POST'])
def runner_result(id):
    runner = Runner.query.filter_by(id=id).first_or_404()
    if current_user.is_authenticated and current_user.id == runner.id:
        form = AddRunner()
        form.populate_obj(runner)
        form.first_name = runner.first_name
        # form.first_name = runner.first_name
        # if form.validate_on_submit():
        #     runner.first_name=form.first_name.data,
        #     runner.last_name=form.last_name.data,
        #     runner.gender=form.gender.data,
        #     runner.active=form.active.data
        #     # db.session.commit()
        # elif request.method == 'GET':
        #     form.populate_obj(runner)
        #     form.first_name = runner.first_name
    else:
        form = AddResult()
        if form.validate_on_submit():
            model = TimeTrialResult(
                time_trial_id=form.time_trial_id.data.id,
                runner_id=form.runner_id.data.id,
                time=form.time.data,
                comment=form.comment.data
            )
            db.session.add(model)
            db.session.commit()
        elif request.method == 'GET':
            form.runner_id.data = runner

    results = runner.results.order_by(TimeTrialResult.time_trial_id.asc())
    url = make_graph(id, results)
    return render_template(
        'runner_results.html',
        form=form,
        runner=runner,
        results=results.items,
        tables=['time-trial-results-list'],
        url=url,
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
    Runner.query.delete()
    TimeTrial.query.delete()
    TimeTrialResult.query.delete()
    flash('Data Deleted')
    return render_template(
        'admin/admin.html',
        title="Admin",
    )


@app.route('/parse_spreadsheet', methods=['GET', 'POST'])
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
            runner = Runner()
            username = v['first_name']+'_'+v['last_name']
            username = username.replace(' ', '_').lower()
            level = 1
            if username == 'tv_' or username == 'daniel_jitnah' :
                level = 2
            elif username == 'rosemary_waghorn':
                level = 3
            runner.active = v['active']
            runner.level = level
            runner.gender = v['gender']
            runner.first_name = v['first_name']
            runner.last_name = v['last_name']
            runner.username = username
            runner.set_password('test123')
            db.session.add(runner)

        data_trials = sheet.get_time_trials_from()
        for k, v in data_trials.items():
            trial = TimeTrial()
            trial.date = v['date']
            db.session.add(trial)
        db.session.commit()

        results = sheet.get_time_trials_results_from()
        errors = []
        for v in results:
            runner = Runner.query.filter_by(first_name=v['first_name'],last_name=v['last_name']).first()
            time_trial = TimeTrial.query.filter_by(date=v['time_trial_date'].date()).first()

            trial = TimeTrialResult()
            trial.runner_id = runner.id
            trial.time_trial_id = time_trial.id
            trial.time = v['time']
            db.session.add(trial)
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

        for runner in Runner.query.all():
            runner.active = 0
        db.session.commit()

        names = TimeTrialUtils.make_active(path)
        missing = []
        for v in names:
            runner = Runner.query.filter_by(first_name=v['first_name'],last_name=v['last_name']).first()
            if runner:
                runner.active = 0
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
    form = LoadResults()
    response = ''
    if form.validate_on_submit():
        f = form.attending.data
        path = False
        if f:
            filename = secure_filename(f.filename)
            path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            f.save(path)

        sheet = TimeTrialSpreadsheet(path)
        active_runners = Runner.query.filter_by(active=1)
        template = sheet.get_template_for(active_runners)

    return render_template(
        'admin/spreadsheet.html',
        title="Print TimeSheet",
        form=form,
        message=response
    )


@app.route('/printed_result', methods=['GET', 'POST'])
@login_required
def create_printed_results():
    if not is_admin():
        raise Forbidden
    return render_template(
        'index.html',
        title="Print Results",
    )


def is_admin():
    return current_user.is_authenticated and current_user.level >= 2


def is_sys_admin():
    return current_user.is_authenticated and current_user.level >= 3


def make_graph(id, results):
    times = [v.time for v in results.items]
    time_trial_dates = [v.time_trial.date.strftime('%b %Y') for v in results.items]
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
    filename = 'images/runner_'+id+'.png'
    path = 'app/static/' + filename
    plt.savefig(path)
    plt.clf()
    return url_for('static', filename=filename)


# Func formatter
def major_formatter(x, pos):
    #time = datetime64
    return type(x) #x.strftime('%M:%S')