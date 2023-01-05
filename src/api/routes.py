"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
from datetime import datetime, timezone
from flask import Flask, request, jsonify, url_for, Blueprint
from api.models import db, User, TokenBlocklist
from api.utils import generate_sitemap, APIException
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt
from flask_bcrypt import Bcrypt

api = Blueprint('api', __name__)

cripto=Bcrypt(Flask(__name__))

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
    if cripto.check_password_hash(user.password, password):
    # if user.password==password:
        print("Clave ok")
        access_token=create_access_token(identity=user.id)
        refresh_token=create_refresh_token(identity=user.id)
        return jsonify({"token":access_token, "refresh":refresh_token}), 200

    else:
    # Clave Invalida
        print(("Clave invalida"))
        return jsonify({"msg":"Inicio de sesion invalido"}), 401

@api.route('/logout', methods=['POST'])
@jwt_required()
def user_logout():
    jti = get_jwt()["jti"]
    now = datetime.now(timezone.utc)
    blocked_token=TokenBlocklist(jti=jti, created_at=now)
    db.session.add(blocked_token)
    db.session.commit()
    return jsonify(msg="JWT revoked")

@api.route('/userdata')
@jwt_required(refresh=True)
def get_user_data():
    user_id=get_jwt_identity()
    user=User.query.get(user_id)
    return jsonify(user.serialize())

@api.route('/signup', methods=['POST'])
def create_user():
    email=request.json.get('email')
    password=request.json.get('password')
    user=User(email=email, password=cripto.generate_password_hash(password).decode("utf-8"), is_active=True)
    db.session.add(user)
    db.session.commit()
    return jsonify({"msg":"Usuario creado"}), 201

@api.route('/updatepassword', methods=['PATCH'])
@jwt_required()
def patch_user_password():
    new_password=request.json.get("password")
    user_id=get_jwt_identity()
    user=User.query.get(user_id)
    user.password=cripto.generate_password_hash(new_password)
    db.session.add(user)
    db.session.commit()
    return jsonify({"msg":"Clave actualizada"}), 200

@api.route('/hello', methods=['POST', 'GET'])
def handle_hello():

    response_body = {
        "message": "Hello! I'm a message that came from the backend, check the network tab on the google inspector and you will see the GET request"
    }

    return jsonify(response_body), 200