from flask import Flask, render_template, redirect, url_for, request
from pymongo import MongoClient
from bson.objectid import ObjectId
from math import floor, ceil
import requests
import json
import os

app = Flask(__name__)

# Setting up MongoDB
host = os.environ.get("MONGODB_URI", "mongodb://localhost:27017/LevelGuide")
client = MongoClient(host=f"{host}?retryWrites=false")
db = client.get_default_database()
characters = db.characters


def init_char():
    """Set character information"""
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
            "N/A": 0
        }
    }
    # Check the class input in each dropdown in the form
    for level in range(1, 21):
        char_class = request.form.get(str(level))
        char["class_levels"][char_class] += 1
        class_level = char["class_levels"][char_class]
        cast_level = get_spell_level(char)

        # Format each level string for use later
        char[str(level)] = f"{char_class} {class_level} {cast_level}"

    return char


def get_spell_level(char):
    """Helper function to calculate spellcasting level"""
    # Full casters count as 1, half casters as 1/2
    cast_level = (char["class_levels"]["Bard"]
                  + char["class_levels"]["Cleric"]
                  + char["class_levels"]["Druid"]
                  + char["class_levels"]["Sorcerer"]
                  + char["class_levels"]["Wizard"]
                  + char["class_levels"]["Paladin"] / 2
                  + char["class_levels"]["Ranger"] / 2)
    # Round down
    return floor(cast_level)


def get_class_names():
    """Make a call to the 5e API and get the names of each class"""
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
    # Formatting parameters to play nicely
    char_class = char_class.lower()
    level = int(level)
    r = requests.get("http://www.dnd5eapi.co/api/classes/"
                     + char_class + "/level/" + str(level))
    if r.status_code == 200 and r.content != b'null':
        features = json.loads(r.content)["features"]
        feature_list = [feature["name"] for feature in features]

        # Filling in for missing elements from the API
        if ((char_class == "barbarian"
                and (level == 6 or level == 10 or level == 14))
            or (char_class == "bard"
                and (level == 6 or level == 14))
            or (char_class == "cleric"
                and (level == 6 or level == 8 or level == 17))
            or (char_class == "druid"
                and (level == 3 or level == 6 or level == 10
                     or level == 14))
            or (char_class == "fighter"
                and (level == 7 or level == 10 or level == 15
                     or level == 18))
            or (char_class == "monk"
                and (level == 6 or level == 11 or level == 17))
            or (char_class == "paladin"
                and (level == 7 or level == 15 or level == 20))
            or (char_class == "ranger"
                and (level == 7 or level == 11 or level == 15))
            or (char_class == "rogue"
                and (level == 9 or level == 13 or level == 17))
            or (char_class == "sorcerer"
                and (level == 6 or level == 14 or level == 18))
            or (char_class == "warlock"
                and (level == 6 or level == 10 or level == 14))
            or (char_class == "wizard"
                and (level == 6 or level == 10 or level == 14))):
            feature_list.append('Subclass feature')

        # More missing features, but for spells this time
        if ((char_class == "bard" or char_class == "cleric"
            or char_class == "druid" or char_class == "sorcerer"
            or char_class == "wizard") and (level % 2 == 1)
                and (level > 1 and level < 18)):
            feature_list.append(f'Level {ceil(level/2)} spells')
    else:
        features = "None"
        feature_list = []

    return feature_list


@app.route('/')
def index():
    """Return homepage."""
    return render_template('index.html')


@app.route('/all')
def show_all_chars():
    """Show a clickable list of all characters"""
    return render_template('char_all.html', chars=characters.find())


@app.route('/new')
def new_char():
    """Show the form to create a new character"""
    return render_template('char_new.html', char={}, levels=range(1, 21),
                           classes=get_class_names(), char_class={})


@app.route('/new', methods=['POST'])
def create_char():
    """Create a new character and insert it into the database"""
    char = init_char()
    char_id = characters.insert_one(char).inserted_id
    return redirect(url_for('show_char', char_id=char_id))


@app.route('/<char_id>')
def show_char(char_id):
    """Display a character, with levels, features, and spell slots"""
    char = characters.find_one({"_id": ObjectId(char_id)})
    char_features = []
    char_class_list = []
    char_cast_levels = []

    # Set specific class info and pass it to the template
    for level in range(1, 21):
        # Manipulating the string we set earlier to get info
        char_class_info = char[str(level)].split()

        # Set the character's class at each level
        char_class = char_class_info[0]
        char_class_list.append(char_class)

        # Set the level of each class
        char_class_level = char_class_info[1]

        # Set the spellcasting level
        char_cast_levels.append(char_class_info[2])

        # Reformatting the string to be displayed nicely
        char[str(level)] = f"{char_class} {char_class_level}"

        # Getting a list of features
        feature_list = get_class_features(char_class, char_class_level)
        char_features.append(feature_list)

    return render_template('char_show.html', char=char, levels=range(1, 21),
                           classes=get_class_names(), features=char_features,
                           cast=char_cast_levels, char_class=char_class_list)


@app.route('/<char_id>', methods=['POST'])
def update_char(char_id):
    """Update the information for a character"""
    char = init_char()
    characters.update_one(
        {"_id": ObjectId(char_id)},
        {"$set": char})
    return redirect(url_for('show_char', char_id=char_id))


@app.route('/<char_id>/delete', methods=['POST'])
def delete_char(char_id):
    """Delete a character"""
    characters.delete_one({"_id": ObjectId(char_id)})
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=os.environ.get('PORT', 5000))
