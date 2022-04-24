import requests
import time
import threading
from random import randint

# noinspection PyPackageRequirements
from sqlalchemy import desc

from ..extensions import logger, db
from .models import Proxies
from .proxies_service import get_proxy


class ProxyBot(threading.Thread):

    def __init__(self, app=None):
        super(ProxyBot, self).__init__()
        self.is_active = False
        self.active_proxy_id = None
        self.app = None

        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.app = app

    def run(self):

        logger.info("Proxy bot started")

        self.is_active = True
        while True:
            while self.is_active:
                self.update_active_proxy_id()

                proxy = self.get_random_proxy()
                if proxy:
                    self.ping_proxy(proxy.proxy_id)

                time.sleep(self.app.config['PROXY_BOT_POLLING_FREQ'])

    def ping_proxy(self, proxy_id):
        proxy = get_proxy(proxy_id)

        if proxy is None:
            return False

        try:
            with requests.get(self.app.config['PROXY_BOT_CHECK_PATH'],
                              proxies=proxy.get_object_format(),
                              timeout=self.app.config['PROXY_BOT_TIMEOUT']) as _:
                proxy.inc_weight()
                proxy.inc_good_try()
                db.session.commit()
                return True
        except (Exception, ):
            proxy.dec_weight()
            proxy.inc_bad_try()
            db.session.commit()
            return False

    @staticmethod
    def get_random_proxy():
        query = db.session.query(Proxies)

        total_count = query.count()

        if total_count:
            offset = randint(1, total_count)
            query = query.offset(offset - 1).limit(1)

        proxy = query.first()

        return proxy

    def update_active_proxy_id(self):
        if self.active_proxy_id and self.ping_proxy(self.active_proxy_id):
            return

        top_proxies = db.session.query(Proxies). \
            order_by(desc(Proxies.proxy_weight), desc(Proxies.proxy_good_try)). \
            limit(self.app.config['PROXY_BOT_CNT_TOP_PROXY']). \
            all()
        for proxy in top_proxies:
            if self.ping_proxy(proxy.proxy_id):
                self.active_proxy_id = proxy.proxy_id
                return

    def get_active_proxy_id(self):
        return self.active_proxy_id

    def restart(self):
        self.is_active = True
        logger.info("Proxy bot started")

    def cancel(self):
        self.is_active = False
        logger.info("Proxy bot stopped")

    def get_status(self):
        return 'active' if self.is_active else 'inactive'

    def get_thread_status(self):
        return 'active' if self.is_alive() else 'inactive'
