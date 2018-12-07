import json

from sqlalchemy_json import MutableJson

from alayatodo import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from alayatodo import login_manager
from sqlalchemy.ext.declarative import DeclarativeMeta


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

    def __init__(self, description,user_id, completed=False):
        self.description = description
        self.completed = completed
        self.user_id = user_id

    def __repr__(self):
        return '<Todo desc={},completed={}>'.format(self.description,self.completed)



class AlchemyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj.__class__, DeclarativeMeta):
            # an SQLAlchemy class
            fields = {}
            for field in [x for x in dir(obj) if not x.startswith('_') and x != 'metadata']:
                data = obj.__getattribute__(field)
                try:
                    json.dumps(data) # this will fail on non-encodable values, like other classes
                    fields[field] = data
                except TypeError:
                    fields[field] = None
            # a json-encodable dict
            return fields

        return json.JSONEncoder.default(self, obj)

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))
