import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
db_drop_and_create_all()

# ROUTES
'''
#? GET route("/drinks")
# public endpoint
# contain only the drink.short() data representation
# returns status code 200 and json {"success": True, "drinks": drinks}
'''


@app.route("/drinks")
def get_drinks():
    drinks = list(map(Drink.short, Drink.query.all()))
    result = {
        "success": True,
        "drinks": drinks
    }
    return jsonify(result)


'''
#? GET route("/drinks-detail")
# require the 'get:drinks-detail' permission
# contain the drink.long() data representation
# returns status code 200 and json {"success": True, "drinks": drinks}
'''
@app.route("/drinks-detail")
@requires_auth("get:drinks-detail")
def get_drinks_detail(token):
    drinks = list(map(Drink.long, Drink.query.all()))
    result = {
        "success": True,
        "drinks": drinks
    }
    return jsonify(result)


'''
#? POST route("/drinks")
# create a new row in the drinks table
# require the 'post:drinks' permission
# contain the drink.long() data representation
# returns status code 200 and json {"success": True, "drinks": drink}
'''
@app.route("/drinks", methods=['POST'])
@requires_auth("post:drinks")
def add_drinks(token):
    if request.data:
        new_drink_data = json.loads(request.data.decode('utf-8'))
        new_drink = Drink(title=new_drink_data['title'], recipe=json.dumps(new_drink_data['recipe']))
        Drink.insert(new_drink)
        drinks = list(map(Drink.long, Drink.query.all()))
        result = {
            "success": True,
            "drinks": drinks
        }
        return jsonify(result)


'''
#? route("/drinks/<drink_id>")
# respond with a 404 error if <id> is not found
# update the corresponding row for <id>
# require the 'patch:drinks' permission
# contain the drink.long() data representation
returns status code 200 and json {"success": True, "drinks": drink}
'''
@app.route("/drinks/<drink_id>", methods=['PATCH'])
@requires_auth("patch:drinks")
def patch_drinks(token, drink_id):
    new_drink_data = json.loads(request.data.decode('utf-8'))
    drink_data = Drink.query.get(drink_id)
    if 'title' in new_drink_data:
        setattr(drink_data, 'title', new_drink_data['title'])
    if 'recipe' in new_drink_data:
        setattr(drink_data, 'recipe', new_drink_data['recipe'])
    Drink.update(drink_data)
    drinks = list(map(Drink.long, Drink.query.all()))
    result = {
        "success": True,
        "drinks": drinks
    }
    return jsonify(result)


'''
#? DELETE route("/drinks/<drink_id>")
# respond with a 404 error if <id> is not found
# delete the corresponding row for <id>
# require the 'delete:drinks' permission
# returns status code 200 and json {"success": True, "delete": id}
'''
@app.route("/drinks/<drink_id>", methods=['DELETE'])
@requires_auth("delete:drinks")
def delete_drinks(token, drink_id):
    drink_data = Drink.query.get(drink_id)
    Drink.delete(drink_data)
    drinks = list(map(Drink.long, Drink.query.all()))
    result = {
        "success": True,
        "drinks": drinks
    }
    return jsonify(result)


#? Error Handling Section

@app.errorhandler(422)
def unprocessable(error):
    error_data = {
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }
    return jsonify(error_data), 422


@app.errorhandler(404)
def not_found(error):
    error_data = {
        "success": False,
        "error": 404,
        "message": "resource not found"
    }
    return jsonify(error_data), 404


@app.errorhandler(AuthError)
def auth_error(e):
    return jsonify(e.error), e.status_code