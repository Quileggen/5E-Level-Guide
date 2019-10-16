from flask import Flask, render_template, redirect, url_for, request
from pymongo import MongoClient
from bson.objectid import ObjectId
import requests
import json
import os

app = Flask(__name__)

host = os.environ.get("MONGODB_URI", "mongodb://localhost:27017/my_app_db")
client = MongoClient(host=f"{host}?retryWrites=false")
db = client.get_default_database()
characters = db.characters

app = Flask(__name__)


def get_class_names():
    """Make a call to the 5e API and get the class names"""
    r = requests.get("http://www.dnd5eapi.co/api/classes")
    if r.status_code == 200:
        classes = json.loads(r.content)["results"]
        class_list = [char_class["name"] for char_class in classes]
    else:
        classes = "None"
        class_list = []
    return class_list


def get_class_features(char_class, level):
    """Call the 5e API and get features of a class at a designated level"""
    r = requests.get("http://www.dnd5eapi.co/api/classes/"
                     + char_class.lower() + "/level/" + str(level))
    if r.status_code == 200 and r.content != b'null':
        features = json.loads(r.content)["features"]
        feature_list = [feature["name"] for feature in features]
    else:
        features = "None"
        feature_list = []
    return feature_list


@app.route('/')
def index():
    """Return homepage."""
    return render_template('index.html')


@app.route('/new')
def new_char():
    """Show the form to create a new character"""
    return render_template('char_new.html', char={}, levels=range(1, 21),
                           classes=get_class_names(), char_class={})


@app.route('/new', methods=['POST'])
def create_char():
    """Create a new character and insert it into the database"""
    char = {
        "name": request.form.get("name"),
        "class_levels": {
            "Barbarian": 0,
            "Bard": 0,
            "Cleric": 0,
            "Druid": 0,
            "Fighter": 0,
            "Monk": 0,
            "Paladin": 0,
            "Ranger": 0,
            "Rogue": 0,
            "Sorcerer": 0,
            "Warlock": 0,
            "Wizard": 0,
            "": 0
        }
    }
    for level in range(1, 21):
        char_class = request.form.get(str(level))
        char["class_levels"][char_class] += 1
        class_level = char["class_levels"][char_class]
        char[str(level)] = str(char_class) + " " + str(class_level)

    char_id = characters.insert_one(char).inserted_id
    return redirect(url_for('show_char', char_id=char_id))


@app.route('/<char_id>')
def show_char(char_id):
    """Display a character"""
    char = characters.find_one({"_id": ObjectId(char_id)})
    char_features = []
    char_class_list = []
    for level in range(1, 21):
        char_class_info = char[str(level)].split()
        char_class = char_class_info[0]
        char_class_list.append(char_class)
        char_class_level = char_class_info[1]
        feature_list = get_class_features(char_class, char_class_level)
        char_features.append(feature_list)
    return render_template('char_show.html', char=char, levels=range(1, 21),
                           classes=get_class_names(), features=char_features,
                           char_class=char_class_list)


@app.route('/<char_id>', methods=['POST'])
def update_char(char_id):
    """Update the information for a character"""
    char = {
        "name": request.form.get("name"),
        "class_levels": {
            "Barbarian": 0,
            "Bard": 0,
            "Cleric": 0,
            "Druid": 0,
            "Fighter": 0,
            "Monk": 0,
            "Paladin": 0,
            "Ranger": 0,
            "Rogue": 0,
            "Sorcerer": 0,
            "Warlock": 0,
            "Wizard": 0,
            "": 0
        }
    }
    for level in range(1, 21):
        char_class = request.form.get(str(level))
        char["class_levels"][char_class] += 1
        class_level = char["class_levels"][char_class]
        char[str(level)] = str(char_class) + " " + str(class_level)

    characters.update_one(
        {"_id": ObjectId(char_id)},
        {"$set": char})
    return redirect(url_for('show_char', char_id=char_id))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=os.environ.get('PORT', 5000))
