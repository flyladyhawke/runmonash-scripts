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


class TimeTrialForm(FlaskForm):
    date = DateField('Date', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    submit = SubmitField('Add')

    def __init__(self, mode, *args, **kwargs):
        super(TimeTrialForm, self).__init__(*args, **kwargs)
        if mode == 'update':
            self.submit = SubmitField('Update')


class RunnerForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    gender = SelectField('Gender', choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')])
    active = BooleanField('Active')
    submit = SubmitField('Add')

    def __init__(self, mode, *args, **kwargs):
        #super().__init__(*args, **kwargs)
        print(self.submit)
        self.submit = SubmitField('Update')
        print(self.submit)
        super(RunnerForm, self).__init__(*args, **kwargs)
        #if mode == 'update':
        print(self.submit)
        print(self._fields)
        print(self._fields['submit'])
        # self._fields['submit'] = SubmitField('Update')

    # def __init__(self, mode='add'):
    #     if mode == 'update':
    #         self.submit = SubmitField('Update')


class TimeTrialResultForm(FlaskForm):
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
