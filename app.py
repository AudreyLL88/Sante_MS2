import os
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env


app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


@app.route("/")
@app.route("/get_cocktails")
def get_cocktails():
    cocktails = list(mongo.db.cocktails.find())
    return render_template("cocktails.html", cocktails=cocktails)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            flash("Username already exists")
            return redirect(url_for("register"))

        register = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }
        mongo.db.users.insert_one(register)

        session["user"] = request.form.get("username").lower()
        flash("Registration successful!")
        return redirect(url_for("profile", username=session["user"]))
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        existing_user = mongo.db.users.find_one(
          {"username": request.form.get("username").lower()})

        if existing_user:
            if check_password_hash(
                existing_user["password"], request.form.get("password")):
                    session["user"] = request.form.get("username").lower()
                    flash("Welcome, {}".format(
                        request.form.get("username")))
                    return redirect(url_for(
                        "profile", username=session["user"]))
            else:
                flash("Incorrect Username and/or Password")
                return redirect(url_for("login"))

        else:
            flash("Incorrect Username and/or Password")
            return redirect(url_for("login"))
    return render_template("login.html")


@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]

    if session["user"]:
        return render_template("profile.html", username=username)

    return render_template("profile.html", username=username)


@app.route("/logout")
def logout():
    flash("You have been logged out")
    session.pop("user")
    return redirect(url_for("login"))


@app.route("/add_cocktail", methods=["GET", "POST"])
def add_cocktail():
    if request.method == "POST":
        cocktail_status = "on" if request.form.get("cocktail_status") else "off"
        task = {
            "category_name": request.form.get("category_name"),
            "cocktail_name": request.form.get("cocktail_name"),
            "cocktail_description": request.form.get("cocktail_description"),
            "cocktail_status": cocktail_status,
            "cocktail_date": request.form.get("cocktail_date"),
            "created_by": session["user"]
        }
        mongo.db.cocktails.insert_one(task)
        flash("Cocktail Successfully Added")
        return redirect(url_for("get_cocktails"))

    categories = mongo.db.categories.find().sort("category_name", 1)
    return render_template("add_cocktail.html", categories=categories)


@app.route("/edit_cocktail/<cocktail_id>", methods=["GET", "POST"])
def edit_cocktail(cocktail_id):
    if request.method == "POST":
        cocktail_status = "on" if request.form.get("cocktail_status") else "off"
        submit = {
            "category_name": request.form.get("category_name"),
            "cocktail_name": request.form.get("cocktail_name"),
            "cocktail_description": request.form.get("cocktail_description"),
            "cocktail_status": cocktail_status,
            "cocktail_date": request.form.get("cocktail_date"),
            "created_by": session["user"]
        }
        mongo.db.cocktails.update({"_id": ObjectId(cocktail_id)}, submit)
        flash("Cocktail Successfully Updated")

    cocktail = mongo.db.cocktails.find_one({"_id": ObjectId(cocktail_id)})
    categories = mongo.db.categories.find().sort("category_name", 1)
    return render_template(
        "edit_cocktail.html", cocktail=cocktail, categories=categories)


@app.route("/delete_cocktail/<cocktail_id>")
def delete_cocktail(cocktail_id):
    mongo.db.cocktails.remove({"_id": ObjectId(cocktail_id)})
    flash("Cocktail Successfully Deleted")
    return redirect(url_for("get_cocktails"))


@app.route("/get_categories")
def get_categories():
    categories = list(mongo.db.categories.find().sort("category_name", 1))
    return render_template("categories.html", categories=categories)


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
