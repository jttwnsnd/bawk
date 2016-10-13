# Import flask stuff
from flask import Flask, render_template, redirect, request, session, jsonify
from flaskext.mysql import MySQL
import bcrypt

#create an instance of the mysql class
mysql = MySQL()
app = Flask(__name__)
#add to the app (Flask object) some config data for our connection
app.config['MYSQL_DATABASE_USER'] = 'x'
app.config['MYSQL_DATABASE_PASSWORD'] = 'x'
#The name of the database we want to connect to at the DB server
app.config['MYSQL_DATABASE_DB'] = 'bawk'
app.config['MYSQL_DATABASE_HOST'] = '127.0.0.1'
# user the mysql object's method "init_app" and pass it the flask object
mysql.init_app(app)
conn = mysql.connect()
#set up a cursor object, which is what the sql uses to connect and run queries
cursor = conn.cursor()
#session secret key
app.secret_key = 'asdf&&^(*ahasfljhas'

# Create route for home page
@app.route('/')
def index():
	# if session['id']:
	get_bawks_query = "SELECT b.id, b.post_content, b.current_vote, u.username, u.avatar FROM bawks AS b INNER JOIN user AS u ON b.uid = u.id  WHERE 1 GROUP BY id DESC"
	cursor.execute(get_bawks_query)
	get_bawks_result = cursor.fetchall()
	if get_bawks_result is not None:
		return render_template('index.html', bawks = get_bawks_result)
	else:
		return render_template('index.html', message = "No bawks yet!")
	if request.args.get('username'):
		#the username variable is set in the query string
		return render_template('register.html', message="That username is already taken")
	else:
		return render_template('index.html')
	# else:
	# 	get_bawks_query = "SELECT b.id, b.post_content, b.current_vote, u.username, u.avatar FROM bawks AS b INNER JOIN user AS u ON b.uid = u.id  WHERE 1"
	# 	cursor.execute(get_bawks_query)
	# 	get_bawks_result = cursor.fetchall()
	# 	if get_bawks_result is not None:
	# 		return render_template('index.html', bawks = get_bawks_result)

@app.route('/register')
def register():
	return render_template('/register.html')

@app.route('/register_submit', methods=['POST'])
def register_submit():
	# first, check to see if the username already exists. SELECT statement.
	check_username_query = "SELECT * FROM user where username = '%s'" % request.form['username']
	cursor.execute(check_username_query)
	check_username_result = cursor.fetchone()
	# second, if it't not taken, then insert the username into mysql
	if (check_username_result is None):
		# no match. insert
		session['username'] = request.form['username']
		real_name = request.form['real_name']
		username = request.form['username']
		password = request.form['password'].encode('utf-8')
		hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())
		email = request.form['email']
		username_insert_query = "INSERT INTO user VALUES (DEFAULT, %s, %s, %s, %s, NULL)"
		cursor.execute(username_insert_query, (real_name, username, hashed_password, email))
		conn.commit()
		get_id_query = "SELECT id FROM user where username = '%s'" % request.form['username']
		cursor.execute(get_id_query)
		get_id_result = cursor.fetchone()
		session['id'] = get_id_result[0]
		return render_template('index.html')
	else:
		# second b, if it is taken, send them back to the register page with a message
		return redirect('/register?username=taken')
@app.route('/login')
def login():
	return render_template('login.html')

@app.route('/login_submit', methods=['POST'])
def login_submit():
	password = request.form['password']
	username = request.form['username']
	check_password_query = "SELECT password, id FROM user where username = '%s'" % request.form['username']
	cursor.execute(check_password_query)
	hashed_password_from_mysql = cursor.fetchone()
	# to check a hash against english:
	if bcrypt.hashpw(password.encode('utf-8'), hashed_password_from_mysql[0].encode('utf-8')) == hashed_password_from_mysql[0].encode('utf-8'):
		#we have a match
		session['username'] = request.form['username']
		session['id'] = hashed_password_from_mysql[1]
		return render_template('index.html')
	else:
		return redirect('/login?message=incorrect_password')

@app.route('/logout')
def logout():
	session.clear()
	return redirect('/?message=logged_out')

@app.route('/<username>')
def user_page(username):
	return render_template('user_landing.html')

@app.route('/post_submit', methods=["POST"])
def post_submit():
	# pull the post from the form
	post_content = request.form['post_content']
	# get the id of the user to keep track of who posted what
	get_user_id = "SELECT id FROM user WHERE username = '%s'" % session['username']
	cursor.execute(get_user_id)
	get_user_id_result = cursor.fetchone()
	user_id = get_user_id_result[0]
	# insert post into the MySQL
	post_content_query = "INSERT INTO bawks (post_content, uid, current_vote) VALUES ('"+post_content+"', "+str(user_id)+", 0)"
	cursor.execute(post_content_query)
	conn.commit()
	return redirect('/')

