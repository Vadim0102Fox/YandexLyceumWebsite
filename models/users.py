import datetime
import sqlalchemy
from sqlalchemy import orm
from flask_login import UserMixin

from werkzeug.security import generate_password_hash, check_password_hash
from .db_session import SqlAlchemyBase


class User(SqlAlchemyBase, UserMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    description = sqlalchemy.Column(sqlalchemy.String, nullable=True, default='')
    avatar_path = sqlalchemy.Column(sqlalchemy.String, default='/static/img/user_icon.png')
    email = sqlalchemy.Column(sqlalchemy.String, index=True, unique=True, nullable=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    role = sqlalchemy.Column(sqlalchemy.Integer, default=1)  # 1 - user, 2 - admin
    created_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    
    # Связь с постами и комментариями
    posts = orm.relationship("Post", back_populates="author")
    comments = orm.relationship("Comment", back_populates="author")

    def __repr__(self):
        return f'<User {self.id}> {self.name} {self.email}'

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)
