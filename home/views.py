from bson import ObjectId
from django import db
from django.shortcuts import render,HttpResponse,redirect
from django.contrib.sessions.models import Session
from django.contrib.auth.models import User
from django.contrib import messages
from datetime import datetime,timedelta,date
from .models import IssueBook, UserExtend,AddBook,ReturnBook,AddStudent,person_collection,student_collection,book_collection,issue_book,user_collection
from django.http import HttpResponse
from django.contrib.auth import authenticate ,logout
from django.contrib.auth import login as dj_login

def index(request):
    return render(request,'index.html')
def staff(request):
    return render(request,'staff.html')
def add_person(request):
    records = { 
        "first_name": "John",
        "lastPname": "smith"
    }
    person_collection.insert_one(records)
    return HttpResponse("New Person is Added")
    
def getAllPersons(request):
    persons = person_collection.find()
    return HttpResponse(persons)

def stafflogin(request):
    if request.session.has_key('is_logged'):
        return redirect('dashboard')
    return render(request,'stafflogin.html')
def staffsignup(request):
    return render(request,'staffsignup.html')
def dashboard(request):
    if request.session.has_key('is_logged'):
        #Book = AddBook.objects.all()
        Book = book_collection.find()
        # Convert ObjectId to string for use in the template
        books = [{'id': int(str(book['id'])), 'bookid': book['bookid'], 'bookname': book['bookname'], 'subject': book['subject'], 'category': book['category']} for book in Book]
        return render(request,'dashboard.html',{'books': books})
    return redirect('stafflogin')
def addbook(request):
    Book = book_collection.find()
    return render(request,'addbook.html',{'Book':Book})

def SignupBackend(request):
    if request.method =='POST':
        uname = request.POST.get("uname")
        fname = request.POST.get("fname")
        lname = request.POST.get("lname")
        email = request.POST.get("email")
        phone = request.POST.get('phone')
        password = request.POST.get('password')

        # Check if username already exists
        if user_collection.find_one({"username": uname}):
            messages.error(request, "Username already taken. Please try another.")
            return redirect("staffsignup")

        # Validate username length
        if len(uname) > 15:
            messages.error(request, "Username must be max 15 characters.")
            return redirect("staffsignup")

        # Validate if username contains only letters and numbers
        if not uname.isalnum():
            messages.error(request, "Username should only contain letters and numbers.")
            return redirect("staffsignup")
        
        id_field = user_collection.find()
        #document_list = list(id_field)
        userId = 1
        id_values = [doc['userid'] for doc in id_field]
        userId = max(id_values) + 1
        # id_values = [doc['userid'] for doc in id_field]
        # print('id Field',id_field)
        # id_field = user_collection.find({}, {"userid": 1})
        # id_values = [doc['userid'] for doc in id_field]
        # max_id = max(id_values)

        # Create the user
        user = {
            "userid" : userId,
            "username": uname,
            "first_name": fname,
            "last_name": lname,
            "email": email,
            "password": password
        }
        user_id = user_collection.insert_one(user).inserted_id

        if user_id:
            messages.success(request, "Your account has been successfully created.")
            return redirect("stafflogin")
        else:
            messages.error(request, "Failed to create user account. Please try again.")
            return redirect("staffsignup")
    else:
        return redirect("staffsignup")
    
def LoginBackend(request):
    if request.method == 'POST':
        loginuname = request.POST.get("loginuname")
        loginpassword = request.POST.get("loginpassword")
        
        # Query the MongoDB collection for the provided username
        user = user_collection.find_one({'username': loginuname})
        
        if user and user['password'] == loginpassword:
            # If user is found and password matches, set session variables and redirect to dashboard
            request.session['is_logged'] = True
            request.session["user_id"] = str(user['_id'])
            messages.success(request, "Successfully logged in")
            return redirect('dashboard')
        else:
            # If authentication fails, redirect to homepage with error message
            messages.error(request, "Invalid Credentials, Please try again")
            return redirect("stafflogin")
    else:
        # Handle GET requests (e.g., navigating to the login page)
        return render(request, 'login.html')