@app.route('/home')
def home():
	return 'home.html'
@app.route('/process_vote', methods=['POST'])
def process_vote():
	pid = request.form['vid'] # this came from jquery $.ajax
	vote_type = request.form['voteType']
	print pid
	username = session['username']
	uid = session['id']
	check_user_votes = "SELECT * FROM votes WHERE votes.uid = '%s' AND votes.pid = '%s'" % (uid, pid)
	cursor.execute(check_user_votes)
	votes = cursor.fetchone()
	print votes
	print check_user_votes
	# it's possible we get none back because the user hasn't voted on this post
	if votes is None:
		# user hasn't voted, insert
		insert_user_vote_query = "INSERT INTO votes (pid, uid, vote_type) VALUES (%s, %s, %s)" % (pid, session['id'], vote_type)
		cursor.execute(insert_user_vote_query)
		conn.commit()
		print insert_user_vote_query
		get_new_total_query = "SELECT sum(vote_type) as vote_total FROM votes WHERE pid = '%s' GROUP BY pid" % pid
		cursor.execute(get_new_total_query)
		get_new_total_result = cursor.fetchone()
		update_count_query = "UPDATE bawks SET current_vote = %s WHERE id = '%s'" % (get_new_total_result[0], pid)
		cursor.execute(update_count_query)
		conn.commit()
		return jsonify({'message': 'voteCounted', 'vote_total': int(get_new_total_result[0])})
	else: #have they voted and
		checkuser_vote_direction_query = "SELECT * FROM votes INNER JOIN user ON user.id = votes.uid WHERE user.username = '%s' AND votes.pid = '%s' and votes.vote_type = '%s'" % (session['username'], pid, vote_type)
		cursor.execute(checkuser_vote_direction_query)
		check_user_vote_direction_result = cursor.fetchone()
		if check_user_vote_direction_result is None:
			update_user_vote_query = "UPDATE votes SET vote_type = %s WHERE uid = '%s' and pid = '%s'" % (vote_type, session['id'], pid)
			cursor.execute(update_user_vote_query)
			conn.commit()
			get_new_total_query = "SELECT sum(vote_type) as vote_total FROM votes WHERE pid = '%s' GROUP BY pid" % pid
			cursor.execute(get_new_total_query)
			get_new_total_result = cursor.fetchone()
			update_count_query = "UPDATE bawks SET current_vote = %s WHERE id = '%s'" % (get_new_total_result[0], pid)
			print get_new_total_result
			print update_count_query
			cursor.execute(update_count_query)
			conn.commit()
			return jsonify({'message': 'voteChanged', 'vote_total': int(get_new_total_result[0])})
		else:
			print votes
			return jsonify({'message':'alreadyVoted'})

	# 	if: #are changing it

	# 	else: #are voting the same, no go.
	
	# return 'good'
@app.route('/follow')
def follow():
	# get_all_not_me_users_query = "SELECT * FROM user WHERE id != '%s'" % session['id']
	get_all_not_me_users_query = "SELECT * FROM user WHERE id != '%s'" % session['id']
	cursor.execute(get_all_not_me_users_query)
	get_all_not_me_users_result = cursor.fetchall()
	# who is the user following.
	# we want the username and id

	get_all_following_query = "SELECT u.username, f.uid_of_user_being_followed FROM follow f Left Join user u ON u.id = f.uid_of_user_being_followed where f.uid_of_user_following = '%s'" % session['id']
	cursor.execute(get_all_following_query)
	get_all_following_result = cursor.fetchall()
	get_all_not_following_query = "SELECT * FROM user WHERE id NOT IN (SELECT uid_of_user_being_followed FROM follow WHERE uid_of_user_following = '%s') and id != '%s'" % (session['id'], session['id'])
	cursor.execute(get_all_not_following_query)
	get_all_not_following_result = cursor.fetchall()
	return render_template('follow.html', following_list = get_all_following_result, not_following_list = get_all_not_following_result)
	# return "hi"

@app.route('/follow_user')
def follow_user():
	user_id_to_follow = request.args.get('user_id')
	follow_query = "INSERT INTO follow (uid_of_user_being_followed, uid_of_user_following) VALUES ('%s', '%s')" % (user_id_to_follow, session['id'])
	cursor.execute(follow_query)
	conn.commit()
	return redirect('/follow')

@app.route('/unfollow_user')
def unfollow_user():
	user_id_to_unfollow = request.args.get('user_id')
	follow_query = "DELETE FROM follow WHERE uid_of_user_being_followed = '%s' AND uid_of_user_folliwng = '%s'" % (user_id_to_unfollow, session['id'])
	cursor.execute(follow_query)
	conn.commit()
	return redirect('/follow')

if __name__ == "__main__":
	app.run(host='0.0.0.0')