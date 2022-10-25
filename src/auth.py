from flask import Blueprint,request,jsonify
from werkzeug.security import check_password_hash,generate_password_hash
import validators
from src.database import User,db
from flask_jwt_extended import create_access_token,create_refresh_token,jwt_required,get_jwt_identity

auth = Blueprint("auth",__name__,url_prefix= "/api/v1/auth")

@auth.post("/register")
def register():
    username = request.json['username']
    email = request.json['email']
    password = request.json['password']

    # validate entries
    if len(password) < 8:
        return jsonify({"Error":"password too short,kindly try again"}),400

    if len(username) < 3:
        return jsonify({"Error":"username too short,kindly try again"}),400

    if not username.isalnum() or " " in username :
        return jsonify({"Error":"username should contain alphanumeric characters with no space"}),400
    
    if not validators.email(email):
         return jsonify({"Error":"You entered an invalid email address"}),400

    if User.query.filter_by(email=email).first() is not None:
        return jsonify({"Error":"Email already registered,would you want to login?"}),409 
    
    if User.query.filter_by(username = username).first() is not None:
         return jsonify({"Error":"username is already taken,try again"}),409

    pwd_hash = generate_password_hash(password)

    user = User(email= email,username=username,password=pwd_hash)
    db.session.add(user)
    db.session.commit()

    return jsonify(
        {
            "message": "User created successfully",
            "user":{
                "email":user.email,
                "username":user.username,
        }
        }
    ),201

@auth.post('/login')
def login():
    email = request.json.get('email','')
    password = request.json.get('password','')

    user = User.query.filter_by(email=email).first()

    if user:
        is_password_correct = check_password_hash(user.password,password)
        
        if is_password_correct :
            access = create_access_token(identity=user.id)
            refresh = create_refresh_token(identity=user.id)

            return jsonify({
                "message": "User log in successful",
                "user":{
                    "access_token":access,
                    "refresh_token":refresh,
                    "email":email,
                    "username":user.username

                }
            }),200
        else:
            return jsonify({
                "Error": "A wrong password was entered"
            }),401  

    else:
        return jsonify({"Error":"user does not exist"})         
          
@auth.post("/me")
@jwt_required()
def getUser():
    user_id = get_jwt_identity()

    user = User.query.filter_by(id=user_id).first()

    return jsonify({"email":user.email,
                    "username":user.username}),200

@auth.post("/token/refresh")
@jwt_required(refresh=True)
def refresh_access_token():

    identity = get_jwt_identity()
    access = create_access_token(identity=identity)

    return jsonify({
        "access token": access
    })


    

   