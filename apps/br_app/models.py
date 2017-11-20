from __future__ import unicode_literals
import re
import bcrypt
from django.db import models
from datetime import datetime

# Create your models here.
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9\.\+_-]+@[a-zA-Z0-9\._-]+\.[a-zA-Z]*$')


class userManager(models.Manager):
    def validate_registration(self, post_data):
        errors = []
        # Empty fields
        for field, value in post_data.iteritems():
            if len(value) < 1:
                errors.append("{} field is required".format(
                    field.replace('_', ' ')))

        # Name length and alpha
        if len(post_data['fname']) < 2:
            errors.append("First name must be at least 2 characters long")
        elif not post_data['fname'].isalpha():
            errors.append("Name can only contain characters")
        if len(post_data['lname']) < 2:
            errors.append("Last name must be at least 2 characters long")
        elif not post_data['lname'].isalpha():
            errors.append("Name can only contain characters")

        # Email format and exist
        if not re.match(EMAIL_REGEX, post_data['email']):
            errors.append("Invalid email")
        if len(self.filter(email=post_data['email'])) > 0:
            errors.append("Email already registered")

        # Birthday before today
        now = datetime.today()
        if now < datetime.strptime(post_data['bday'], '%Y-%m-%d'):
            errors.append("Can't be born in the future")

        # Password length and match
        if len(post_data['password']) < 8:
            errors.append("Password must be at least 8 characters long")
        if post_data['password'] != post_data['pw_confirm']:
            errors.append("Passwords do not match")

        if not errors:
            pw_hash = bcrypt.hashpw(
                (post_data['password'].encode()), bcrypt.gensalt())
            new_user = User.objects.create(
                first_name=post_data['fname'],
                last_name=post_data['lname'],
                email=post_data['email'],
                password=pw_hash,
                bday=post_data['bday']
            )
            return new_user

        return errors

    def validate_login(self, post_data):
        errors = []
        if len(self.filter(email=post_data['email'])) == 1:
            user = self.filter(email=post_data['email'])[0]
            if not bcrypt.checkpw(post_data['password'].encode(), user.password.encode()):
                errors.append("Incorrect password")
        else:
            errors.append("Could not find User")
        if errors:
            return errors
        else:
            return user


class reviewManager(models.Manager):
    def validate_review(self, post_data, user):
        errors = []
        if len(post_data['title']) < 1 or len(post_data['review']) < 1:
            errors.append("Fields cannot be empty")
        if len(post_data['existing_author']) < 0 and len(post_data['new_author']) < 3:
            errors.append('new author names must 3 or more characters')
            print post_data['new_author']
        if post_data['existing_author'] != "" and post_data['new_author'] != "":
            errors.append("Cannot have two authors for one book")
        print errors
        if not errors:
            if post_data['new_author'] == "":
                author = Author.objects.get(name=post_data['existing_author'])
                print author
            else:
                author = Author.objects.create(name=post_data['new_author'])
            if not Book.objects.filter(title=post_data['title']):
                book = Book.objects.create(
                    title = post_data['title'],
                    author = author
                )
            else:
                book = Book.objects.get(title=post_data['title'])
                # print book Doesnt reach
            return self.create(
                review = post_data['review'],
                rating = post_data['rating'],
                book = book,
                reviewer = User.objects.get(id=user)
        )
            
    def recent_and_not(self):
        return (self.all().order_by('-created_at')[:3], self.all().order_by('-created_at')[3:])


class User(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    bday = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = userManager()

class Author(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.ForeignKey(Author, related_name="books")

    def __str__(self):
        return self.title


class Review(models.Model):
    review = models.TextField()
    rating = models.IntegerField()
    book = models.ForeignKey(Book, related_name="reviews")
    reviewer = models.ForeignKey(User, related_name="reviews_left")
    created_at = models.DateTimeField(auto_now_add=True)
    objects = reviewManager()

    def __str__(self):
        return "Book: {}".format(self.book.title)
