from flask import Flask, render_template, redirect, url_for, request
from pymongo import MongoClient
from bson.objectid import ObjectId
import requests
import json
# import classes
import os

app = Flask(__name__)

host = os.environ.get("MONGODB_URI", "mongodb://localhost:27017/my_app_db")
client = MongoClient(host=f"{host}?retryWrites=false")
db = client.get_default_database()
characters = db.characters

app = Flask(__name__)


def get_class_names():
    r = requests.get("http://www.dnd5eapi.co/api/classes")
    if r.status_code == 200:
        classes = json.loads(r.content)["results"]
        class_list = [name["name"] for name in classes]
    else:
        classes = "None"
        class_list = []
    return class_list


@app.route('/')
def index():
    """Return homepage."""
    return render_template('index.html')


@app.route('/new')
def new_char():
    """Show the form to create a new character"""
    return render_template('char_new.html', char={}, levels=range(20),
                           classes=get_class_names())


@app.route('/new', methods=['POST'])
def create_char():
    """Create a new character and insert it into the database"""
    char = {
        "name": request.form.get("name"),
    }
    for i in range(20):
        char[str(i + 1)] = request.form.get(str(i + 1))

    char_id = characters.insert_one(char).inserted_id
    return redirect(url_for('show_char', char_id=char_id))


@app.route('/<char_id>')
def show_char(char_id):
    """Display a character"""
    char = characters.find_one({"_id": ObjectId(char_id)})
    return render_template('char_show.html', char=char, levels=range(20),
                           classes=get_class_names())


@app.route('/<char_id>', methods=['POST'])
def update_char(char_id):
    """Update the information for a character"""
    char = {
        "name": request.form.get("name"),
    }
    for i in range(20):
        char[str(i + 1)] = request.form.get(str(i + 1))
    characters.update_one(
        {"_id": ObjectId(char_id)},
        {"$set": char})
    return redirect(url_for('show_char', char_id=char_id))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=os.environ.get('PORT', 5000))