def AddBookSubmission(request):
    if request.session.has_key('is_logged'):
        if request.method == "POST":
            user_id = 1
            user1 = User.objects.get(id=user_id)
            bookid = request.POST["bookid"]
            bookname = request.POST["bookname"]
            subject = request.POST["subject"]
            category=request.POST["category"]
            add = AddBook(user=user1,bookid=bookid,bookname=bookname,subject=subject,category=category)
            add.save()
            Book = book_collection.find()
        # Convert ObjectId to string for use in the template
            books = [{'id': int(str(book['id'])), 'bookid': book['bookid'], 'bookname': book['bookname'], 'subject': book['subject'], 'category': book['category']} for book in Book]
            return render(request,'dashboard.html',{'books': books})
            
    return redirect('/')
def deletebook(request, id):
    if request.session.has_key('is_logged'):
        result = book_collection.delete_one({'id': id})
        return redirect('dashboard')
    return redirect('login')
def bookissue(request):
    return render(request,'bookissue.html')
def returnbook(request):
    return render(request,'returnbook.html')
def HandleLogout(request):
        del request.session['is_logged']
        del request.session["user_id"] 
        logout(request)
        messages.success(request, " Successfully logged out")
        return redirect('dashboard')

def issuebooksubmission(request):
       if request.method == 'POST':
        user_id = 1
        student_id = request.POST['studentid']
        book_id = request.POST['book1']

        book = book_collection.find_one({'bookid': book_id})
        
        if book:
            if book['category'] == "Not-Issued":
                # Set the category to "Issued" for the book in MongoDB
                book_collection.update_one({'bookid': book_id}, {'$set': {'category': 'Issued'}})
                
                # Save the issue record in MongoDB
                issue_date = datetime.now()
                expiry_date = issue_date + timedelta(days=15)  # Assuming a 15-day issue period
                issue_record = {
                    'user_id': (user_id),
                    'student_id': student_id,
                    'book_id': (book_id),
                    'issuedate': issue_date,
                    'expirydate': expiry_date
                }
                issue_book.insert_one(issue_record)
                
                messages.success(request, "Book issued successfully.")
            else:
                messages.error(request, "Book already issued.")
        else:
            messages.error(request, "Book not found.")
            
       return redirect('dashboard')
       
def returnbooksubmission(request):
    if request.method == 'POST':
        if True:
            user_id = 1
            book_id = request.POST.get('bookid2')
            
            # Check if the user_id exists and retrieve the corresponding User instance
            try:
                user_instance = User.objects.get(id=user_id)
            except User.DoesNotExist:
                messages.error(request, "User does not exist.")
                return redirect('login')  # Redirect to login page if user does not exist
            
            # Assuming you have a MongoDB collection for AddBook
            book = book_collection.find_one({'bookid': book_id})
            print('book from db',book)
            if book and book['category'] == "Issued":
                # Update category in AddBook collection
                book_collection.update_one({'bookid': book_id}, {'$set': {'category': "Not-Issued"}})
                
                # Delete entry from IssueBook collection
                issue_book.delete_one({'book_id': book_id})
                
                # Save entry in ReturnBook collection with the correct User instance
                return_book = ReturnBook(user=user_instance, bookid2=book_id)
                return_book.save()
                
                messages.success(request, "Book returned successfully!")
            else:
                messages.error(request, "Book is not issued!")
        else:
            messages.error(request, "User is not logged in!")
            return redirect('login')  # Redirect to login page if user is not logged in

        # Fetch all entries from ReturnBook collection
        return_books = list(ReturnBook.objects.all())
        return render(request, 'returnbook.html', {'Return': return_books})

    return redirect('/')

