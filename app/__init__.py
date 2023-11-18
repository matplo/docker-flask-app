from flask import Flask, render_template
from flask_flatpages import FlatPages
from flask_bootstrap import Bootstrap
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user

app = Flask(__name__)
from app import views
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['FLATPAGES_EXTENSION'] = '.md'
flatpages = FlatPages(app)
bootstrap = Bootstrap(app)
login_manager = LoginManager()
login_manager.init_app(app)

# User class for Flask-Login
class User(UserMixin):
    # create a user class as per your requirement
    pass

@login_manager.user_loader
def load_user(user_id):
    # Load user from database or any data structure you prefer
    return User()

if __name__ == '__main__':
    # app.run(debug=True)
    app.run(debug=False)
