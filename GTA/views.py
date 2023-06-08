from flask import render_template, request, url_for, redirect, flash
from flask_login import login_user, login_required, logout_user, current_user

from GTA import app, db
from GTA.models import User, Gym, Venue, Reservation, History

import datetime
from datetime import date
from sqlalchemy import or_


# 装饰器，为这个函数绑定一个URL
# 当用户访问这个URL的时候，就会触发这个函数
# 获取返回值，把返回值显示在浏览器窗口上
@app.route('/', methods=['GET', 'POST'])
def index():
    key = ''
    if request.method == 'POST':
        if 'submit2' in request.form:
            if not current_user.is_authenticated:  # 如果当前用户未认证
                # 视图函数代表某个路由的端点
                # url_for第一个参数就是端点值，默认为视图函数的名称
                # 用于生成URL
                return redirect(url_for('index'))  # 重定向到主页

            # 获取表单数据
            name = request.form['name']
            pos = request.form['pos']
            # 验证数据
            if not name or not pos or len(name) > 60 or len(pos) > 60:
                flash('Invalid input.')  # 显示错误提示
                return redirect(url_for('index'))  # 重定向回主页
            # 保存表单数据到数据库
            gym = Gym(name=name, pos=pos)  # 创建记录
            db.session.add(gym)  # 添加到数据库会话
            db.session.commit()  # 提交数据库会话
            flash('Item created.')  # 显示成功创建的提示
            return redirect(url_for('index'))  # 重定向回主页
        elif 'submit1' in request.form:
            # 获取表单数据
            key = request.form['key']
            gyms = Gym.query.filter(Gym.name.like(f'%{key}%')).all()
            return render_template('index.html', gyms=gyms, key=key)  # 重定向回主页

    gyms = Gym.query.all()
    # 使用render_template()可以把模板渲染出来
    # 必须传入的参数是模板文件名（相对于templates根目录的文件路径）
    # 还要把模板内部使用的变量通过关键字传入这个函数
    return render_template('index.html', gyms=gyms, key=key)


@app.route('/gym/check/<int:gym_id>', methods=['GET', 'POST'])
@login_required
def check(gym_id):
    # movie = Movie.query.get_or_404(gym_id)
    gym = Gym.query.get_or_404(gym_id)
    venues = Venue.query.filter_by(gym_id=gym_id)

    dates = ['今天', '明天']  # 下拉选择框的选项

    if request.method == 'POST':
        select_date = request.form['date']
        return render_template('check.html', gym=gym, venues=venues, dates=dates, select_date=select_date)

    select_date = '今天'
    return render_template('check.html', gym=gym, venues=venues, dates=dates,
                           select_date=select_date)  # 传入被编辑的体育场馆记录


@app.route('/gym/check/<int:gym_id>/<int:venue_id>', methods=['GET', 'POST'])
@login_required
def check_venue(gym_id, venue_id):
    key = ''
    reservations = Reservation.query.filter_by(gym_id=gym_id, venue_id=venue_id).all()
    now = datetime.datetime.now()
    res_list = []
    user = User.query.all()
    gyms = Gym.query.all()
    venues = Venue.query.all()

    if request.method == 'POST':
        key = request.form['key']
        reservations = Reservation.query.filter(or_(Reservation.name.like(f'%{key}%'), Reservation.phone.like(f'%{key}%'))).all()
        for res in reservations:
            if res.res_day == now.strftime('%d') and res.res_mon == now.strftime('%m') and res.res_year == now.strftime(
                    '%Y'):
                res_list.append(res)
        return render_template('check_venue.html', reservations=res_list, gyms=gyms, venues=venues, user=user, key=key)  # 传入被编辑的体育场馆记录

    for res in reservations:
        if res.res_day == now.strftime('%d') and res.res_mon == now.strftime('%m') and res.res_year == now.strftime('%Y'):
            res_list.append(res)

    return render_template('check_venue.html', reservations=res_list, gym=gyms, venues=venues, user=user, key=key)  # 传入被编辑的体育场馆记录


