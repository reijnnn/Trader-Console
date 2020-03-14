from ..extensions import db
from .models      import Notifications, Notification_status

def add_notification(text, chat_id, task_id='', status=Notification_status.QUEUE, reply_to_message_id=None):
	notification = Notifications(
		notif_status        = status,
		notif_text          = text,
		chat_id             = chat_id,
		task_id             = task_id,
		reply_to_message_id = reply_to_message_id
	)
	db.session.add(notification)
	db.session.commit()

def get_queue_notifications():
	notifications = db.session.query(Notifications).filter(Notifications.notif_status == Notification_status.QUEUE).all()
	return notifications

def update_notification_status(notif_id):
	db.session.query(Notifications).filter(Notifications.notif_id == notif_id).update(dict(notif_status=Notification_status.SEND))
	db.session.commit()
