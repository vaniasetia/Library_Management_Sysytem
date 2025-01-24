"""Entities:
    Book
Attributes:
Title
Genre
Last Issued Time
Last Return Time
Is Issued (True/False)
    User
Attributes:
Name
User ID
Books Issued (List of Book objects)
API Endpoints:
Books API:
Add Book: /books/ (POST)
Remove Book: /books/ (DELETE)
Browse Available Books: /books/catalogue/ (GET)
Users API:
Create User: /users/ (POST)
Actions API:
Issue Book: /books/issue/ (POST)
Return Book: /books/return/ (POST)"""


from fastapi import FastAPI, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

app = FastAPI()

# Pydantic Models
class Book(BaseModel):
    id: int
    title: str
    genre: str
    last_issued_time: Optional[datetime] = None
    last_return_time: Optional[datetime] = None
    is_issued: bool = False

class User(BaseModel):
    name: str
    user_id: int
    books_issued: List[Book] = []

# In-memory storage
books: List[Book] = []
users: List[User] = []

# Routes
@app.post("/books/")
def add_book(book: Book):
    #Add a new book to the library.
    if book.id in [book.id for book in books]:
        raise HTTPException(status_code=400, detail="Book with this id already exists.")
    books.append(book)
    return {"message": f"Book '{book.title}' added successfully."}

@app.delete("/books/")
def remove_book(id: int):
    #Remove a book from the library.
    for book in books:
        if book.id == id and not book.is_issued:
            books.remove(book)
            return {"message": f"Book '{book.title}' removed successfully."}
    raise HTTPException(status_code=404, detail="Book not found or currently issued.")

@app.post("/users/")
def create_user(user: User):
    #Create a new user.
    if user.user_id in [user.user_id for user in users]:
        raise HTTPException(status_code=400, detail="User ID already exists.")
    users.append(user)
    return {"message": f"User '{user.name}' created successfully."}


@app.post("/books/issue/")
def issue_book(user_id: int, book_id: int):
    #Issue a book to a user.
    user = next((user for user in users if user.user_id == user_id), None)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    book = next((book for book in books if book.id == book_id and not book.is_issued), None)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found or already issued.")

    book.is_issued = True
    book.last_issued_time = datetime.now()
    user.books_issued.append(book.title)
    return {"message": f"Book '{book.title}' issued to user '{user.name}' successfully."}

@app.post("/books/return/")
def return_book(user_id: int, book_id: int):
    #Return a book issued by a user.
    user = next((user for user in users if user.user_id == user_id), None)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    if book_id not in [book.id for book in user.books_issued]:
        raise HTTPException(status_code=404, detail="Book not found in user's issued list.")

    book = next((book for book in books if book.id == book_id), None)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found.")

    book.is_issued = False
    book.last_return_time = datetime.now()
    user.books_issued.remove(book)
    return {"message": f"Book '{book.title}' returned successfully by user '{user.name}'."}

@app.get("/books/catalogue/")
def browse_books():
    #View the catalogue of available (non-issued) books.
    available_books = [book for book in books if not book.is_issued]
    if not available_books:
        return {"message": "No books available."}
    return {"available_books": [{"title": book.title, "genre": book.genre} for book in available_books]}
