import os
from flask import Flask, render_template, request, redirect, session
from models import db, User, Movie

app = Flask(__name__)
app.secret_key = "secret123"

DATABASE_URL = os.environ.get("DATABASE_URL")

if DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://")
    app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///movie.db"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

# ---------- CREATE TABLE ----------
with app.app_context():
    db.create_all()

# ---------- ROUTES ----------

@app.route("/")
def index():
    movies = Movie.query.all()
    return render_template("index.html", movies=movies)


@app.route("/movie/<int:id>")
def movie_detail(id):
    movie = Movie.query.get_or_404(id)
    return render_template("movie_detail.html", movie=movie)


@app.route("/register", methods=["GET","POST"])
def register():

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = User(username=username, password=password)

        db.session.add(user)
        db.session.commit()

        return redirect("/login")

    return render_template("register.html")


@app.route("/login", methods=["GET","POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username, password=password).first()

        if user:
            session["user"] = username
            return redirect("/")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")


@app.route("/add_movie", methods=["GET","POST"])
def add_movie():

    if "user" not in session:
        return redirect("/login")

    if request.method == "POST":

        title = request.form.get("title")
        genre = request.form.get("genre")
        year = request.form.get("year")
        image_url = request.form.get("image_url")

        movie = Movie(
            title=title,
            genre=genre,
            year=year,
            image_url=image_url
        )

        db.session.add(movie)
        db.session.commit()

        return redirect("/")

    return render_template("add_movie.html")


@app.route("/edit_movie/<int:id>", methods=["GET","POST"])
def edit_movie(id):

    if "user" not in session:
        return redirect("/login")

    movie = Movie.query.get_or_404(id)

    if request.method == "POST":

        movie.title = request.form.get("title")
        movie.genre = request.form.get("genre")
        movie.year = request.form.get("year")
        movie.image_url = request.form.get("image_url")

        db.session.commit()

        return redirect("/")

    return render_template("edit_movie.html", movie=movie)


@app.route("/delete_movie/<int:id>")
def delete_movie(id):

    if "user" not in session:
        return redirect("/login")

    movie = Movie.query.get_or_404(id)

    db.session.delete(movie)
    db.session.commit()

    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
