from flask import abort, request

from authz import db
from authz.decorator import auth_required
from authz.model import User
from authz.schema import UserSchema

class UserController:
    def creat_user():
        if request.content_type != "application/json":
            abort(415)  # Bad media type.
        user_schema = UserSchema(only=["username", "password"])
        try:
            data = user_schema.load(request.get_json())  # Validate request data.
        except:
            abort(400) # Invalid request.
        if not data["username"] or not data["password"]:
            abort(400) # Empty data.
        try:
	        user = User.query.filter_by(username=data["username"]).first()
        except:
    	    abort(500) # Database error.
        if user is not None:
            abort(409) # User is already registered.
        user = User(username=data["username"], password=data["password"]) # Create new user.
        db.session.add(user) # Add to database session.
        try:
            db.session.commit() # Database CREATE query.
        except:
            db.session.rollback()
            abort(500) # Database error.
        user_schema = UserSchema()
        return {
                "user": user_schema.dump(user)
                },201

    @auth_required
    def get_users():
        try:
            users = User.query.all()
        except:
            abort(500) # Database error.
        users_schema = UserSchema(many=True)
        return {
                "users": users_schema.dump(users)
                }, 200

    @auth_required
    def get_user(user_id):
        try:
            user = User.query.get(user_id)
        except:
            abort(500) # Database error.
        if user is None:
            abort(404)
        user_schema = UserSchema()
        return {
                "user": user_schema.dump(user)
                }, 200

    @auth_required
    def update_user(user_id):
        if request.content_type != "application/json":
            abort(415)
        user_schema = UserSchema(only=["password"])
        try:
            data = user_schema.load(request.get_json()) # validate request data.
        except:
            abort(400)
        if not data["password"]:
            abort(400)
        try:
            user = User.query.get(user_id) # Select the user.
        except:
            abort(500) # Database error.
        if user is None:
            abort(404)
        user.password = data["password"]
        try:
            db.session.commit() # Database UPDATE query.
        except:
            db.session.rollback()
            abort(500) # Database error.
        user_schema = UserSchema()
        return {
                "user": user_schema.dump(user)
                }, 200

    @auth_required
    def delete_user(user_id):
        try:
            user = User.query.get(user_id)
        except:
            abort(500) # Database error.
        if user is None:
            abort(404)
        db.session.delete(user)
        try:
            db.session.commit() # Database DELETE query.
        except:
            db.session.rollback()
            abort(500) # Database error.
        return {}, 204
