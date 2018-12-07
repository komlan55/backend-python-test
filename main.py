

from alayatodo import app, db
from alayatodo.models import User, Todo

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Todo': Todo}