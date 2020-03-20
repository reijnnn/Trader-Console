from flask_sqlalchemy import SQLAlchemy

class SQLAlchemyDB(SQLAlchemy):
   def __init__(self, *args, **kwargs):
      super().__init__(*args, **kwargs)

   def set_app_instance(self, app):
      self.app = app
