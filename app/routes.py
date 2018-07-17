from flask import render_template, url_for, flash, redirect
from app import app, db
from app.forms import AddTimeTrial, AddRunner
from app.models import TimeTrial, Runner
from src import time_trial


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Index')


@app.route('/addTimeTrial', methods=['GET', 'POST'])
def add_time_trial():
    form = AddTimeTrial()
    if form.validate_on_submit():
        model = TimeTrial(
            date=form.date.data,
            description=form.description.data
        )
        db.session.add(model)
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect('/addTimeTrial')
    return render_template('add_time_trial.html', title='Add', form=form)


@app.route('/addRunner', methods=['GET', 'POST'])
def add_runner():
    form = AddRunner()
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
    return render_template('add_runner.html', title='Add', form=form)
