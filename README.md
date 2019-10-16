#Overview

This site allows people to keep track of character levels for Dungeons and Dragons 5th Edition.
Create a character, plug in the class it will use for each level, and the program will display a
table that includes the major class features for those levels.


#How To Use

From the home page, click the "New Character" button, and you will be redirected to the setup page.
Here, you input a name and select a class for each level via dropdowns. Once finished, click "Save"
at the bottom, and the feature table will appear. You can edit the character's name or levels at
any time, or delete the character altogether.


#Why I Made This

As an avid D&D player, I often find myself fleshing out a backlog of characters to play. I have a
fundamental concept, decide what class, race, etc. makes sense, and work up from there. Sometimes
the best way to realize an idea is to multiclass, but that adds a layer of complexity beyond what
a standard character sheet can handle. Thus, I started making a Google Sheets document to keep
track of what classes to take at which levels, and what abilities I would gain from those. After
messing with formulae and conditions, I decided it would be helpful to make an app that handled the
details for me. And so here we are.


#The Code

This program is built in Python, using Flask and MongoDB. Everything runs from `app.py`, with HTML
files using Jinja2 templating providing the frontend.