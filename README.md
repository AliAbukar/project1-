# Project 1

Web Programming with Python and JavaScript

DATABASE_URL=postgres://ligpqfmaxvdhfc:c9683e2b3b435c05a9f22586d7f60a9c37edb896df02e5d29415d298f82f1567@ec2-54-83-9-169.compute-1.amazonaws.com:5432/d6p6b3nnl8j6gp

In project we have:
    templates : contains the the html files of the projects
    import.py : contains the code to import books.cvs to the database
    application.py : contains the routes of the project

In templates we have eight page html:-
    Error.html  : to handle all errors, to not let the website crash
    layout.html : contains common layout and links
    index.html  : shows the homepage
    login.html  : shows the login form
    signup.html : shows the signup page
    search.html : to handle searches, isbn, title, author
    results.html: to display the search that was made
    book.html   : to display about the book from the search results "http://covers.openlibrary.org/a/      
  		  $key/ $value-$size.jpg" used this api to get cover of the books for their isbn

In this project1, i built a book review website. 
Users will be able to register for my website and 
then log in using their username and password.When users log in,
they will be able to search for books,leave comments for individual books,
and see the reviews made by other people. 
I also used the a third-party API by Goodreads, another book review website, 
to pull in ratings from a broader audience.
Logout page:-Logged in users will be able to log out of the website.
Finally, users will be able to get the reselts for book details and 
book reviews via your website’s API.
