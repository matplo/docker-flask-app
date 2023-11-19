from flask import Flask
from flask_flatpages import FlatPages
from flask_bootstrap import Bootstrap
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask import render_template, request, redirect, url_for, flash

import os, sys
import inspect
# Get the directory of the current file
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.append(current_dir)
## Combine with the relative path to the templates folder
#template_dir = os.path.join(current_dir, app.template_folder)
#print("Absolute path of the template folder:", template_dir)

# app = Flask(__name__)
app = Flask("docker.flask", template_folder=os.path.join(current_dir, 'templates'))
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['FLATPAGES_EXTENSION'] = '.md'
app.config['FLATPAGES_ROOT'] = os.path.join(current_dir, 'pages')
app.config['USER_DB_CONFIG'] = os.path.join(current_dir, 'user_db_config.yaml')
flatpages = FlatPages(app)
print('number of pages:', len([p for p in flatpages]))
for p in flatpages:
	print(p)
bootstrap = Bootstrap(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # The name of the login route

from user_util import User, UserStorage
users = UserStorage(app)

from flask_login import AnonymousUserMixin
class Anonymous(AnonymousUserMixin):
    def __init__(self):
        self.username = 'Guest'
# Set the anonymous user class in the login manager
login_manager.anonymous_user = Anonymous

# Routes and views
@app.route('/')
@app.route('/index')
@app.route('/home')
def index():
    page = flatpages.get_or_404('index')
    # print('current user :: username = ', current_user.username, file=sys.stderr)
    return render_template('page.html', page=page)


@login_manager.user_loader
def load_user(user_id):
    return users.get_user(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = users.get_user(username)

        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password')

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/page/<path:path>/')
@login_required
def page(path):
    page = flatpages.get_or_404(path)
    return render_template('page.html', page=page)


@app.route('/protected')
@login_required
def protected():
    return "This is a protected page."


@app.errorhandler(404)
def page_not_found(e):
    # Note the 404 after render_template
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True)
