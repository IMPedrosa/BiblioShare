from flask import Blueprint, request, render_template, redirect, url_for, flash
from forms import LoginForm, SignupForm
from models import User
from app import db

auth = Blueprint('auth', __name__)

@auth.route('/')
def index():
  return redirect(url_for('auth.login'))

@auth.route('/login', methods=['GET', 'POST'])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		username = form.username.data
		password = form.password.data
		user = User.query.filter_by(username=username).first()
		if user and user.verify_password(password):
			flash('Login bem-sucedido!', 'success')
			return redirect(url_for('home'))
		else:
			flash('Usuário ou senha inválidos.', 'danger')
	return render_template('login.html', form=form)

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash('Conta criada com sucesso!', 'success')
        return redirect(url_for('auth.login'))
    return render_template('signup.html', form=form)
