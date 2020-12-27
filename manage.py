import unittest
from flask_script import Manager, prompt_bool
from flask_migrate import MigrateCommand
from flask import current_app
from trader import create_app

manager = Manager(create_app)
manager.add_command('db', MigrateCommand)
manager.add_option('-c', '--config', dest="config", required=False, help="Config file")
manager.add_option('-m', '--mode', dest="mode", required=False, help="Application mode")


@manager.command
def reset_db():
    """ Recreate database tables """
    print('Start "reset_db"')

    from trader.extensions import db

    if prompt_bool('Are you sure you want to lose all your data in "{}"'.format(
            current_app.config['SQLALCHEMY_DATABASE_URI'])):
        db.drop_all()
        db.create_all()
        print("Done")

    print('Finish "reset_db"')


@manager.option('-l', '--login', dest='login', required=True, help="User login")
@manager.option('-p', '--password', dest='password', required=True, help="User password")
def add_root_user(login, password):
    """ Add root user with role 'SUPER_ADMIN' """
    print('Start "add_root_user" with params "{}, {}"'.format(login, '***'))

    from trader.user.models import Users, UserStatus, UserRole
    from trader.extensions import db

    user = Users()
    user.login = login
    user.role = UserRole.SUPER_ADMIN
    user.status = UserStatus.ACTIVE
    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    print('Finish "add_root_user"')


@manager.option('-t', '--table', dest='table', required=True, help="Table name")
def print_table(table):
    """ Display all table rows """
    print('Start "print_table" with params "{}"'.format(table))

    from trader.extensions import db

    try:
        result = db.session.execute("SELECT * FROM '{}';".format(table))
    except Exception as e:
        print('QUERY. ERROR. {}'.format(e))
    else:
        row_count = 0
        for row in result:
            row_count = row_count + 1
            print(row)
        if row_count == 0:
            print("QUERY.WARNING. No data found")
        result.close()

    print('Finish "print_table"')


@manager.command
def print_all_routes():
    """ Display all app routes """
    print(current_app.url_map)


@manager.command
def run_unittests():
    """ Run all unittests """
    print('Start "run_unittests"')

    if prompt_bool('Are you sure you want to lose all your data in "{}"'.format(
            current_app.config['SQLALCHEMY_DATABASE_URI'])):
        tests = unittest.TestLoader().discover('tests', pattern='test_*.py')
        result = unittest.TextTestRunner(verbosity=2).run(tests)
        print(result)

    print('Finish "run_unittests"')


if __name__ == "__main__":
    manager.run()
