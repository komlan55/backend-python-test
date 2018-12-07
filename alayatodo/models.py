from alayatodo import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from alayatodo import login_manager


class User(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password = db.Column(db.String(128))

    def __repr__(self):
        return '<User id={},username={}>'.format(self.id,self.username)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

class Todo(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    description = db.Column(db.String(140))
    completed = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Todo desc={},completed={}>'.format(self.description,self.completed)

    def to_json(self):
        return "{description:{} ,completed:{} ,user_id:{} }".format(self.id, self.description,self.completed,self.user_id)


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))
