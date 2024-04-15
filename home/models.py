from django.db import models
from django.contrib.auth.models import User
from django.db.models.fields import CharField
from datetime import datetime,timedelta
from .db_connection import db

class UserExtend(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    phone = models.IntegerField()
    def __str__(self):
       return self.user.username
    
book_collection = db['Book']    
class AddBook(models.Model):
    user = models.ForeignKey(User,default = 1, on_delete=models.CASCADE)
    bookid = models.CharField(max_length=10)
    bookname = models.CharField(max_length=50)
    subject = models.CharField(max_length=20)
    category = models.CharField(max_length=10)
    id_field = book_collection.find()

    def save(self, *args, **kwargs):
        book_collection = db['Book']
        book_data = {
            'id' : self.bookid,
            'user': 1,
            'bookid': self.bookid,
            'bookname': self.bookname,
            'subject': self.subject,
            'category': self.category,
        }
        book_collection.insert_one(book_data)
        super(AddBook, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.bookname} [{self.bookid}]"

def expiry():
    return datetime.today() + timedelta(days=15)

issue_book = db['IssueBook']
user_collection = db['UserDetails']
class IssueBook(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    studentid=CharField(max_length=20)
    book1=models.CharField(max_length=20)
    issuedate=models.DateField(auto_now=True)
    expirydate=models.DateField(default=expiry)
    def __str__(self):
        return self.studentid

class ReturnBook(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    bookid2=models.CharField(max_length=20)

student_collection = db['Student']
 
class AddStudent(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    sname = models.CharField(max_length=30)
    studentid = models.CharField(max_length=20)

    def save(self, *args, **kwargs):
        student_data = {
            'sname': self.sname,
            'studentid': self.studentid
        }
        student_collection.insert_one(student_data)
        super(AddStudent, self).save(*args, **kwargs)

    def __str__(self):
        return self.sname + '[' + str(self.studentid) + ']'
    
person_collection = db['Person']
# student_list = db['Student']