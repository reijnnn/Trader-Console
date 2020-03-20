from ..extensions   import db
from ..utils.helper import time_now

class Task_status:
   ACTIVE    = 'ACTIVE'
   DROPPED   = 'DROPPED'
   CANCELED  = 'CANCELED'
   COMPLETED = 'COMPLETED'
   ENDED     = 'ENDED'

class Tasks(db.Model):
   __tablename__ = 'tasks'

   task_id             = db.Column(db.Integer,  primary_key=True)
   task_name           = db.Column(db.String,   nullable=False)
   task_params         = db.Column(db.String,   nullable=False)
   task_status         = db.Column(db.String,   nullable=False)
   task_date           = db.Column(db.DateTime, nullable=False, default=time_now)
   task_cnt_errors     = db.Column(db.Integer,  default=0)
   chat_id             = db.Column(db.Integer,  nullable=False)
   reply_to_message_id = db.Column(db.Integer)
   last_exec_time      = db.Column(db.DateTime)

   def __repr__(self):
      return "<Task(task_id='%s', task_name='%s', task_params='%s', task_status='%s', task_date='%s', chat_id='%s', task_cnt_errors='%s')>" % (
               self.task_id, self.task_name, self.task_params, self.task_status, self.task_date, self.chat_id, self.task_cnt_errors)
