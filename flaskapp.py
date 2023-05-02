from flask import Flask, render_template, redirect, url_for, session, request as req

from model.psql_interface import Psql_interface
import bcrypt

import requests
import os
import sys

PGUSER = "postgres"
PGPASS_FILE = "./model/.pgpass"
DB_NAME = "food_truck"
SRC_PATH = "./src"
IMG_PATH = "static/imgs/"

here_abspath = os.path.dirname( os.path.realpath( sys.argv[0] ) )
src_path = os.path.abspath( os.path.join( here_abspath, SRC_PATH ) )
pgpass = open(os.path.join(here_abspath, PGPASS_FILE)).read().strip()
    
psql = Psql_interface(PGUSER, pgpass, DB_NAME, src_path)
app = Flask(__name__)
app.config["SECRET_KEY"] = "My secret key"

@app.route("/")
def html_home():
    username = session["username"] if "username" in session else None
    is_admin = session["is_admin"] if "is_admin" in session else False
    return render_template("home.html", username=username, is_admin=is_admin)


@app.route("/menu")
def html_menu():
    username = session["username"] if "username" in session else None
    menu = psql.psql_psycopg2_query(f"SELECT * FROM food")
    burgers = []
    drinks = []
    for entry in menu:
        item = {}
        item["id"] = entry[0]
        item["name"] = entry[1]
        item["category"] = entry[2]
        item["price"] = f'${float(entry[3])/100:.2f}'
        item["description"] = entry[4]
        if entry[5].startswith("http"):
            item["image_url"] = entry[5]    
        else:
            item["image_url"] = f"{IMG_PATH}{entry[5]}"
        if item["category"] == "burger":
            burgers.append(item)
        elif item["category"] == "drink":
            drinks.append(item)
    return render_template("menu.html",username=username, burgers=burgers, drinks=drinks)

@app.route("/about")
def html_about():
    username = session["username"] if "username" in session else None
    return render_template("about.html", username=username)

@app.route("/contact")
def html_contact():
    username = session["username"] if "username" in session else None
    return render_template("contact.html",username=username)

@app.route("/bad_page")
def html_bad_page():
    return render_template("bad.html")

@app.route("/admin")
def html_admin():
    user_id = session.get("user_id", "")
    if user_id is None:
        return render_template("admin_login.html")
    else:
        return render_template("admin_home.html")

@app.route("/admin-login")
def html_admin_login_form():
    return render_template("admin_login.html")

@app.route("/admin-login", methods=["POST"])
def html_admin_login_action():
    email = req.form.get("email")
    password = req.form.get("password")
    usernames = psql.psql_psycopg2_query()
    # check for existence of user in DB and handle appropriately
    # e.g. if exists, go back to "/"; otherwise, display error page or refresh "/login"
    return

@app.route("/signin", methods=["GET","POST"])
def html_signin():
    if req.method == "GET":
        username = session["username"] if "username" in session else None
        if username is not None:
            return redirect("/")
        return render_template("signin.html", invalid_user="False")
    if req.method == "POST":
        user = req.form.get("user")
        users = psql.psql_psycopg2_query("SELECT username FROM users;")
        users = [tup[0] for tup in users]
        emails = psql.psql_psycopg2_query("SELECT email FROM users;")
        emails = [tup[0] for tup in emails]
        if not ((user in users) or (user in emails)):
            return render_template("signin.html", invalid_user="True")
        sql_query = f"SELECT password_hash FROM users WHERE username = '{user}'"
        hashed_password = psql.psql_psycopg2_query(sql_query)[0][0]
        isValidPassword = bcrypt.checkpw(req.form.get("password").encode(), hashed_password.encode())
        if not (isValidPassword):
            return render_template("signin.html", invalid_user="True")
        session["username"] = user
        sql_query = f"SELECT is_admin FROM users WHERE username = '{user}'"
        session["is_admin"] = psql.psql_psycopg2_query(sql_query)[0][0]
        return redirect("/")

@app.route("/signup", methods=["GET","POST"])
def html_signup():
    if req.method == "GET":
        username = session["username"] if "username" in session else None
        if username is not None:
            return redirect("/")
        return render_template("signup.html", invalid_user="False")
    if req.method == "POST":
        email = req.form.get("email")
        username = req.form.get("username")
        hashed_password = bcrypt.hashpw(req.form.get("password").encode(), bcrypt.gensalt()).decode()
        users = psql.psql_psycopg2_query("SELECT username FROM users;")
        users = [tup[0] for tup in users]
        emails = psql.psql_psycopg2_query("SELECT email FROM users;")
        emails = [tup[0] for tup in emails]
        if ((username in users) or (email in emails)):
            return render_template("signup.html", invalid_user="True")
        sql_params = [email, username, hashed_password]
        sql_query = f"""
            INSERT INTO users (email, username, password_hash)
            VALUES (%s, %s, %s)
            ;
        """
        psql.psql_psycopg2_query(sql_query, sql_params)
        return redirect("/")

@app.route("/logout")
def page_logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
    