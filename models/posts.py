import datetime
import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase


class Post(SqlAlchemyBase):
    __tablename__ = 'posts'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    text = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    image_path = sqlalchemy.Column(sqlalchemy.String, nullable=True)  # путь к изображению, если есть
    created_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)

    author_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    author = orm.relationship('User')
    
    # Связь с комментариями
    comments = orm.relationship('Comment', back_populates='post')

    def __repr__(self):
        return f'<Post {self.id}> Автор: {self.author_id}'


class Comment(SqlAlchemyBase):
    __tablename__ = 'comments'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    text = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)

    author_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    author = orm.relationship('User')

    post_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('posts.id'))
    post = orm.relationship('Post', back_populates='comments')

    def __repr__(self):
        return f'<Comment {self.id}> Автор: {self.author_id} Пост: {self.post_id}'
