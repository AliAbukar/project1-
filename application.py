import os
import requests
import json
from flask import Flask, session, render_template, request, flash, redirect, url_for, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)
session
# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.secret_key = os.getenv('SECRET')
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))



@app.route("/")
def index():

    return render_template("index.html")

@app.route("/login", methods = ['POST', 'GET'])
def login():
    username = request.form.get("username")
    password = request.form.get("password")
    currentUser = request.form.get("username")
    if request.method == 'POST':
        if db.execute("SELECT *FROM users WHERE username = :username AND password = :password",{"username" :username, "password" :password}).rowcount==0:
            return render_template("login.html", message = ("Wrong username or password"))
        else:
            session['logged_in'] = True
            session['user_id'] = username
            return render_template("search.html", username = session['user_id'])
    return render_template("login.html")

@app.route("/register", methods = ['POST', 'GET'])
def signup():
    username = request.form.get("username")
    password = request.form.get("password")
    currentUser = request.form.get("username")
    newuser = db.execute('SELECT *FROM users WHERE username = :username', {"username" :username})

    if request.method== "POST":
        if newuser.rowcount==1:
            return render_template('signup.html', message='User already exists!!')
        else:
            db.execute('INSERT INTO users (username, password) VALUES (:username, :password)',{"username": username, "password": password})
            db.commit()
            session['logged_in'] = True
            session['user_id'] = username
            return render_template('search.html', username = session['user_id'] ,message = " Welcome, You are logged in!")

    return render_template("signup.html")


@app.route('/search', methods=['GET','POST'])
def search():
    if request.method == "POST":
        searchQuery = request.form.get("searchQuery")
        session['searchedFor'] = searchQuery
        searchResult = db.execute("SELECT isbn, author, title FROM books WHERE isbn iLIKE '%"+searchQuery+"%' OR author iLIKE '%"+searchQuery+"%' OR title iLIKE '%"+searchQuery+"%'").fetchall()
        print("searchQuery")

        session["books"] = []
        noResult = db.execute("SELECT isbn, author, title FROM books WHERE isbn iLIKE '%"+searchQuery+"%' OR author iLIKE '%"+searchQuery+"%' OR title iLIKE '%"+searchQuery+"%'")
        if noResult.rowcount==0:
            message = "No result was found"
            return render_template("results.html", message = message)
        for row in searchResult:
            book = dict()
            book["isbn"] = row[0]
            book["author"] = row[1]
            book["title" ] = row[2]

            session["books"].append(book)
        return render_template("results.html", username=session['user_id'], searchedFor=searchQuery, books=session["books"])

    return render_template('search.html', username=session['user_id'])


@app.route("/book/<isbn>", methods=['GET','POST'])
def book(isbn):
    book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchone()
    book_id = db.execute("SELECT book_id FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchone()
    session['book_id'] = book_id
    bid = book_id[0]
    username = session['user_id']
    user_id = db.execute('SELECT user_id FROM users WHERE username=:username',{'username':username}).fetchone()
    uid = user_id[0]
    
    print(uid)
    print(bid)
    if session['user_id'] is None:
        session['logged_in'] = False
        return render_template("login.html", message="You loggin  first!!")
    if book is None:
        return render_template("error.html", message="book does not exist")
    if request.method == "GET":
        # Processing the json data
        res = requests.get("https://www.goodreads.com/book/review_counts.json",
                        params={"key": "zDJmGLJmkc694O9VI0w0qQ", "isbns": book.isbn}).json()["books"][0]
        ratings_count = res["ratings_count"]
        average_rating = res["average_rating"]

        reviews = db.execute('SELECT scale, comments, users.user_id, username FROM users JOIN bookreview ON (users.user_id = bookreview.user_id) WHERE bookreview.book_id = :bid;', {'bid': bid}).fetchall()
        users = []
        
        return render_template("book.html", book=book, users=users,review=reviews,
                            ratings_count=ratings_count, average_rating=average_rating, username=session["user_id"])
    if request.method=='POST':
        rating = request.form.get('rating')
        comment= request.form.get('comment')
        if db.execute('SELECT * from bookreview where user_id=:uid AND book_id=:bid',{"uid":uid, 'bid':bid}).rowcount==1:
            return render_template('error.html', message='You cannot submit a review twice for the same book, Please go back to the previous page')
        else:
            db.execute('insert into bookreview (user_id,book_id,scale,comments) VALUES (:uid,:bid,:rating, :comment)',{'uid':uid, 'bid':bid, 'rating':rating, 'comment':comment})
            db.commit()
            return redirect(url_for('book', isbn=book.isbn))

# Page for the website's API
@app.route("/api/<isbn>", methods=["GET"])
def api(isbn):

    bdata = db.execute("SELECT * FROM books WHERE isbn = :bisbn", {"bisbn": isbn}).fetchone()
    if bdata is None:
        return "No Such A Book in the Database", 404
    bookid = db.execute("SELECT book_id from books where isbn =:isbn",{"isbn":isbn}).fetchone()


    numOfRatings = db.execute("SELECT COUNT (*) FROM bookreview WHERE book_id = :book_id", {"book_id": bookid.book_id}).fetchone()
    averageRating = db.execute("SELECT AVG (scale) FROM bookreview WHERE book_id = :book_id", {"book_id": bookid.book_id}).fetchone()

    app.logger.debug(f'numOfRatings type is {type(numOfRatings)}, value is {numOfRatings}')
    app.logger.debug(f'averageRating type is {type(averageRating)}, value is {averageRating}')

    response = {}
    response['title'] = bdata.title 
    response['author'] = bdata.author
    response['year'] = bdata.year
    response['isbn'] = bdata.isbn
    response['review_count'] = str(numOfRatings[0])
    response['average_score'] = '% 1.1f' % averageRating[0]

    json_response = json.dumps(response)

    return json_response, 200



@app.route("/profile")
def profile():
    flash ("Hello, Profile!!")
    return render_template("profile.html", username= session['user_id'])

@app.route("/logout")
def logout():
    flash ("")

    session['logged_in'] = False
    return render_template("index.html")

if __name__ == "__main__":
    app.run()
