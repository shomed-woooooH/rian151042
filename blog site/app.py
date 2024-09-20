from flask import Flask, render_template, request, redirect, session
import json
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a random secret key

# Path to the user data file
USER_DATA_FILE = 'users.json'

def load_user_data():
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_user_data(data):
    with open(USER_DATA_FILE, 'w') as f:
        json.dump(data, f)

@app.route('/')
def index():
    username = session.get('username')
    if not username:
        return redirect('/login')

    # Load posts from the user's JSON file
    posts = []
    if os.path.exists(f"{username}_blogs.json"):
        with open(f"{username}_blogs.json", 'r') as f:
            posts = json.load(f)

    return render_template('index.html', username=username, posts=posts)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        users = load_user_data()
        if username in users and users[username] == password:
            session['username'] = username
            return redirect('/')
        return "Invalid credentials", 401

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        users = load_user_data()
        if username in users:
            return "Username already exists", 409
        
        users[username] = password
        save_user_data(users)
        
        # Create a new blog file for the user
        with open(f"{username}_blogs.json", 'w') as f:
            json.dump([], f)

        return redirect('/login')

    return render_template('register.html')

@app.route('/new', methods=['POST'])
def new_post():
    title = request.form['title']
    content = request.form['content']
    username = session['username']
    
    # Load existing posts
    with open(f"{username}_blogs.json", 'r') as f:
        posts = json.load(f)

    # Add the new post
    posts.append({'title': title, 'content': content})

    # Save back to the file
    with open(f"{username}_blogs.json", 'w') as f:
        json.dump(posts, f)

    return redirect('/')

@app.route('/post/<int:post_id>')
def view_post(post_id):
    username = session.get('username')
    if not username:
        return redirect('/login')

    # Load the posts from the user's JSON file
    with open(f"{username}_blogs.json", 'r') as f:
        posts = json.load(f)

    # Check if the post_id is valid
    if post_id < 0 or post_id >= len(posts):
        return "Post not found", 404

    # Get the specific post to display
    post = posts[post_id]
    
    return render_template('post.html', post=post)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)
