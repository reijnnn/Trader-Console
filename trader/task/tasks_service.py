from ..extensions     import logger, db
from .models          import Tasks, Task_status

from json     import loads
from datetime import datetime, timedelta

def get_active_tasks():
   active_tasks = db.session.query(Tasks).filter_by(task_status=Task_status.ACTIVE).all()
   return active_tasks

def complete_task(task_id):
   db.session.query(Tasks).filter_by(task_id=task_id).update(dict(task_status=Task_status.COMPLETED))
   db.session.commit()

def cancel_task(task_id):
   db.session.query(Tasks).filter_by(task_id=task_id).update(dict(task_status=Task_status.CANCELED))
   db.session.commit()

def drop_task(task_id):
   db.session.query(Tasks).filter_by(task_id=task_id).update(dict(task_status=Task_status.DROPPED))
   db.session.commit()

def get_task(task_id):
   task = db.session.query(Tasks).filter_by(task_id=task_id).first()
   return task

def add_task_error(task_id):
   db.session.query(Tasks).filter_by(task_id=task_id).update(dict(task_cnt_errors=(Tasks.task_cnt_errors + 1)))
   db.session.commit()

def get_task_errors(task_id):
   return db.session.query(Tasks.task_cnt_errors).filter_by(task_id=task_id).scalar()

def need_execute_task(task_id):
   task   = db.session.query(Tasks).filter_by(task_id=task_id).first()
   params = loads(task.task_params)

   if 'period' not in params:
      return True

   if not task.last_exec_time:
      return True

   period_type  = params['period'][-1]
   period_value = int(params['period'][:-1])

   td = timedelta(seconds=0)
   if period_type == 's':
      td = timedelta(seconds=period_value)
   if period_type == 'm':
      td = timedelta(minutes=period_value)
   if period_type == 'h':
      td = timedelta(hours=period_value)
   if period_type == 'd':
      td = timedelta(days=period_value)

   if task.last_exec_time + td < datetime.now():
      return True

   return False

def update_task_exec_time(task_id):
   db.session.query(Tasks).filter_by(task_id=task_id).update(dict(last_exec_time=datetime.now().replace(microsecond=0)))
   db.session.commit()

def need_end_task(task_id):
   task   = db.session.query(Tasks).filter_by(task_id=task_id).first()
   params = loads(task.task_params)

   if 'duration' not in params:
      return False

   period_type  = params['duration'][-1]
   period_value = int(params['duration'][:-1])

   td = timedelta(seconds=0)
   if period_type == 'm':
      td = timedelta(minutes=period_value)
   if period_type == 'h':
      td = timedelta(hours=period_value)
   if period_type == 'd':
      td = timedelta(days=period_value)
   if period_type == 'w':
      td = timedelta(weeks=period_value)
   if period_type == 'M':
      td = timedelta(days=period_value * 31)
   if period_type == 'Y':
      td = timedelta(days=period_value * 365)

   if task.task_date + td < datetime.now():
      return True

   return False

def end_task(task_id):
   db.session.query(Tasks).filter_by(task_id=task_id).update(dict(task_status=Task_status.ENDED))
   db.session.commit()
