
from flask import Flask, render_template, abort, request, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    UserMixin,
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user
)
from werkzeug.security import generate_password_hash, check_password_hash

# Flask application
app = Flask(__name__)

app.config["SECRET_KEY"] = "my-development-secret-key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///blog.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Database
db = SQLAlchemy(app)

# Flask Login configuration
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


# Post Model
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)


# User Model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


# Load logged-in user
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


# Home Page
@app.route("/")
def home():
    posts = Post.query.all()
    return render_template("posts.html", posts=posts)


# Add Sample Posts
@app.route("/add-samples")
def add_samples():
    if Post.query.count() == 0:
        post1 = Post(
            title="Introduction to Python",
            content="Python is a beginner-friendly programming language."
        )
        post2 = Post(
            title="What is Flask?",
            content="Flask is a lightweight Python web framework."
        )
        post3 = Post(
            title="Learning SQLite",
            content="SQLite is a lightweight database."
        )

        db.session.add_all([post1, post2, post3])
        db.session.commit()

    return "Sample posts added successfully!"


# Post Details
@app.route("/post/<int:post_id>")
def post_detail(post_id):
    post = db.session.get(Post, post_id)

    if post is None:
        abort(404)

    return render_template("post_detail.html", post=post)


# Registration
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"].strip()
        email = request.form["email"].strip()
        password = request.form["password"]

        if User.query.filter_by(username=username).first():
            flash("Username already exists!")
            return redirect(url_for("register"))

        if User.query.filter_by(email=email).first():
            flash("Email already registered!")
            return redirect(url_for("register"))

        user = User(username=username, email=email)
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        login_user(user)
        flash("Registration successful!")
        return redirect(url_for("dashboard"))

    return render_template("register.html")


# Login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            flash("Login successful!")
            return redirect(url_for("dashboard"))

        flash("Invalid username or password!")

    return render_template("login.html")


# Protected Dashboard
@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", user=current_user)


# Logout
@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out successfully!")
    return redirect(url_for("login"))


# Run Application
if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)
