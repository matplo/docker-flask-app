from flask import render_template
from app import app

# Routes and views
@app.route('/')
def index():
	return render_template('page.html', page="HOME")

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Assume you have a form with 'username' and 'password'
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Validate credentials
        # If valid:
        user = User() # Create a User object
        login_user(user)
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/logout')
def logout():
	return render_template('page.html', page="LOGOUT")

@app.route('/page/<path:path>/')
def page(path):
    page = flatpages.get_or_404(path)
    return render_template('page.html', page=page)

@app.route('/protected')
@login_required
def protected():
    return "This is a protected page."
