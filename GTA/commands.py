import click

from GTA import app, db
from GTA.models import User, Gym, Venue, History


@app.cli.command()  # 注册为命令，可以传入 name 参数来自定义命令
@click.option('--drop', is_flag=True, help='Create after drop.')
def initdb(drop):
    """Initialize the database."""
    if drop:
        db.drop_all()
    db.create_all()
    click.echo('Initialized database.')


@app.cli.command()
def forge():
    """Generate fake data."""
    db.create_all()

    gyms = [
        {'name': '同济大学嘉定校区体育馆', 'pos': '曹安公路4800号', 'img': '同济大学嘉定校区体育馆.jpeg', 'res': 100, 'max': 150},
        {'name': '同济大学四平校区体育馆', 'pos': '四平路1239号', 'img': '同济大学嘉定校区体育馆.jpeg', 'res': 0, 'max': 150},
        {'name': '嘉定体育馆', 'pos': '嘉定新成路118号', 'img': '同济大学嘉定校区体育馆.jpeg', 'res': 0, 'max': 150}
    ]
    venues = [
        {'gym_id': 1, 'type': '篮球馆', 'max': 100, 'res1': 50, 'res2': 40},
        {'gym_id': 1, 'type': '游泳馆', 'max': 50, 'res1': 50, 'res2': 0},
        {'gym_id': 2, 'type': '篮球馆', 'max': 100, 'res1': 0, 'res2': 0},
        {'gym_id': 2, 'type': '游泳馆', 'max': 50, 'res1': 0, 'res2': 0},
        {'gym_id': 3, 'type': '篮球馆', 'max': 100, 'res1': 0, 'res2': 0},
        {'gym_id': 3, 'type': '游泳馆', 'max': 50, 'res1': 0, 'res2': 0}
    ]

    user = User(name='Admin', username='admin', is_admin=1)
    user.set_password("123")
    db.session.add(user)
    user = User(name='Custom', username='zjc', is_admin=0)
    user.set_password("123")
    db.session.add(user)
    for g in gyms:
        gym = Gym(name=g['name'], pos=g['pos'], img=g['img'], max=g['max'], res=g['res'])
        db.session.add(gym)
    for v in venues:
        venue = Venue(gym_id=v['gym_id'], type=v['type'], max=v['max'], res1=v['res1'], res2=v['res2'])
        db.session.add(venue)

    histories = [
        {'user_id': 1, 'res_year': '2023', 'res_mon': '6', 'res_day': '6', 'gym_id': 1, 'venue_id': 1},
        {'user_id': 1, 'res_year': '2023', 'res_mon': '5', 'res_day': '20', 'gym_id': 1, 'venue_id': 2}
    ]
    for h in histories:
        history = History(user_id=h['user_id'], res_year=h['res_year'], res_mon=h['res_mon'], res_day=h['res_day'], gym_id=h['gym_id'], venue_id=h['venue_id'])
        db.session.add(history)

    db.session.commit()
    click.echo('Done.')


@app.cli.command()
@click.option('--username', prompt=True, help='The username used to login.')
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='The password used to login.')
def admin(username, password):
    """Create user."""
    db.create_all()

    user = User.query.filter_by(username=username).first()  # 按username找到用户
    if user is not None:
        if user.admin == 1:
            click.echo('Updating user...')
            user.username = username
            user.set_password(password)
        else:
            user.admin = 1
            user.username = username
            user.set_password(password)
    else:
        click.echo('Creating user...')
        user = User(username=username, name='Admin')
        user.is_admin = 1
        user.set_password(password)
        db.session.add(user)

    db.session.commit()
    click.echo('Done.')


@app.cli.command()
@click.option('--username', prompt=True, help='The username used to login.')
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='The password used to login.')
def custom(username, password):
    """Create user."""
    db.create_all()

    user = User.query.filter_by(username=username).first()  # 按username找到用户
    if user is not None:
        click.echo('User exists...')
        click.echo('Failed.')
    else:
        click.echo('Creating user...')
        user = User(username=username, name='Custom')
        user.is_admin = 0
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        click.echo('Done.')
