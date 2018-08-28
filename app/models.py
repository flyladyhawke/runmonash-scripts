from app import db
from app import login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


@login.user_loader
def load_user(id):
    return Runner.query.get(int(id))


class TimeTrial(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date)
    description = db.Column(db.String(150))
    results = db.relationship('TimeTrialResult', backref='time_trial', lazy='dynamic')

    def get_formatted_date(self):
        return self.date.strftime("%d/%m/%Y")

    def __repr__(self):
        return '{}'.format(self.date.strftime('%d/%m/%Y'))


class Runner(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    gender = db.Column(db.String(2))
    active = db.Column(db.Integer)
    level = db.Column(db.Integer)
    password_hash = db.Column(db.String(128))
    results = db.relationship('TimeTrialResult', backref='runner', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_pb(self, time_trial_id=False):
        # result = TimeTrialResult.query.filter_by(runner_id=self.id).first()
        if time_trial_id:
            # TODO filter where results are before the time trial given
            result = self.results.order_by(TimeTrialResult.time.asc()).first()
        else:
            result = self.results.order_by(TimeTrialResult.time.asc()).first()
        if result:
            return result.time.strftime('%M:%S')
        else:
            return ''

    def get_pb_time(self):
        # result = TimeTrialResult.query.filter_by(runner_id=self.id).first()
        result = self.results.order_by(TimeTrialResult.time.asc()).first()
        if result:
            return result.time
        else:
            return ''

    def get_latest_result(self):
        result = self.results.order_by(TimeTrialResult.id.desc()).first()
        if result:
            return result.time.strftime('%M:%S')
        else:
            return ''

    def __repr__(self):
        return '{} {}'.format(self.first_name, self.last_name)


class TimeTrialResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time_trial_id = db.Column(db.Integer, db.ForeignKey('time_trial.id'))
    runner_id = db.Column(db.Integer, db.ForeignKey('runner.id'))
    time = db.Column(db.Time)
    comment = db.Column(db.String(50))

    def get_is_pb(self):
        if self.get_is_first_time():
            return False

        pb_time = self.runner.get_pb_time()
        # Check number of results to make sure not a duplicate pb
        # TODO make only for time trials earlier than this
        results = TimeTrialResult.query.filter_by(runner_id=self.runner_id, time=pb_time)
        if results.count() == 1 and self.time == pb_time:
            return True
        else:
            return False

    def get_is_first_time(self):
        result = self.runner.results
        if result and result.count() == 1:
            return True
        else:
            return False

    def __repr__(self):
        return '<TimeTrialResult>'
