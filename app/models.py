from app import db


class TimeTrial(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date)
    description = db.Column(db.String(150))
    results = db.relationship('TimeTrialResult', backref='time_trial', lazy='dynamic')

    def __repr__(self):
        return '{}'.format(self.date)


class Runner(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    gender = db.Column(db.String(2))
    active = db.Column(db.Integer)
    results = db.relationship('TimeTrialResult', backref='runner', lazy='dynamic')

    def get_pb(self, user):
        self.results.order_by(TimeTrialResult.time.asc()).first()

    def get_latest_result(self, user):
        self.results.order_by(TimeTrialResult.time_trial.date.desc()).first()

    def __repr__(self):
        return '{} {}'.format(self.first_name, self.last_name)


class TimeTrialResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time_trial_id = db.Column(db.Integer, db.ForeignKey('time_trial.id'))
    runner_id = db.Column(db.Integer, db.ForeignKey('runner.id'))
    time = db.Column(db.DateTime)
    comment = db.Column(db.String(50))

    def __repr__(self):
        return '<TimeTrialResult>'
