# Import flask stuff
from flask import Flask, render_template, redirect
from flaskext.mysql import MySQL

# Set up mysql connection later

app = Flask(__name__)

# Create route for home page
@app.route('/')
def index():
	return render_template('index.html')

@app.route('/register')
def register():
	return render_template('/register.html')

if __name__ == "__main__":
	app.run(debug=True)