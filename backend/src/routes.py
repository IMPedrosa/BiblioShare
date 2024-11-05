from flask import Blueprint, request, render_template, redirect, url_for, flash
from forms import LoginForm, SignupForm
from models import User, Book
from app import db
from flask import session

auth = Blueprint('auth', __name__)

@auth.route('/')
def index():
	if 'user_id' in session:
		return redirect(url_for('auth.home'))
	return redirect(url_for('auth.login'))

@auth.route('/login', methods=['GET', 'POST'])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		username = form.username.data
		password = form.password.data
		user = User.query.filter_by(username=username).first()
		if user and user.verify_password(password):
			session['user_id'] = user.id
			session['username'] = user.username
			return redirect(url_for('auth.home'))
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

@auth.route('/home')
def home():
	if 'user_id' in session:
		return render_template('home.html')
	return redirect(url_for('auth.login'))

@auth.route('/logout')
def logout():
	session.pop('username', None)
	session.pop('user_id', None)
	return redirect(url_for('auth.login'))

@auth.route('/register-book', methods=['GET', 'POST'])
def cadastrar_livro():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    if request.method == 'POST':
        title = request.form['titulo']
        author = request.form['autor']
        publication_year = request.form['ano_publicacao']
        genre = request.form['genero']
        description = request.form['descricao']
        new_book = Book(title=title, author=author, publication_year=publication_year, genre=genre, details=description, owner_id=session['user_id'])
        db.session.add(new_book)
        db.session.commit()
        flash('Livro cadastrado com sucesso!', 'success')
        return redirect(url_for('auth.home'))
    return render_template('book-registration.html')

@auth.route('/edit-book/<int:book_id>', methods=['GET', 'POST'])
def editar_livro(book_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    book = Book.query.get_or_404(book_id)
    if request.method == 'POST':
        book.title = request.form['titulo']
        book.author = request.form['autor']
        book.publication_year = request.form['ano_publicacao']
        book.genre = request.form['genero']
        book.details = request.form['descricao']
        db.session.commit()
        flash('Livro atualizado com sucesso!', 'success')
        return redirect(url_for('auth.home'))
    return render_template('book-registration.html', book=book)

@auth.route('/delete-book/<int:book_id>', methods=['POST'])
def deletar_livro(book_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    book = Book.query.get_or_404(book_id)
    db.session.delete(book)
    db.session.commit()
    flash('Livro deletado com sucesso!', 'success')
    return redirect(url_for('auth.home'))

@auth.route('/toggle-availability/<int:book_id>', methods=['POST'])
def alternar_disponibilidade(book_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    book = Book.query.get_or_404(book_id)

    if book.borrower_id is not None:
        flash('Este livro está emprestado e não pode ser disponibilizado no momento.', 'danger')
        return redirect(url_for('auth.home'))
    
    book.is_available = not book.is_available
    db.session.commit()

    flash('Disponibilidade do livro atualizada com sucesso!', 'success')
    return redirect(url_for('auth.home'))

@auth.route('/search-books', methods=['GET', 'POST'])
def buscar_livros():
    filters = []
    if request.method == 'POST':
        title = request.form.get('titulo')
        author = request.form.get('autor')
        genre = request.form.get('genero')
        is_available = request.form.get('disponivel')

        if title:
            filters.append(Book.title.ilike(f'%{title}%'))
        if author:
            filters.append(Book.author.ilike(f'%{author}%'))
        if genre:
            filters.append(Book.genre.ilike(f'%{genre}%'))
        if is_available == 'on':
            filters.append(Book.is_available.is_(True))

    books = Book.query.filter(*filters).all()
    return render_template('search-books.html', books=books)

@auth.route('/my-books', methods=['GET'])
def meus_livros():
	if 'user_id' not in session:
		return redirect(url_for('auth.login'))
	
	user_id = session['user_id']
	books = Book.query.filter_by(owner_id=user_id).all()
	
	return render_template('my-books.html', books=books)