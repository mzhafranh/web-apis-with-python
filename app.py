from html.entities import html5
from pydoc import HTMLDoc
from flask import Flask, jsonify, request

# Intitialise the app
app = Flask(__name__)

# Define what the app does

#Chapter 3
"""
@app.get("/greet")
def index():
    return "Hello World!"

@app.get("/greetname")
def indexGreet():
    name = request.args.get("name")
    if not name:
        return jsonify({"status" : "error"})
    else:
        return jsonify({"data" : f"Hello, {name}!"})

@app.get("/fancygreet")
def fancyIndex():
    return '<!doctype html><html><head><meta charset="UTF-8"><title>Sisterin STI 20 Kel 1</title></head><body><pre>            _____                    _____                    _____            _____           _______         \n           /\    \                  /\    \                  /\    \          /\    \         /::\    \        \n          /::\____\                /::\    \                /::\____\        /::\____\       /::::\    \       \n         /:::/    /               /::::\    \              /:::/    /       /:::/    /      /::::::\    \      \n        /:::/    /               /::::::\    \            /:::/    /       /:::/    /      /::::::::\    \     \n       /:::/    /               /:::/\:::\    \          /:::/    /       /:::/    /      /:::/~~\:::\    \    \n      /:::/____/               /:::/__\:::\    \        /:::/    /       /:::/    /      /:::/    \:::\    \   \n     /::::\    \              /::::\   \:::\    \      /:::/    /       /:::/    /      /:::/    / \:::\    \  \n    /::::::\    \   _____    /::::::\   \:::\    \    /:::/    /       /:::/    /      /:::/____/   \:::\____\ \n   /:::/\:::\    \ /\    \  /:::/\:::\   \:::\    \  /:::/    /       /:::/    /      |:::|    |     |:::|    |\n  /:::/  \:::\    /::\____\/:::/__\:::\   \:::\____\/:::/____/       /:::/____/       |:::|____|     |:::|    |\n  \::/    \:::\  /:::/    /\:::\   \:::\   \::/    /\:::\    \       \:::\    \        \:::\    \   /:::/    / \n   \/____/ \:::\/:::/    /  \:::\   \:::\   \/____/  \:::\    \       \:::\    \        \:::\    \ /:::/    /  \n            \::::::/    /    \:::\   \:::\    \       \:::\    \       \:::\    \        \:::\    /:::/    /   \n             \::::/    /      \:::\   \:::\____\       \:::\    \       \:::\    \        \:::\__/:::/    /    \n             /:::/    /        \:::\   \::/    /        \:::\    \       \:::\    \        \::::::::/    /     \n            /:::/    /          \:::\   \/____/          \:::\    \       \:::\    \        \::::::/    /      \n           /:::/    /            \:::\    \               \:::\    \       \:::\    \        \::::/    /       \n          /:::/    /              \:::\____\               \:::\____\       \:::\____\        \::/____/        \n          \::/    /                \::/    /                \::/    /        \::/    /         ~~              \n           \/____/                  \/____/                  \/____/          \/____/                          \n                                                                                                               </pre></body></html>'
"""

#Chapter 4
"""
@app.get("/greet")
def indexGreet():
    name = request.args.get("name")
    if not name:
        return jsonify({"status" : "error"})
    else:
        return jsonify({"data" : f"Hello, {name}!"})

@app.get("/age")
def indexAge():
    yearOfBirth = int(request.args.get("yob"))
    if not yearOfBirth:
        return jsonify({"status" : "error", "message" : "No Year of Birth was given"})
    else:
        age = 2022-yearOfBirth
        if (age == 0):
            response = {"data" : "You aren't old enough to use this feature!"}
            return jsonify(response)
        else:
            response = {"data" : f"You are {age} year(s) old"}
            return jsonify(response)
"""
#Chapter 5
@app.get("/greet")
def indexGreet():
    fname = request.args.get("fname")
    lname = request.args.get("lname")
    if not fname and not lname:
        return jsonify({"status" : "error"})
    elif not lname:
        return jsonify({"data" : f"Hello, {fname}!"})
    else:
        return jsonify({"data" : f"Hello, {fname} {lname}!"})



