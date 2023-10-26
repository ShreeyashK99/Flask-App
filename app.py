from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from flask import jsonify

app = Flask(__name__)
app.secret_key = "supersecretkey"

app.config["MONGO_URI"] = "mongodb://localhost:27017/flask_signup_login_db"
mongo = PyMongo(app)

ADMIN_USERNAME = "Shreek"
ADMIN_PASSWORD = "sh12345"

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

        return render_template('success_signup.html')

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        users = mongo.db.users
        login_user = users.find_one({'username': request.form['username']})

        if login_user and login_user['password'] == request.form['password']:
            return render_template('user_dashboard.html', username=request.form['username'])

        flash('Invalid credentials!')
    return render_template('login.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            return redirect(url_for('admin_dashboard'))

        flash('Invalid admin credentials!')

    return render_template('admin_login.html')

@app.route('/admin/add_item', methods=['POST'])
def add_item():
    items = mongo.db.items
    existing_item = items.find_one({'name': request.form['item_name']})

    if existing_item:
        flash('Item already exists!')
        return redirect(url_for('admin_dashboard'))

    items.insert_one({
        'name': request.form['item_name'],
        'price': request.form['item_price']
    })

    flash('Item added successfully!')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/dashboard')
def admin_dashboard():
    items = list(mongo.db.items.find())
    return render_template('admin_dashboard.html', items=items)

@app.route('/users')
def list_users():
    users = mongo.db.users.find()
    return render_template('list_users.html', users=users)

@app.route('/users/update/<user_id>', methods=['GET', 'POST'])
def update_user(user_id):
    user = mongo.db.users.find_one_or_404({"_id": ObjectId(user_id)})
    if request.method == 'POST':
        mongo.db.users.update_one(
            {"_id": ObjectId(user_id)},
            {
                "$set": {
                    'fullname': request.form['fullname'],
                    'email': request.form['email'],
                    'username': request.form['username'],
                    'password': request.form['password']
                }
            }
        )
        flash('User updated successfully!')
        return redirect(url_for('list_users'))
    return render_template('edit_user.html', user=user)

@app.route('/users/delete/<user_id>')
def delete_user(user_id):
    mongo.db.users.delete_one({"_id": ObjectId(user_id)})
    flash('User deleted successfully!')
    return redirect(url_for('list_users'))

@app.route('/logout/<user_type>', methods=['POST'])
def logout(user_type):
    if user_type == "admin":
        flash('Admin has been logged out!')
        return render_template('admin_logout.html')
    else:
        flash('User has been logged out!')
        return render_template('user_logout.html')

@app.route('/api/users', methods=['GET'])
def get_all_users():
    users = mongo.db.users.find()
    user_list = []
    for user in users:
        user_data = {
            'id': str(user['_id']),
            'fullname': user['fullname'],
            'email': user['email'],
            'username': user['username']
        }
        user_list.append(user_data)
    
    return jsonify(user_list)

if __name__ == '__main__':
    app.run(debug=True)
