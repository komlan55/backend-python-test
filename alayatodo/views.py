import json

from alayatodo import app
from flask_login import current_user, login_user,logout_user,login_required
from alayatodo.models import User, Todo, AlchemyEncoder
from alayatodo import db
from flask import (
    g,
    redirect,
    render_template,
    request,
    session,
    url_for, flash)

@app.route('/')
def home():
    with app.open_resource('../README.md', mode='r') as f:
        readme = "".join(l for l in f)
        return render_template('index.html', readme=readme)


@app.route('/login', methods=['GET','POST'])
def login():

    username = request.form.get('username')
    password = request.form.get('password')
    if request.method == 'POST':

        if username is not None and password is not None:
            user = User.query.filter_by(username=username).first()
            if user is None or not user.check_password(password):
                flash('Invalid username or password')
                return redirect('/login')
            if login_user(user, remember=False):
                return redirect('/todo')

    return render_template('login.html')

@app.route('/register',methods=['GET','POST'])
def register():

    username = request.form.get('username')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')

    if request.method == 'POST':
        valid = True
        user = User.query.filter_by(username=username).first()
        print(user)
        if username is  None :
            flash('Please enter a username')
            valid = False
        if user is not None:
            flash('This username is already taken. Please choose another')
            valid = False
        if password is None or confirm_password is None:
            flash('Please enter a password')
            valid = False

        if password != confirm_password:
            flash('Password dont match')
            valid = False

        if valid:
            user =  User(username=username)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            return redirect('/login')
        else:
            return render_template('register.html')

    else:
        return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    session.pop("username",None)
    logout_user()
    return redirect('/')

@app.route('/todo/<id>', methods=['GET'])
@login_required
def todo(id):
    todo = Todo.query.get(id)

    return render_template('todo.html', todo=todo)

@app.route('/todo/<id>/json', methods=['GET'])
@login_required
def todo_json(id):
    todo = Todo.query.get(id)
    text = json.dumps(todo, cls=AlchemyEncoder)
    return render_template('todo_json.html', todo=todo, json=text)


@app.route('/todo/<id>', methods=['POST'])
def todo_complete(id):
    todo = Todo.query.get(id)
    todo.completed = not todo.completed
    db.session.commit()

    return redirect('/todo')


@app.route('/todo', methods=['GET','POST'])
@app.route('/todo/', methods=['GET','POST'])
@login_required
def todos():
    ppp = app.config['ITEM_PER_PAGE']

    page = request.args.get('page', 1, type=int)
    todos = Todo.query.paginate(page,ppp,False)

    next_url = url_for('todos', page=todos.next_num)  if todos.has_next else None
    prev_url = url_for('todos', page=todos.prev_num)  if todos.has_prev else None

    return render_template('todos.html', todos=todos.items,next_url=next_url, prev_url=prev_url)

@app.route('/explore')
@login_required
def explore():
    ppp = app.config['ITEM_PER_PAGE']

    page = request.args.get('page', 1, type=int)
    todos = Todo.query.order_by(Todo.id).paginate(page, ppp, False)
    next_url = url_for('explore', page=todos.next_num) \
        if todos.has_next else None
    prev_url = url_for('explore', page=todos.prev_num) \
        if todos.has_prev else None
    return render_template("todos.html", title='Explore', todos=todos.items, next_url=next_url, prev_url=prev_url)


@app.route('/todo/add', methods=['POST'])
@login_required
def todo_add():
    desc = request.form.get('description', '')
    print("desc={}".format(desc))

    if desc is None:
        flash('Description must not be empty')
    else:
        user = User.query.filter_by(username=current_user.username).first()
        todo = Todo(description=desc,user_id=user.id)
        db.session.add(todo)
        db.session.commit()

        flash('Todo has been successfully added')

    return redirect('/todo')

@app.route('/todo/<id>/delete', methods=['POST'])
@login_required
def todo_delete(id):

    todo = Todo.query.get(id)
    db.session.delete(todo)
    db.session.commit()

    flash('Todo has been successfully deleted')

    return redirect('/todo')
