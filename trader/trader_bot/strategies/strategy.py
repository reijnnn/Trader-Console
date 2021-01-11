from ...extensions import db
from ..models import BinanceKlines
from sqlalchemy.sql import func


class Strategy:

    def __init__(self, api):
        self.binance_api = api

    @staticmethod
    def get_config():
        pass

    def load_klines(self, symbol, interval, limit=250, start_time=None, end_time=None):
        if start_time and end_time:
            res, err = self.binance_api.klines(symbol=symbol, interval=interval, start_time=start_time,
                                               end_time=end_time, limit=limit)
        elif start_time:
            res, err = self.binance_api.klines(symbol=symbol, interval=interval, start_time=start_time, limit=limit)
        else:
            last_open_time = db.session.query(func.max(BinanceKlines.open_time)).filter_by(symbol=symbol,
                                                                                           interval=interval).scalar()
            res, err = self.binance_api.klines(symbol=symbol, interval=interval, start_time=last_open_time, limit=limit)

        if err:
            raise Exception(
                "load_klines(symbol={}, interval={}, limit={}). Error: {}".format(symbol, interval, limit, err))

        for k in res:
            kline = BinanceKlines(
                symbol=symbol,
                interval=interval,
                open_time=k[0],
                open=k[1],
                high=k[2],
                low=k[3],
                close=k[4],
                volume=k[5],
                num_trades=k[8]
            )
            db.session.merge(kline)
            db.session.commit()

        if len(res) < limit:
            return True
        return False

    def load_last_kline(self, symbol, interval='4h'):
        res, err = self.binance_api.klines(symbol=symbol, interval=interval, limit=1)
        if err:
            raise Exception("load_last_kline(symbol={}, interval={}). Error: {}".format(symbol, interval, err))

        res = res[0]
        kline = BinanceKlines(
            symbol=symbol,
            interval=interval,
            open_time=res[0],
            open=res[1],
            high=res[2],
            low=res[3],
            close=res[4],
            volume=res[5],
            num_trades=res[8]
        )
        return kline

    def load_price(self, symbol):
        res, err = self.binance_api.price(symbol)
        if err:
            raise Exception("load_price(symbol={}). Error: {}".format(symbol, err))
        return res['price']

    def execute(self, task_id):
        pass
