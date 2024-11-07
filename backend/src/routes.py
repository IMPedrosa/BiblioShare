from flask import Blueprint, request, render_template, redirect, url_for, flash
from forms import LoginForm, SignupForm
from models import User, Book, History
#from app import db
from flask import session
from datetime import datetime
from collections import Counter

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
    from app import db
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
    from app import db
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
        return redirect(url_for('auth.meus_livros'))
    return render_template('book-registration.html')

@auth.route('/edit-book/<int:book_id>', methods=['GET', 'POST'])
def editar_livro(book_id):
    from app import db
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
        return redirect(url_for('auth.meus_livros'))
    return render_template('book-registration.html', book=book)

@auth.route('/delete-book/<int:book_id>', methods=['POST'])
def deletar_livro(book_id):
    from app import db
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    book = Book.query.get_or_404(book_id)
    db.session.delete(book)
    db.session.commit()
    flash('Livro deletado com sucesso!', 'success')
    return redirect(url_for('auth.meus_livros'))

@auth.route('/toggle-availability/<int:book_id>', methods=['POST'])
def alternar_disponibilidade(book_id):
    from app import db
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    book = Book.query.get_or_404(book_id)

    if book.borrower_id is not None:
        flash('Este livro está emprestado e não pode ser disponibilizado no momento.', 'danger')
        return redirect(url_for('auth.home'))
    
    book.is_available = not book.is_available
    db.session.commit()

    flash('Disponibilidade do livro atualizada com sucesso!', 'success')
    return meus_livros()
    
@auth.route('/search-books', methods=['GET', 'POST'])
def buscar_livros():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    user_id = session['user_id']
    filters = [Book.owner_id != user_id]
    filters.append(Book.is_available.is_(True))

    title, author, genre, is_available = "", "", "", "on"
    if request.method == 'POST':
        title = request.form.get('titulo')
        author = request.form.get('autor')
        genre = request.form.get('genero')
        is_available = request.form.get('disponibilidade')

        if title:
            filters.append(Book.title.ilike(f'%{title}%'))
        if author:
            filters.append(Book.author.ilike(f'%{author}%'))
        if genre:
            filters.append(Book.genre.ilike(f'%{genre}%'))
        if is_available == 'off':
            filters.append(Book.is_available.is_(False))
        else:
            filters.append(Book.is_available.is_(True))

    books = Book.query.filter(*filters).all()
    return render_template('search-books.html', books=books, title=title, author=author, genre=genre, is_available=is_available)

@auth.route('/my-books', methods=['GET'])
def meus_livros():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    user_id = session['user_id']
    owned_books = Book.query.filter_by(owner_id=user_id).all()
    borrowed_books = Book.query.filter_by(borrower_id=user_id).all()
    
    return render_template('my-books.html', owned_books=owned_books, borrowed_books=borrowed_books)

@auth.route('/borrow-book/<int:book_id>', methods=['POST'])
def pegar_emprestado(book_id):
    from app import db
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    book = Book.query.get_or_404(book_id)
    
    if not book.is_available:
        flash('Este livro não está disponível para empréstimo.', 'danger')
        return redirect(url_for('auth.buscar_livros'))
    
    book.is_available = False
    book.borrower_id = session['user_id']
    owner_id = book.owner_id
    db.session.commit()

    history = History(
        book_id=book.id,
        borrower_id=session['user_id'],
        owner_id=owner_id,
        borrow_date=datetime.utcnow(),
        return_date=None,
        returned=False
    )
    db.session.add(history)
    db.session.commit()
    
    flash('Livro emprestado com sucesso!', 'success')
    return redirect(url_for('auth.buscar_livros'))

@auth.route('/return-book/<int:book_id>', methods=['POST'])
def devolver_livro(book_id):
    from app import db
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    book = Book.query.get_or_404(book_id)
    
    if book.borrower_id != session['user_id']:
        flash('Você não tem permissão para devolver este livro.', 'danger')
        return redirect(url_for('auth.meus_livros'))
    
    book.is_available = True
    book.borrower_id = None
    db.session.commit()

    history = History.query.filter_by(book_id=book.id, borrower_id=session['user_id'], returned=False).first()
    if history:
        history.return_date = datetime.utcnow()
        history.returned = True
        db.session.commit()

    flash('Livro devolvido com sucesso!', 'success')
    return redirect(url_for('auth.meus_livros'))

@auth.route('/user-statistics', methods=['GET',  'POST'])
def estatisticas_usuario():
    from app import db
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    user_id = session['user_id']
    
    total_books = Book.query.filter_by(owner_id=user_id).count()

    total_borrowed_books = History.query.filter_by(owner_id=user_id).count()

    total_books_borrowed = History.query.filter_by(borrower_id=user_id).count()

    borrowed_books_by_month = db.session.query(
        db.func.extract('year', History.borrow_date).label('year'),
        db.func.extract('month', History.borrow_date).label('month'),
        db.func.count(History.id).label('count')
    ).filter(
        History.owner_id == user_id
    ).group_by('year', 'month').all()

    borrowed_books_by_month = [(int(year), int(month), count) for year, month, count in borrowed_books_by_month]

    borrowed_books_taken_by_month = db.session.query(
        db.func.extract('year', History.borrow_date).label('year'),
        db.func.extract('month', History.borrow_date).label('month'),
        db.func.count(History.id).label('count')
    ).filter(
        History.borrower_id == user_id
    ).group_by('year', 'month').all()

    borrowed_books_taken_by_month = [(int(year), int(month), count) for year, month, count in borrowed_books_taken_by_month]

    return render_template('user-statistics.html', 
        total_books=total_books, 
        total_borrowed_books=total_borrowed_books,
        total_books_borrowed=total_books_borrowed,
        borrowed_books_by_month=borrowed_books_by_month,
        borrowed_books_taken_by_month=borrowed_books_taken_by_month)