@app.route('/gym/reserve/<int:gym_id>/<int:venue_id>/<string:date>', methods=['GET', 'POST'])
@login_required
def reserve(gym_id, venue_id, date):
    if request.method == 'POST':  # 处理编辑表单的提交请求
        name = request.form['name']
        phone = request.form['pos']

        if not name or not phone:
            flash('Invalid input.')
            return redirect(url_for('reserve', gym_id=gym_id, venue_id=venue_id, date=date))

        # r = Reservation.query.filter_by(user_id=current_user.id)
        # if r is not None:
        #     flash('You have a reservation at this time!')
        #     return redirect(url_for('reserve', gym_id=gym_id, venue_id=venue_id, date=date))  # 重定向回对应的编辑页面

        res = Reservation(user_id=current_user.id, gym_id=gym_id, venue_id=venue_id, name=name, phone=phone)
        now = datetime.datetime.now()
        if date == '今天':
            res.res_year = now.strftime('%Y')
            res.res_mon = now.strftime('%m')
            res.res_day = now.strftime('%d')
        else:
            tomorrow = now + datetime.timedelta(days=1)
            res.res_year = tomorrow.strftime('%Y')
            res.res_mon = tomorrow.strftime('%m')
            res.res_day = tomorrow.strftime('%d')
        res.year = now.strftime('%Y')
        res.mon = now.strftime('%m')
        res.day = now.strftime('%d')
        res.hour = now.strftime('%H')
        res.min = now.strftime('%M')
        res.sec = now.strftime('%S')
        res.state = 0
        db.session.add(res)
        db.session.commit()  # 提交数据库会话
        flash('Reservation submitted.')
        return redirect(url_for('check', gym_id=gym_id))  # 重定向回查看

    return render_template('reserve.html')  # 传入被编辑的体育场馆记录


@app.route('/reservation', methods=['GET', 'POST'])
@login_required
def reservation():
    # if request.method == 'POST':
    #     return redirect(url_for('reservation'))

    reservations = Reservation.query.filter_by(user_id=current_user.id).all()
    gyms = Gym.query.all()
    venues = Venue.query.all()

    return render_template('reservation.html', reservations=reservations, gyms=gyms, venues=venues)


@app.route('/verify', methods=['GET', 'POST'])
@login_required
def verify():
    # if request.method == 'POST':
    #     return redirect(url_for('reservation'))

    reservations = Reservation.query.filter_by(state=0).all()
    gyms = Gym.query.all()
    venues = Venue.query.all()
    user = User.query.all()
    return render_template('verify.html', reservations=reservations, gyms=gyms, venues=venues, user=user)


@app.route('/gym/edit/<int:gym_id>', methods=['GET', 'POST'])
@login_required
def edit(gym_id):
    # movie = Movie.query.get_or_404(gym_id)
    gym = Gym.query.get_or_404(gym_id)

    if request.method == 'POST':  # 处理编辑表单的提交请求
        name = request.form['name']
        pos = request.form['pos']

        if not name or not pos or len(pos) > 60 or len(name) > 60:
            flash('Invalid input.')
            return redirect(url_for('edit', gym_id=gym_id))  # 重定向回对应的编辑页面

        gym.name = name  # 更新名称
        gym.pos = pos  # 更新位置
        db.session.commit()  # 提交数据库会话
        flash('Item updated.')
        return redirect(url_for('index'))  # 重定向回主页

    return render_template('edit.html', gym=gym)  # 传入被编辑的体育场馆记录


@app.route('/gym/delete/<int:gym_id>', methods=['POST'])  # 一般删除修改页面、表单提交页面、API页面因为需要安全性所以只接受POST请求
@login_required
def delete(gym_id):
    gym = Gym.query.get_or_404(gym_id)  # 获取体育场馆记录
    db.session.delete(gym)  # 删除对应的记录
    db.session.commit()  # 提交数据库会话
    flash('Item deleted.')
    return redirect(url_for('index'))  # 重定向回主页


@app.route('/reservation/retry/<int:res_id>', methods=['POST'])  # 一般删除修改页面、表单提交页面、API页面因为需要安全性所以只接受POST请求
@login_required
def retry(res_id):
    res = Reservation.query.get_or_404(res_id)  # 获取体育场馆记录
    res.state = 0
    db.session.commit()  # 提交数据库会话
    flash('Retry.')
    return redirect(url_for('reservation'))  # 重定向回主页


@app.route('/verify/agree/<int:res_id>', methods=['POST'])  # 一般删除修改页面、表单提交页面、API页面因为需要安全性所以只接受POST请求
@login_required
def agree(res_id):
    now = datetime.datetime.now()
    tomorrow = now + datetime.timedelta(days=1)

    res = Reservation.query.get_or_404(res_id)
    res.state = 1
    gym = Gym.query.get_or_404(res.gym_id)
    gym.res = gym.res + 1
    venue = Venue.query.get_or_404(res.venue_id)
    if res.res_day == now.strftime('%d') and res.res_mon == now.strftime('%m') and res.res_year == now.strftime('%Y'):
        venue.res1 = venue.res1 + 1
    elif res.res_day == tomorrow.strftime('%d') and res.res_mon == tomorrow.strftime(
            '%m') and res.res_year == tomorrow.strftime('%Y'):
        venue.res2 = venue.res2 + 1
    db.session.commit()  # 提交数据库会话
    flash('Agreed.')
    reservations = Reservation.query.filter_by(state=0).all()
    gyms = Gym.query.all()
    venues = Venue.query.all()
    user = User.query.all()
    return render_template('verify.html', reservations=reservations, gyms=gyms, venues=venues, user=user)


