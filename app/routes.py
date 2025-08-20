from flask import Blueprint, render_template, url_for, flash, redirect, request, abort
from app import db, bcrypt
from app.forms import RegistrationForm, LoginForm, TaskForm
from app.models import User, Task, Category
from flask_login import login_user, current_user, logout_user, login_required
from datetime import datetime

main = Blueprint('main', __name__)

@main.route("/")
@main.route("/dashboard")
@login_required
def dashboard():
    tasks = Task.query.filter_by(owner=current_user).order_by(Task.due_date).all()
    return render_template('dashboard.html', tasks=tasks)

@main.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_pw)
        db.session.add(user)
        db.session.commit()
        flash('Account created! You can now log in.', 'success')
        return redirect(url_for('main.login'))
    return render_template('register.html', form=form)

@main.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash('Logged in successfully.', 'success')
            return redirect(next_page) if next_page else redirect(url_for('main.dashboard'))
        else:
            flash('Login unsuccessful. Check email and password.', 'danger')
    return render_template('login.html', form=form)

@main.route("/logout")
def logout():
  logout_user()
  flash('You have been logged out.', 'info')
  return redirect(url_for('main.login'))

@main.route("/task/new", methods=['GET', 'POST'])
@login_required
def new_task():
  form = TaskForm()
  form.category.choices = [(c.id, c.name) for c in Category.query.all()]
  if form.validate_on_submit():
    task = Task(
      title=form.title.data,
      description=form.description.data,
      due_date=form.due_date.data,
      priority=form.priority.data,
      category_id=form.category.data,
      owner=current_user
    )
    db.session.add(task)
    db.session.commit()
    flash('Task added successfully!', 'success')
    return redirect(url_for('main.dashboard'))
  return render_template('task_form.html', form=form, legend='Add Task')

@main.route("/task/<int:task_id>/update", methods=['GET', 'POST'])
@login_required
def update_task(task_id):
  task = Task.query.get_or_404(task_id)
  if task.owner != current_user:
    abort(403)
  form = TaskForm()
  form.category.choices = [(c.id, c.name) for c in Category.query.all()]
  if form.validate_on_submit():
    task.title = form.title.data
    task.description = form.description.data
    task.due_date = form.due_date.data
    task.priority = form.priority.data
    task.category_id = form.category.data
    db.session.commit()
    flash('Task updated!', 'success')
    return redirect(url_for('main.dashboard'))
  elif request.method == 'GET':
    form.title.data = task.title
    form.description.data = task.description
    form.due_date.data = task.due_date
    form.priority.data = task.priority
    form.category.data = task.category_id
  return render_template('task_form.html', form=form, legend='Update Task')

@main.route("/task/<int:task_id>/delete", methods=['POST'])
@login_required
def delete_task(task_id):
  task = Task.query.get_or_404(task_id)
  if task.owner != current_user:
    abort(403)
  db.session.delete(task)
  db.session.commit()
  flash('Task deleted!', 'info')
  return redirect(url_for('main.dashboard'))

@main.route("/task/<int:task_id>/toggle", methods=['GET'])
@login_required
def toggle_task(task_id):
  task = Task.query.get_or_404(task_id)
  if task.owner != current_user:
    abort(403)
  task.is_completed = not task.is_completed
  db.session.commit()
  flash('Task status updated.', 'success')
  return redirect(url_for('main.dashboard'))
