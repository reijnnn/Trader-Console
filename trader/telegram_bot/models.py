from ..extensions   import db
from ..utils.helper import time_now

class Notification_status:
	QUEUE = 'QUEUE'
	SEND  = 'SEND'

class Notifications(db.Model):
	__tablename__ = 'notifications'

	notif_id            = db.Column(db.Integer,  primary_key=True)
	notif_status        = db.Column(db.String,   nullable=False)
	notif_date          = db.Column(db.DateTime, nullable=False, default=time_now)
	notif_text          = db.Column(db.String,   nullable=False)
	chat_id             = db.Column(db.Integer,  nullable=False)
	task_id             = db.Column(db.Integer)
	reply_to_message_id = db.Column(db.Integer)

	def __repr__(self):
		return "<Notification(notif_id='%s', notif_status='%s', notif_date='%s', notif_text='%s', chat_id='%s', task_id='%s')>" % (
						self.notif_id, self.notif_status, self.notif_date, self.notif_text, self.chat_id, self.task_id)
