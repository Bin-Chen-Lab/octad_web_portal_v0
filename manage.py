from flask_script import Manager, Shell
from flask_migrate import MigrateCommand, Migrate
from app import app, db
from models.profile import User


migrate = Migrate(app, db)
manager = Manager(app)
#if app.config['DEBUG'] or app.config['TESTING']:
manager.add_command('db', MigrateCommand)


@manager.command
def init_admin():
    ''' To be used only for the first time during setup '''
    password = 'reset@123'
    print password

    login = User('admin', password, 0, True)
    login.save()
    # from app import db
    # db.session.commit()


manager.add_command('shell', Shell(make_context=lambda:{'app': app, 'db': db}))

if __name__ == '__main__':
    manager.run()
    # app.run(host="0.0.0.0", port=8000)
    # app.run(host="192.168.100.151", port=5005)
