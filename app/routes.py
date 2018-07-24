from flask import render_template, url_for, flash, redirect, request
from app import app, db
from app.forms import AddTimeTrial, AddRunner, AddResult, LoadAttending, LoadResults
from app.models import TimeTrial, Runner, TimeTrialResult
from src.time_trial import TimeTrialSpreadsheet, TimeTrialUtils
from werkzeug.utils import secure_filename
import os


@app.route('/')
@app.route('/index')
def index():
    current = TimeTrial.query.all()
    is_admin = request.args.get('is_admin', 0, type=int)
    return render_template('index.html', title='Index', current=current, is_admin=is_admin)


@app.route('/time_trial', methods=['GET', 'POST'])
def time_trial():
    form = AddTimeTrial()
    current = TimeTrial.query.all()
    is_admin = request.args.get('is_admin', 0, type=int)
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
    return render_template('time_trial.html', title='Add', form=form, current=current, is_admin=is_admin)


@app.route('/runner', methods=['GET', 'POST'])
def runner():
    form = AddRunner()
    current = Runner.query.all()
    is_admin = request.args.get('is_admin', 0, type=int)
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

    # page = request.args.get('page', 1, type=int)
    # results = current.results.paginate(
    #     page, app.config['POSTS_PER_PAGE'], False)
    # next_url = url_for('runner', page=results.next_num) \
    #     if results.has_next else None
    # prev_url = url_for('runner', page=results.prev_num) \
    #     if results.has_prev else None
    return render_template(
        'runner.html',
        title='Runners',
        form=form,
        runner=runner,
        current=current,
        next_url=None,
        prev_url=None,
        is_admin=is_admin
    )
    return render_template('runner.html', title='Add', form=form, current=current, is_admin=is_admin)


@app.route('/time_trial_result/<date>', methods=['GET', 'POST'])
def time_trial_result(date):
    tt = TimeTrial.query.filter_by(date=date).first_or_404()
    form = AddResult()
    is_admin = request.args.get('is_admin', 0, type=int)
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

    page = request.args.get('page', 1, type=int)
    results = tt.results.order_by(TimeTrialResult.runner_id.asc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('time_trial_result', date=tt.date, page=results.next_num) \
        if results.has_next else None
    prev_url = url_for('time_trial_result', date=tt.date, page=results.prev_num) \
        if results.has_prev else None
    return render_template(
        'time_trial_results.html',
        form=form,
        time_trial=tt,
        results=results.items,
        next_url=next_url,
        prev_url=prev_url,
        is_admin=is_admin
    )


@app.route('/runner_result/<id>', methods=['GET', 'POST'])
def runner_result(id):
    runner = Runner.query.filter_by(id=id).first_or_404()
    form = AddResult()
    is_admin = request.args.get('is_admin', 0, type=int)
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

    page = request.args.get('page', 1, type=int)
    results = runner.results.order_by(TimeTrialResult.time_trial_id.asc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('runner_result', id=runner.id, page=results.next_num) \
        if results.has_next else None
    prev_url = url_for('runner_result', id=runner.id, page=results.prev_num) \
        if results.has_prev else None
    return render_template(
        'runner_results.html',
        form=form,
        runner=runner,
        results=results.items,
        next_url=next_url,
        prev_url=prev_url,
        is_admin=is_admin
    )


@app.route('/admin')
def admin():
    is_admin = request.args.get('is_admin', 0, type=int)
    return render_template(
        'admin/admin.html',
        title="Admin",
        is_admin=is_admin
    )


@app.route('/parse_spreadsheet', methods=['GET', 'POST'])
def parse_spreadsheet():
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
            runner.active = v['active']
            runner.gender = v['gender']
            runner.first_name = v['first_name']
            runner.last_name = v['last_name']
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
def parse_attending():
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
def create_printed_timesheet():
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
def create_printed_results():
    return render_template(
        'index.html',
        title="Print Results",
    )