def Search(request):
    if request.session.has_key('is_logged'):
        query2=request.GET["query2"]
        Book=AddBook.objects.filter(bookid__icontains=query2)
        params={'Book':Book}
        return render(request,'dashboard.html',params)
    return redirect("login") 
# def editbookdetails(request,id):
#     if request.session.has_key('is_logged'):
#         Book = book_collection.find_one({'_id': id})
#         return render(request,'editdetails.html',{'Book':Book})
#     return redirect('login')
def editbookdetails(request, id):
    if request.session.has_key('is_logged'):
        book = book_collection.find_one({'id': id})
        return render(request, 'editdetails.html', {'Book': book})
    return redirect('login')
def updatedetails(request,id):
    if request.session.has_key('is_logged'):
        if request.method == "POST":
            # Retrieve the book document from MongoDB based on its _id
            book = book_collection.find_one({'id': id})
            if book:
                # Update the fields of the book document
                book_collection.update_one({'id': id}, {'$set': {
                    'bookid': request.POST["bookid"],
                    'bookname': request.POST["bookname"],
                    'subject': request.POST["subject"],
                    'category': request.POST["category"]
                }})
                return redirect("dashboard")
            else:
                # Handle the case where the book document with the specified _id does not exist
                messages.error(request, "Book with the specified ID does not exist.")
        else:
            # Handle the case where the request method is not POST
            messages.error(request, "Invalid request method.")
    else:
        # Handle the case where the user is not logged in
        return redirect('login')

def addstudent(request):
    if request.session.has_key('is_logged'):
       return render(request,'addstudent.html')
    return redirect ('login')

def viewstudents(request):
    if request.session.has_key('is_logged'):
        #Student=AddStudent.objects.all()
        Student = student_collection.find()
        return render(request,'viewstudents.html',{'Student':Student})
    return redirect('stafflogin')

def Searchstudent(request):
    if request.session.has_key('is_logged'):
        query3=request.GET["query3"]
        Student=AddStudent.objects.filter(studentid__icontains=query3)
        params={'Student':Student}
        return render(request,'viewstudents.html',params)
    return redirect("stafflogin") 

def addstudentsubmission(request):
    if request.session.has_key('is_logged'):
        if request.method == "POST":
            user_id = 1
            user1 = User.objects.get(id=user_id)
            sname = request.POST["sname"]
            studentid = request.POST["studentid"]
            add = AddStudent(user = user1,sname=sname,studentid=studentid)
            add.save()
            Student = AddStudent.objects.all()
            return render(request,'addstudent.html',{'Student':Student})
    return redirect('/')

def viewissuedbook(request):
    if request.session.has_key('is_logged'):
        # Retrieve all issued book records from the MongoDB collection
        issued_books = issue_book.find()

        # Initialize an empty list to store book details
        lis = []

        # Iterate over each issued book record
        for book in issued_books:
            # Extract relevant information from the MongoDB document
            student_id = book['student_id']
            book_id = book['book_id']
            issue_date = book['issuedate']
            expiry_date = book['expirydate']

            # Fetch additional details of the student and book from their respective collections
            student = student_collection.find_one({'studentid': student_id})
            book_details = book_collection.find_one({'bookid': book_id})

            # Calculate fine (assuming 15 days issue period)
            days_issued = (datetime.now() - issue_date).days
            fine = max(0, days_issued - 15) * 10

            # Create a tuple with the extracted information
            if student and book_details:
                info = (
                    student['sname'],
                    student_id,
                    book_details['bookname'],
                    book_details['subject'],
                    issue_date.strftime('%d-%m-%Y'),
                    expiry_date.strftime('%d-%m-%Y'),
                    fine
                )
                print(info)

                # Append the tuple to the list
                lis.append(info)

        # Render the template with the list of book details
        return render(request, 'viewissuedbook.html', {'lis': lis})
    
    # Redirect to login if the user is not logged in
    return redirect('/')
