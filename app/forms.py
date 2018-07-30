from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField, SelectField, DateField, TimeField, PasswordField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired
from flask_wtf.file import FileField, FileAllowed, FileRequired
from app.models import TimeTrial, Runner


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class AddTimeTrial(FlaskForm):
    date = DateField('Date', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    submit = SubmitField('Add')


class AddRunner(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    gender = SelectField('Gender', choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')])
    active = BooleanField('Active')
    submit = SubmitField('Add')


class AddResult(FlaskForm):
    time_trial_id = QuerySelectField('Date', validators=[DataRequired()], query_factory=lambda: TimeTrial.query.all())
    runner_id = QuerySelectField('Runner', validators=[DataRequired()], query_factory=lambda: Runner.query.all())
    time = TimeField('Time', format='%M:%S')
    comment = StringField('Comment')
    submit = SubmitField('Add')


class LoadAttending(FlaskForm):
    attending = FileField('Attending Spreadsheet', validators=[
        FileRequired(),
        FileAllowed(['xlsx'], 'excel (.xlsx) only!')
    ])
    submit = SubmitField('Upload')


class LoadResults(FlaskForm):
    attending = FileField('Results Spreadsheet', validators=[
        FileAllowed(['xlsx'], 'excel (.xlsx) only!')
    ])
    submit = SubmitField('Upload')
