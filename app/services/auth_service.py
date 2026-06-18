# app/services/auth_service.py

import re
import hashlib

from app.models.account import Account
from app.extensions import db

class AuthService:

    @staticmethod
    def hash_password(password, secret_key):
        value = password + secret_key

        return hashlib.sha1(value.encode()).hexdigest()

    @staticmethod
    def register_user(username, password, email, secret_key):

        if Account.query.filter_by(username=username).first():
            return False, "Account already exists!"

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return False, "Invalid email address!"

        if not re.match(r"[A-Za-z0-9]+", username):
            return False, "Username must contain only characters and numbers!"

        if not username or not password or not email:
            return False, "Please fill out the form!"

        hashed_password = AuthService.hash_password(
            password,
            secret_key
        )

        account = Account(
            username=username,
            password=hashed_password,
            email=email
        )

        db.session.add(account)
        db.session.commit()

        return True, "You have successfully registered!"

    @staticmethod
    def authenticate_user(username, password, secret_key):

        account = Account.query.filter_by(
            username=username
        ).first()

        if not account:
            return False, None, "Incorrect username/password!"

        hashed_password = AuthService.hash_password(
            password,
            secret_key
        )

        if account.password != hashed_password:
            return False, None, "Incorrect password!"

        return True, account, "Login successful"

