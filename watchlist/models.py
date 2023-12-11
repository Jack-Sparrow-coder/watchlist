from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from watchlist import db


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    username = db.Column(db.String(20))
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def validate_password(self, password):
        return check_password_hash(self.password_hash, password)

# 关联表（多对多）
movie_actor = db.Table('movie_actor',
    db.Column('id', db.Integer, primary_key=True),
    db.Column('movie_id', db.Integer, db.ForeignKey('movie.movie_id')),
    db.Column('actor_id', db.Integer, db.ForeignKey('actor.actor_id')),
    db.Column('role', db.String(20)),  # 角色信息，可以是主演、导演等
)


class Movie(db.Model):
    movie_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60))
    year = db.Column(db.String(4))
    date = db.Column(db.String(20))
    country = db.Column(db.String(20))
    type = db.Column(db.String(10))
    box = db.Column(db.Float)

    # 定义电影和演员的关系: 第一个参数表示和哪张表作关联，第二个参数表示通过哪张表和 "Actor"做关联，第三个参数表示反向字段名
    actors = db.relationship('Actor', secondary=movie_actor, back_populates='movies')


class Actor(db.Model):
    actor_id = db.Column(db.Integer, primary_key=True)
    actor_name = db.Column(db.String(30))
    gender = db.Column(db.String(4))
    nationality = db.Column(db.String(20))

    # 定义演员和电影的关系
    movies = db.relationship('Movie', secondary=movie_actor, back_populates='actors')