@app.route('/verify/refuse/<int:res_id>', methods=['POST'])  # 一般删除修改页面、表单提交页面、API页面因为需要安全性所以只接受POST请求
@login_required
def refuse(res_id):
    res = Reservation.query.get_or_404(res_id)  # 获取体育场馆记录
    res.state = 2
    db.session.commit()  # 提交数据库会话
    flash('Refused.')
    reservations = Reservation.query.filter_by(state=0).all()
    gyms = Gym.query.all()
    venues = Venue.query.all()
    user = User.query.all()
    return render_template('verify.html', reservations=reservations, gyms=gyms, venues=venues, user=user)


@app.route('/reservation/delete/<int:res_id>', methods=['POST'])  # 一般删除修改页面、表单提交页面、API页面因为需要安全性所以只接受POST请求
@login_required
def delete_res(res_id):
    now = datetime.datetime.now()
    tomorrow = now + datetime.timedelta(days=1)

    res = Reservation.query.get_or_404(res_id)  # 获取体育场馆记录

    gym = Gym.query.get_or_404(res.gym_id)
    gym.res = gym.res - 1
    venue = Venue.query.get_or_404(res.venue_id)
    if res.res_day == now.strftime('%d') and res.res_mon == now.strftime('%m') and res.res_year == now.strftime('%Y'):
        venue.res1 = venue.res1 - 1
    elif res.res_day == tomorrow.strftime('%d') and res.res_mon == tomorrow.strftime(
            '%m') and res.res_year == tomorrow.strftime('%Y'):
        venue.res2 = venue.res2 - 1

    db.session.delete(res)  # 删除对应的记录
    db.session.commit()  # 提交数据库会话
    flash('Reservation deleted.')
    reservations = Reservation.query.filter_by(user_id=current_user.id).all()
    gyms = Gym.query.all()
    venues = Venue.query.all()
    return render_template('reservation.html', reservations=reservations, gyms=gyms, venues=venues)


@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        name = request.form['name']

        if not name or len(name) > 20:
            flash('Invalid input.')
            return redirect(url_for('settings'))

        current_user.name = name
        # current_user 会返回当前登录用户的数据库记录对象
        # user = User.query.first()
        # user.name = name
        db.session.commit()
        flash('Settings updated.')
        return redirect(url_for('index'))

    return render_template('settings.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            flash('Invalid input.')
            return redirect(url_for('login'))

        user = User.query.filter_by(username=username).first()
        # 验证用户名和密码是否一致
        if user is not None:
            if username == user.username and user.validate_password(password):
                login_user(user)  # 登入用户
                flash('Login success.')
                return redirect(url_for('index'))  # 重定向到主页

        flash('Invalid username or password.')  # 如果验证失败，显示错误消息
        return redirect(url_for('login'))  # 重定向回登录页面

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm = request.form['confirm']

        if not username or not password or not confirm:
            flash('Invalid input.')
            return redirect(url_for('register'))

        user = User.query.filter_by(username=username).first()
        # 验证用户名和密码是否一致
        if user is not None:
            flash('Username already exists.')
            return redirect(url_for('register'))
        elif password != confirm:
            flash('Two passwords do not match.')
            return redirect(url_for('register'))
        else:
            user = User(username=username, name='momo')
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash('Register success.')
            return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/logout')
@login_required  # 用于视图保护
def logout():
    logout_user()  # 用于视图保护，后面会详细介绍
    flash('Goodbye.')
    return redirect(url_for('index'))  # 重定向回首页


@app.route('/history')
@login_required  # 用于视图保护
def history():
    if current_user.is_authenticated:
        histories = History.query.filter_by(user_id=current_user.id).all()
        date_list = []
        for h in histories:
            date_h = date(int(h.res_year), int(h.res_mon), int(h.res_day))
            date_list.append(date_h)
        gym = Gym.query.all()
        venue = Venue.query.all()
        return render_template('history.html', history=date_list, gym=gym, venue=venue)
    return render_template('history.html')
