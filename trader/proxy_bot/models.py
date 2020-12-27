from ..extensions import db
from ..utils.helper import time_now
from math import ceil

INIT_PROXY_WEIGHT = 100
INCREMENT_VALUE = 1
DECREMENT_INDEX = 9 / 10


class Proxies(db.Model):
    __tablename__ = 'proxies'

    proxy_id = db.Column(db.Integer, primary_key=True)
    proxy_type = db.Column(db.String, nullable=False)
    proxy_ip = db.Column(db.String, nullable=False)
    proxy_port = db.Column(db.String, nullable=False)
    proxy_weight = db.Column(db.Integer, nullable=False)
    proxy_good_try = db.Column(db.Integer, default=0)
    proxy_bad_try = db.Column(db.Integer, default=0)
    last_update_time = db.Column(db.DateTime, nullable=False, default=time_now, onupdate=time_now)

    def __init__(self, proxy_type, proxy_ip, proxy_port):
        self.proxy_type = proxy_type
        self.proxy_ip = proxy_ip
        self.proxy_port = proxy_port
        self.proxy_weight = INIT_PROXY_WEIGHT

    def get_object_format(self):
        return {
            self.proxy_type: "{}:{}".format(self.proxy_ip, self.proxy_port)
        }

    def inc_good_try(self, inc=INCREMENT_VALUE):
        self.proxy_good_try = self.proxy_good_try + inc

    def inc_bad_try(self, inc=INCREMENT_VALUE):
        self.proxy_bad_try = self.proxy_bad_try + inc

    def inc_weight(self, inc=INCREMENT_VALUE):
        self.proxy_weight = self.proxy_weight + inc

    def dec_weight(self, dec=DECREMENT_INDEX):
        self.proxy_weight = max(ceil(self.proxy_weight * dec) - 1, 0)

    def __repr__(self):
        return "<Proxy(proxy_id='%s', proxy_type='%s', proxy_ip='%s', proxy_port='%s', " \
               "proxy_weight='%s', proxy_good_try='%s', proxy_bad_try='%s')>" % (
                self.proxy_id, self.proxy_type, self.proxy_ip, self.proxy_port,
                self.proxy_weight, self.proxy_good_try, self.proxy_bad_try)
