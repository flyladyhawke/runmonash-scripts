from flask import render_template, url_for, flash, redirect, request
from app import app, db
from app.forms import AddTimeTrial, AddRunner, AddResult
from app.models import TimeTrial, Runner, TimeTrialResult
from src import time_trial


@app.route('/')
@app.route('/index')
def index():
    current = TimeTrial.query.all()
    return render_template('index.html', title='Index', current=current)


@app.route('/time_trial', methods=['GET', 'POST'])
def add_time_trial():
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
        return redirect(url_for('add_time_trial'))
    return render_template('time_trial.html', title='Add', form=form, current=current)


@app.route('/runner', methods=['GET', 'POST'])
def add_runner():
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
        return redirect(url_for('add_runner'))
    return render_template('runner.html', title='Add', form=form, current=current)


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

    page = request.args.get('page', 1, type=int)
    results = tt.results.paginate(
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
        prev_url=prev_url
    )


@app.route('/runner_result/<id>', methods=['GET', 'POST'])
def runner_result(id):
    runner = Runner.query.filter_by(id=id).first_or_404()
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

    page = request.args.get('page', 1, type=int)
    results = runner.results.paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('id', id=runner.id, page=results.next_num) \
        if results.has_next else None
    prev_url = url_for('id', id=runner.id, page=results.prev_num) \
        if results.has_prev else None
    return render_template(
        'runner_results.html',
        form=form,
        runner=runner,
        results=results.items,
        next_url=next_url,
        prev_url=prev_url
    )
