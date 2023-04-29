from flask import Flask, render_template, redirect, url_for, request as req

from model.psql_interface import Psql_interface

import requests
import os
import sys

PGUSER = "postgres"
PGPASS_FILE = "./model/.pgpass"
DB_NAME = "food_truck"
TABLE_NAME = "food"
DB_TEMPLATE_JSON = "food_db_table_format.json"
DB_SEED_DATA_JSON = "seed_food_db_data.json"
SRC_PATH = "./src"
IMG_PATH = "static/imgs/"

here_abspath = os.path.dirname( os.path.realpath( sys.argv[0] ) )
src_path = os.path.abspath( os.path.join( here_abspath, SRC_PATH ) )
pgpass = open(os.path.join(here_abspath, PGPASS_FILE)).read().strip()
    
app = Flask(__name__)
psql = Psql_interface(PGUSER, pgpass, DB_NAME, src_path, DB_TEMPLATE_JSON, DB_SEED_DATA_JSON)

@app.route("/")
def html_home():
    return render_template("home.html")

@app.route("/menu")
def html_menu():
    menu = psql.psql_psycopg2_query(f"SELECT * FROM {TABLE_NAME}")
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
    return render_template("menu.html", burgers=burgers, drinks=drinks)

@app.route("/about")
def html_about():
    return render_template("about.html")

@app.route("/contact")
def html_contact():
    return render_template("contact.html")

@app.route("/bad_page")
def html_bad_page():
    return render_template("bad.html")


if __name__ == "__main__":
    app.run(debug=True)
    