from flask import Blueprint, request, render_template, redirect, url_for, flash
from forms import LoginForm, SignupForm

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		username = form.username.data
		password = form.password.data
		if username == "admin" and password == "senha":
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
		# new_user = User(username=username, password=password)
		# db.session.add(new_user)
		# db.session.commit()
		flash('Conta criada com sucesso!', 'success')
		return redirect(url_for('auth.login')) # Redireciona para a página de login (você pode criar essa rota)
	return render_template('signup.html', form=form)

