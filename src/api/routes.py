"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
from flask import Flask, request, jsonify, url_for, Blueprint
from api.models import db, User
from api.utils import generate_sitemap, APIException
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity

api = Blueprint('api', __name__)

    # Inicio  de sesión
@api.route('/login',  methods=['POST'])
def user_login():
    email=request.json.get('email')
    password=request.json.get('password')
    user=User.query.filter(User.email==email).first()
    # No encuentro Usuario

    if user == None:
        print(("Correo invalido"))
        return jsonify({"msg":"Inicio de sesion invalido"}), 401
    # Validacion de la clave

    if user.password==password:
        print("Clave ok")
        access_token=create_access_token(identity=user.id)
        refresh_token=create_refresh_token(identity=user.id)
        return jsonify({"token":access_token, "refresh":refresh_token}), 200

    else:
    # Clave Invalida
        print(("Clave invalida"))
        return jsonify({"msg":"Inicio de sesion invalido"}), 401

@api.route('/userdata')
@jwt_required()
def get_user_data():
    user_id=get_jwt_identity()
    user=User.query.get(user_id)
    return jsonify(user.serialize())


@api.route('/hello', methods=['POST', 'GET'])
def handle_hello():

    response_body = {
        "message": "Hello! I'm a message that came from the backend, check the network tab on the google inspector and you will see the GET request"
    }

    return jsonify(response_body), 200