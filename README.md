# Dunder-Mifflin-Web-Application
This repository is a fully-responsive web application created using Flask, MySQL, and Bootstrap/Jquery. Created originally as a final project for CIS 451 at the University of Oregon, this application simulates MySQL data interactions using a powerful and clean user interface.

### How does it work?
View the diagram below for a basic overview of the application. Essentially, the application is deployed on Heroku's free hosting service. Gunicorn provides the HTTPS WSGi interface for interfacing with Flask. The Flask application, a Python web framework, handles the core logic of the application, connecting to a guest account on a MySQL server hosted on ix-dev at the University of Oregon. It queries and parses the database to handle user requests, which are served either directly through AJAX calls or Flask render templates.

![diagram](https://raw.githubusercontent.com/jens-johnson/Dunder-Mifflin-Web-Application/master/static/images/diagram.png)
