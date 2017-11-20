from django.shortcuts import render, redirect
from .models import User, Book, Author, Review
from django.contrib.messages import error
# Create your views here.


def index(request):
    try:
        request.session['user']
    except:
        request.session['user'] = ""

    if request.session['user']:
        return render(request, 'br_app/bookHome.html')
    return render(request, 'br_app/index.html')


def bookHome(request):
    if not request.session['user']:
        return redirect('/')
    context = {
        'user': User.objects.get(id=request.session['user']),
        'reviews': Review.objects.recent_and_not()[0],
        'more': Review.objects.recent_and_not()[1],
        'books': Book.objects.all()
    }
    return render(request, 'br_app/bookHome.html', context)


def register(request):
    errors = User.objects.validate_registration(request.POST)
    if type(errors) == list:
        for err in errors:
            error(request, err)
        return redirect('/')
    request.session['user'] = User.objects.get(email=request.POST['email']).id
    return redirect('/bookHome')


def login(request):
    errors = User.objects.validate_login(request.POST)
    if type(errors) == list:
        for err in errors:
            error(request, err)
        return redirect('/')
    request.session['user'] = User.objects.get(email=request.POST['email']).id
    return redirect('/bookHome')


def logout(request):
    del request.session['user']
    return redirect('/')


def addPage(request):
    context = {
        'author': Author.objects.all()
    }
    return render(request, 'br_app/add.html', context)

def addBook(request):
    errors = Review.objects.validate_review(
        request.POST, request.session['user'])
    if type(errors) == list:
        for err in errors:
            error(request, err)
        return redirect('/')
    if request.POST['addReview'] == "1":
        return redirect('/book/' + request.POST['bookID'])
    return redirect('/bookHome')

def showUser(request, user_id):
    user = User.objects.get(id=user_id)
    unique_ids = user.reviews_left.all().values("book").distinct()
    unique_books = []
    for book in unique_ids:
        unique_books.append(Book.objects.get(id=book['book']))
    context = {
        'user': User.objects.get(id=user_id),
        'unique': unique_books
    }
    return render(request, 'br_app/showUser.html', context)


def showBook(request, book_id):
    book = Book.objects.get(id=book_id)
    context = {
        'book': book,
        'user': User.objects.get(id=request.session['user']),
    }
    return render(request, 'br_app/showBook.html', context)

def delete(request, book_id):
    Book.objects.get(id=book_id).delete()
    return redirect('/bookHome')