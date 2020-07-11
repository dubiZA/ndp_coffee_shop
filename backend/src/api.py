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
uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
# db_drop_and_create_all()

# ROUTES
'''
GET /drinks
    it should be a public endpoint
    it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks}
    where drinks is the list of drinks
    or appropriate status code indicating reason for failure
'''


@app.route('/drinks')
def get_drinks():
    drinks = Drink.query.all()
    # print(drinks)
    if not drinks:
        abort(404)
    else:
        drinks = [drink.short() for drink in drinks]
        print(drinks)

        return jsonify({
            'success': True,
            'drinks': drinks
        })


'''
GET /drinks-detail
    it should require the 'get:drinks-detail' permission
    it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks}
    where drinks is the list of drinks
    or appropriate status code indicating reason for failure
'''


@app.route('/drinks-detail')
@requires_auth(permission='get:drinks-detail')
def get_drinks_detail(jwt):
    drinks = Drink.query.all()
    if not drinks:
        abort(404)
    else:
        drinks = [drink.long() for drink in drinks]

        return jsonify({
            'success': True,
            'drinks': drinks
        })


'''
POST /drinks
    it should create a new row in the drinks table
    it should require the 'post:drinks' permission
    it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink}
    where drink an array containing only the newly created drink
    or appropriate status code indicating reason for failure
'''


@app.route('/drinks', methods=['POST'])
@requires_auth(permission='post:drinks')
def post_drinks(jwt):
    drink_details = request.get_json()

    if 'title' not in drink_details or 'recipe' not in drink_details:
        abort(422)

    drink_title = drink_details['title']
    drink_recipe = drink_details['recipe']

    try:
        new_drink = Drink(title=drink_title, recipe=json.dumps(drink_recipe))
        new_drink.insert()
        print(new_drink)

        drink_long = Drink.query.filter_by(title=drink_title).one_or_none()

        if not drink_long:
            abort(404)

        drink_long = [drink_long.long()]

        return jsonify({
            'success': True,
            'drinks': drink_long
        })
    except:
        abort(422)


'''
PATCH /drinks/<id>
    where <id> is the existing model id
    it should respond with a 404 error if <id> is not found
    it should update the corresponding row for <id>
    it should require the 'patch:drinks' permission
    it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink}
    where drink an array containing only the updated drink
    or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth(permission='patch:drinks')
def patch_drink(jwt, drink_id):
    drink_details = request.get_json()

    edit_drink = Drink.query.get(drink_id)
    if not edit_drink:
        abort(404)

    if 'title' in drink_details:
        drink_title = drink_details['title']
        edit_drink.title = drink_title

    if 'recipe' in drink_details:
        drink_recipe = json.dumps(drink_details['recipe'])
        edit_drink.recipe = drink_recipe

    try:
        edit_drink.update()
        drink_long = Drink.query.get(drink_id)
        drink_long = [drink_long.long()]

        return jsonify({
            'success': True,
            'drinks': drink_long
        })
    except:
        abort(422)


'''
DELETE /drinks/<id>
    where <id> is the existing model id
    it should respond with a 404 error if <id> is not found
    it should delete the corresponding row for <id>
    it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id}
    where id is the id of the deleted record
    or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth(permission='delete:drinks')
def delete_drink(jwt, drink_id):
    drink = Drink.query.get(drink_id)
    if not drink:
        abort(404)

    try:
        drink.delete()

        return jsonify({
            'success': True,
            'delete': drink_id
        })
    except:
        abort(422)


# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(400)
def bad_request(error):
    return jsonify({
                    "success": False,
                    "error": 400,
                    "message": "bad request"
                    }), 400


@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
                    "success": False,
                    "error": 401,
                    "message": "unauthorized"
                    }), 401


@app.errorhandler(403)
def forbidden(error):
    return jsonify({
                    "success": False,
                    "error": 403,
                    "message": "forbidden"
                    }), 403


@app.errorhandler(404)
def not_found(error):
    return jsonify({
                    "success": False,
                    "error": 404,
                    "message": "not found"
                    }), 404


@app.errorhandler(405)
def not_allowed(error):
    return jsonify({
                    "success": False,
                    "error": 405,
                    "message": "method not allowed"
                    }), 405


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False,
                    "error": 422,
                    "message": "unprocessable"
                    }), 422


'''
implement error handler for AuthError
    error handler should conform to general task above
'''


@app.errorhandler(AuthError)
def auth_error(exception):
    return jsonify({
        'success': False,
        'error': exception.status_code,
        'message': exception.error
    }), exception.status_code
