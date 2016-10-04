#Bawk (Social Post) App

##Overview of the Project
Collaborators:
PirieD704 - http://www.github.com/PirieD704
jttwnsnd

This is a simple Yik Yak/Twitter type clone. The app allows the user to register/login, it hashes the password using bcrypt, and displays the "bawks" of the user's followers. THe user can follow other users, and view the profile.

##TEchnologies in use
* HTML
* CSS
* Bootstrap
* Javascript
* AJAX
* Compass/SASS
* Python
* Flask
* Jinja
* MySQL

##Local Installation Requirements
```pip install flask flask-mysql bcrypt```

##URL to Live Demo

##Challenges & Solutions
We found that approaching this as a mobile first, back-end app meant our approach needed to consist of view-checking, and design choices that are optimal for both views. In the case with our ```textarea``` where the user can insert their post, an original view consisted of being too wide. We utilized Bootstraps ```hidden-*``` classes to allow certain sizes of these views to appear at certain sizes.