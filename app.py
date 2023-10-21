from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_pymongo import PyMongo

app = Flask(__name__)
app.secret_key = "supersecretkey" 


app.config["MONGO_URI"] = "mongodb://localhost:27017/flask_signup_login_db"
mongo = PyMongo(app)


ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "adminpassword"

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        users = mongo.db.users
        existing_user = users.find_one({'username': request.form['username']})

        if existing_user:
            flash('Username already exists!')
            return redirect(url_for('signup'))

        users.insert_one({
            'fullname': request.form['fullname'],
            'email': request.form['email'],
            'username': request.form['username'],
            'password': request.form['password'] 
        })
        
        flash('Successfully signed up!')
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        users = mongo.db.users
        login_user = users.find_one({'username': request.form['username']})

        if login_user and login_user['password'] == request.form['password']:
            flash('Logged in successfully!')
            return redirect(url_for('login'))
            
        flash('Invalid credentials!')
        return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            flash('Admin logged in successfully!')
            return redirect(url_for('admin_dashboard'))

        flash('Invalid admin credentials!')
        return redirect(url_for('admin_login'))

    return render_template('admin_login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    users = mongo.db.users.find()
    return render_template('admin_dashboard.html', users=users)

@app.route('/api/users', methods=['GET'])
def get_all_users():
    users = mongo.db.users.find()
    user_data = []
    
    for user in users:
        user_data.append({
            'fullname': user['fullname'],
            'email': user['email'],
            'username': user['username']
        })
        
    return jsonify(user_data)

if __name__ == '__main__':
    app.run(debug=True)
