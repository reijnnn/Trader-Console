from ..extensions import db
from .models      import Proxies

def get_proxy(proxy_id):
   proxy = db.session.query(Proxies).filter_by(proxy_id=proxy_id).first()
   return proxy
