from flask import Flask, render_template, redirect, url_for, request
from pymongo import MongoClient
from bson.objectid import ObjectId
import classes
import os

app = Flask(__name__)

host = os.environ.get("MONGODB_URI", "mongodb://localhost:27017/my_app_db")
client = MongoClient(host=f"{host}?retryWrites=false")
db = client.get_default_database()
characters = db.characters

app = Flask(__name__)


@app.route('/')
def index():
    """Return homepage."""
    return render_template('index.html')


@app.route('/new')
def new_char():
    """Show the form to create a new character"""
    return render_template('char_new.html', char={}, levels=range(20),
                           classes=classes.classes)


@app.route('/new', methods=['POST'])
def create_char():
    """Create a new character and insert it into the database"""
    char = {
        "name": request.form.get("name"),
        "1": request.form.get("1"),
        "2": request.form.get("2"),
        "3": request.form.get("3"),
        "4": request.form.get("4"),
        "5": request.form.get("5"),
        "6": request.form.get("6"),
        "7": request.form.get("7"),
        "8": request.form.get("8"),
        "9": request.form.get("9"),
        "10": request.form.get("10"),
        "11": request.form.get("11"),
        "12": request.form.get("12"),
        "13": request.form.get("13"),
        "14": request.form.get("14"),
        "15": request.form.get("15"),
        "16": request.form.get("16"),
        "17": request.form.get("17"),
        "18": request.form.get("18"),
        "19": request.form.get("19"),
        "20": request.form.get("20")
    }
    char_id = characters.insert_one(char).inserted_id
    return redirect(url_for('show_char', char_id=char_id))


@app.route('/<char_id>')
def show_char(char_id):
    """Display a character"""
    char = characters.find_one({"_id": ObjectId(char_id)})
    return render_template('char_show.html', char=char, levels=range(20),
                           classes=classes.classes)


@app.route('/<char_id>', methods=['POST'])
def update_char(char_id):
    """Update the information for a character"""
    char = {
        "name": request.form.get("name"),
        "1": request.form.get("1"),
        "2": request.form.get("2"),
        "3": request.form.get("3"),
        "4": request.form.get("4"),
        "5": request.form.get("5"),
        "6": request.form.get("6"),
        "7": request.form.get("7"),
        "8": request.form.get("8"),
        "9": request.form.get("9"),
        "10": request.form.get("10"),
        "11": request.form.get("11"),
        "12": request.form.get("12"),
        "13": request.form.get("13"),
        "14": request.form.get("14"),
        "15": request.form.get("15"),
        "16": request.form.get("16"),
        "17": request.form.get("17"),
        "18": request.form.get("18"),
        "19": request.form.get("19"),
        "20": request.form.get("20")
    }
    characters.update_one(
        {"_id": ObjectId(char_id)},
        {"$set": char})
    return redirect(url_for('show_char', char_id=char_id))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=os.environ.get('PORT', 5000))
