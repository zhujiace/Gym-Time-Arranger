from flask_login import UserMixin
# Werkzeug 内置了用于生成和验证密码散列值的函数
from werkzeug.security import generate_password_hash, check_password_hash

from GTA import db


# 让存储用户的 User 模型类继承 Flask-Login 提供的 UserMixin 类
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    username = db.Column(db.String(20))
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Integer)  # 是否为管理员 1-管理员 0-非管理员

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def validate_password(self, password):
        return check_password_hash(self.password_hash, password)


class Gym(db.Model):  # 体育场馆
    id = db.Column(db.Integer, primary_key=True)  # 主键
    name = db.Column(db.String(60))  # 体育馆名称
    pos = db.Column(db.String(60))  # 体育馆位置
    img = db.Column(db.String(60))  # 图片位置
    max = db.Column(db.Integer)
    res = db.Column(db.Integer)


class Venue(db.Model):  # 具体场馆
    id = db.Column(db.Integer, primary_key=True)  # 主键
    gym_id = db.Column(db.Integer)
    type = db.Column(db.String(60))
    max = db.Column(db.Integer)
    res1 = db.Column(db.Integer)
    res2 = db.Column(db.Integer)


class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    gym_id = db.Column(db.Integer)
    venue_id = db.Column(db.Integer)
    res_year = db.Column(db.String(60))
    res_mon = db.Column(db.String(60))
    res_day = db.Column(db.String(60))
    name = db.Column(db.String(60))
    phone = db.Column(db.String(60))
    year = db.Column(db.String(60))
    mon = db.Column(db.String(60))
    day = db.Column(db.String(60))
    hour = db.Column(db.String(60))
    min = db.Column(db.String(60))
    sec = db.Column(db.String(60))
    state = db.Column(db.Integer)  # 0-审核中 1-审核通过 2-已过期


class History(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    res_year = db.Column(db.String(60))
    res_mon = db.Column(db.String(60))
    res_day = db.Column(db.String(60))
    gym_id = db.Column(db.Integer)
    venue_id = db.Column(db.Integer)