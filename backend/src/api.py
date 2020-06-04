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
#? following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''

db_drop_and_create_all()


## ROUTES Section
'''
#? GET /drinks
# it's a public endpoint
# contain only drink.short() data representation
# returns status code 200 and json {"success": True, "drinks": drinks} 
# Note: drinks is the list of drinks
'''
@app.route('/drinks', methods=['GET'])
def get_drinks():
    try:
        # query to get all drinks list
        drinks = Drink.query.all()

        print(drinks)
        # return the result with success status
        return jsonify({
            'success': True,
            'drinks': [drink.short() for drink in drinks]
        }), 200

    except:
        # returns status code indicating failure
        abort(404)


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''


'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''


'''
#? DELETE /drinks/<id>
# <id> should be existing 
# should respond with a 404 error if <id> is not found
# require the 'delete:drinks' permission 
# returns status code 200 and json {"success": True, "deleted": drink_id} 
# if failure status code indicating reason of failure
'''
@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(token, drink_id):
    try:
        drink = Drink.query.filter_by(id=drink_id).one_or_none()

        # the given id does not exsits 
        if drink is None:
            abort(404)

        # complete process of DELETE and return success status with id
        drink.delete()
        return jsonify({
            'success': True,
            'deleted': drink_id
        })
    except:
        abort(422)


## Error Handling Section

'''
#? implement error handler for 404
    error handler should conform to general task above 
'''

@app.errorhandler(404)
def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found." +
            "The requested page" +
            "could not be found" +
            "but may be available again in the future"
        }), 404

@app.errorhandler(422)
def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable," +
            "unable to process" +
            "the contained instructions." +
            "Error realted to semantically erroneous"
        }), 422

@app.errorhandler(400)
def bad_syntax(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "The request cannot be fulfilled due to bad syntax"
        }), 400

@app.errorhandler(500)
def Server_Error(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "Internal Server Error."
        }), 500



'''
@TODO implement error handler for AuthError
    error handler should conform to general task above 
'''
