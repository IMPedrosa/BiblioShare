from app import app, db
from models import User, Book, History
from datetime import datetime, timedelta
import random

def create_users_and_books():
    users = [
        User(username='user1', password='senha123'),
        User(username='user2', password='senha456'),
        User(username='user3', password='senha789'),
        User(username='user4', password='senha321'),
        User(username='user5', password='senha654'),
    ]
    
    # Adicionar os usuários ao banco
    db.session.add_all(users)
    db.session.commit()
    
    # Criar livros e associar aos usuários
    books = []
    book_data = [
        ('Book 1', 'Author 1', 2020, 'Ficção', users[0]),
        ('Book 2', 'Author 2', 2021, 'Mistério', users[0]),
        ('Book 3', 'Author 3', 2022, 'Aventura', users[0]),
        ('Book 4', 'Author 4', 2024, 'Ficção', users[0]),
        ('Book 5', 'Author 5', 2020, 'Romance', users[0]),
        ('Book 6', 'Author 6', 2021, 'Drama', users[0]),
        ('Book 7', 'Author 7', 2022, 'História', users[0]),
        ('Book 8', 'Author 8', 2024, 'Ficção', users[0]),
        ('Book 9', 'Author 9', 2021, 'Mistério', users[0]),
        ('Book 10', 'Author 10', 2020, 'Ficção', users[0]),
        ('Book 11', 'Author 11', 2022, 'Aventura', users[1]),
        ('Book 12', 'Author 12', 2024, 'Ficção', users[1]),
        ('Book 13', 'Author 13', 2020, 'Romance', users[1]),
        ('Book 14', 'Author 14', 2021, 'Mistério', users[1]),
        ('Book 15', 'Author 15', 2024, 'Ficção', users[1]),
        ('Book 16', 'Author 16', 2022, 'História', users[1]),
        ('Book 17', 'Author 17', 2024, 'Drama', users[1]),
        ('Book 18', 'Author 18', 2020, 'Ficção', users[1]),
        ('Book 19', 'Author 19', 2021, 'Romance', users[1]),
        ('Book 20', 'Author 20', 2024, 'Mistério', users[1]),
        ('Book 21', 'Author 21', 2020, 'Ficção', users[2]),
        ('Book 22', 'Author 22', 2021, 'Aventura', users[2]),
        ('Book 23', 'Author 23', 2022, 'História', users[2]),
        ('Book 24', 'Author 24', 2024, 'Ficção', users[2]),
        ('Book 25', 'Author 25', 2020, 'Mistério', users[2]),
        ('Book 26', 'Author 26', 2021, 'Drama', users[2]),
        ('Book 27', 'Author 27', 2022, 'Aventura', users[2]),
        ('Book 28', 'Author 28', 2024, 'Ficção', users[2]),
        ('Book 29', 'Author 29', 2020, 'Romance', users[2]),
        ('Book 30', 'Author 30', 2024, 'Mistério', users[2]),
        ('Book 31', 'Author 31', 2020, 'Ficção', users[3]),
        ('Book 32', 'Author 32', 2021, 'Mistério', users[3]),
        ('Book 33', 'Author 33', 2022, 'Aventura', users[3]),
        ('Book 34', 'Author 34', 2024, 'Ficção', users[3]),
        ('Book 35', 'Author 35', 2020, 'Romance', users[3]),
        ('Book 36', 'Author 36', 2021, 'Drama', users[3]),
        ('Book 37', 'Author 37', 2022, 'História', users[3]),
        ('Book 38', 'Author 38', 2024, 'Ficção', users[3]),
        ('Book 39', 'Author 39', 2020, 'Mistério', users[3]),
        ('Book 40', 'Author 40', 2024, 'Romance', users[3]),
        ('Book 41', 'Author 41', 2020, 'Ficção', users[4]),
        ('Book 42', 'Author 42', 2021, 'Mistério', users[4]),
        ('Book 43', 'Author 43', 2022, 'Aventura', users[4]),
        ('Book 44', 'Author 44', 2024, 'Ficção', users[4]),
        ('Book 45', 'Author 45', 2020, 'Romance', users[4]),
        ('Book 46', 'Author 46', 2021, 'Drama', users[4]),
        ('Book 47', 'Author 47', 2022, 'História', users[4]),
        ('Book 48', 'Author 48', 2024, 'Ficção', users[4]),
        ('Book 49', 'Author 49', 2020, 'Mistério', users[4]),
        ('Book 50', 'Author 50', 2024, 'Aventura', users[4]),
    ]
    
    for title, author, year, genre, owner in book_data:
        book = Book(
            title=title, 
            author=author, 
            publication_year=year, 
            genre=genre, 
            owner_id=owner.id, 
            is_available=True
        )
        books.append(book)
    
    db.session.add_all(books)
    db.session.commit()
    
    return users, books

def create_borrowing_history(users, books):
    history = []
    months = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    
    for _ in range(100):
        borrower = random.choice(users)
        owner = random.choice(users)
        
        if borrower == owner:
            continue
        
        available_books = [book for book in books if book.owner_id == owner.id and book.is_available]
        
        if not available_books:
            continue 
        
        book = random.choice(available_books)
        borrow_date = datetime(2024, random.choice(months), random.randint(1, 28))
        
        return_date = borrow_date + timedelta(days=random.randint(10, 30)) if random.random() > 0.2 else None
        returned = return_date is not None and random.random() > 0.3
        
        # Criando o histórico de empréstimo
        history_record = History(
            book_id=book.id, 
            borrower_id=borrower.id, 
            owner_id=owner.id, 
            borrow_date=borrow_date, 
            return_date=return_date if returned else None, 
            returned=returned
        )
        
        book.is_available = not returned
        
        history.append(history_record)
    
    db.session.add_all(history)
    db.session.commit()

    print("Dados de seed inseridos com sucesso!")


if __name__ == '__main__':
    with app.app_context(): 
        db.create_all()
        users, books = create_users_and_books()
        create_borrowing_history(users, books)
