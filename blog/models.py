from blog import login
from blog import db
from datetime import datetime
from flask_login import UserMixin


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    access_level = db.Column(db.Integer)
    username = db.Column(db.String(64), index=True, unique=True)
    password = db.Column(db.String(128))
    fullname = db.Column(db.String(128), index=True)
    email = db.Column(db.String(120), index=True, unique=True)
    phone_number = db.Column(db.String(10), index=True, unique=True)
    homeworks = db.relationship("HomeWork", backref="author", lazy="dynamic")
    solutions = db.relationship("Solution", backref="author", lazy="dynamic")
    messages_sent = db.relationship("Messages",
                                            foreign_keys="Message.sender_id",
                                            backref="author", lazy="dynamic")
    messages_received = db.relationship("Messages",
                                            foreign_keys="Message.recipent_id",
                                            backref="author", lazy="dynamic")
    last_message_read_time = db.Column(db.DateTime)


    def __repr__(self):
        return "<User {}>".format(self.username)

    def check_password(self, password):
        return self.password == password

    def is_teacher(self):
        return self.access_level == 1

    def new_messages(self):
        last_read_time = self.last_message_read_time or datetime(1900, 1, 1)
        return Message.query.filter_by(recipient=self).filter(
                Message.timestamp > last_read_time).count()  


class HomeWork(db.Model):
    __tablename__ = 'homework'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32))
    unique_name = db.Column(db.String)
    path = db.Column(db.String)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    solutions = db.relationship("Solution", backref="problem", lazy="dynamic")
        

class Solution(db.Model):
    __tablename__ = 'solution'
    id = db.Column(db.Integer, primary_key=True)
    path = db.Column(db.String)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.now)
    homework_id = db.Column(db.Integer, db.ForeignKey("homework.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    name = db.Column(db.String(32))
    unique_name = db.Column(db.String)


class Messages(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    recipent_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.now)

    def __repr__(self):
        return "<Message {}>".format(self.body)
        