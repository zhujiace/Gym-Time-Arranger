import os
import sys

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# SQLite URI compatible
WIN = sys.platform.startswith('win')
if WIN:
    prefix = 'sqlite:///'
else:
    prefix = 'sqlite:////'

# 创建一个程序对象
app = Flask(__name__)
# 我们需要设置签名所需的密钥
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev')
# 告诉SQLAlchemy数据库连接地址
app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(os.path.dirname(app.root_path), os.getenv('DATABASE_FILE', 'data.db'))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 初始化扩展，传入程序实例app
db = SQLAlchemy(app)
# 实例化扩展类
login_manager = LoginManager(app)


@login_manager.user_loader
def load_user(user_id):  # 创建用户加载回调函数，接受用户 ID 作为参数
    from GTA.models import User
    user = User.query.get(int(user_id))  # 用 ID 作为 User 模型的主键查询对应的用户
    return user  # 返回用户对象


# 如果未登录的用户访问对应的 URL，Flask-Login 会把用户重定向到登录页面，并显示一个错误提示
login_manager.login_view = 'login'
login_manager.login_message = '该操作需要登录账号'


# 上下文过程，把user带入所有模板中
# @app.context_processor
# def inject_user():
#     from watchlist.models import User
#     user = User.query.first()
#     return dict(user=user)


from GTA import views, errors, commands
