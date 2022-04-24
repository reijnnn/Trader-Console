from datetime import datetime, timedelta
from json import loads

from ...extensions import db
from ...task.tasks_service import get_task
from ..models import BinanceKlines
from .strategy import Strategy


class DumpPriceHistory(Strategy):

    @staticmethod
    def get_config():
        config = {
            'params': {
                'strategy': {
                    'required': 1
                },

                'symbol': {
                    'required': 1,
                    'check_function': 'check_symbol'
                },
                'interval': {
                    'required': 1,
                    'check_function': 'check_interval'
                },
                'start_date': {
                    'default': '20190101',
                    'check_function': 'check_date'
                },

                'period': {
                    'default': '10m',
                    'check_function': 'check_period'
                },
                'duration': {
                    'default': '1M',
                    'check_function': 'check_duration'
                },
                'id': {
                }
            },
            'help': {
                'examples': [
                    '/task create strategy=dump_price_history symbol=BTCUSDT interval=1h start_date=20190101',
                    '/task edit id=[id] period=15m duration=1Y start_date=20180101'
                ]
            }
        }
        return config

    def execute(self, task_id):
        task = get_task(task_id)
        params = loads(task.task_params)

        interval_type = params['interval'][-1]
        interval_val = int(params['interval'][:-1])

        if interval_type == 'm':
            interval_time = timedelta(minutes=interval_val)
        elif interval_type == 'h':
            interval_time = timedelta(hours=interval_val)
        elif interval_type == 'd':
            interval_time = timedelta(days=interval_val)
        elif interval_type == 'w':
            interval_time = timedelta(days=interval_val * 7)
        elif interval_type == 'M':
            interval_time = timedelta(days=31)
        else:
            interval_time = timedelta(days=0)

        limit_loads = 100
        start_year = int(params['start_date'][0:4])
        start_month = int(params['start_date'][4:6])
        start_day = int(params['start_date'][6:8])

        start_time = datetime(start_year, start_month, start_day, 3, 0)
        end_time = start_time + interval_time * (limit_loads - 1)

        while True:
            binance_start_time = int(start_time.timestamp()) * 1000
            binance_end_time = int(end_time.timestamp()) * 1000

            count_klines = db.session.query(BinanceKlines). \
                filter_by(symbol=params['symbol'], interval=params['interval']). \
                filter(BinanceKlines.open_time >= binance_start_time). \
                filter(BinanceKlines.open_time <= binance_end_time). \
                count()

            if count_klines < limit_loads:
                is_less_limit = self.load_klines(symbol=params['symbol'], interval=params['interval'],
                                                 limit=limit_loads, start_time=binance_start_time,
                                                 end_time=binance_end_time)
                if is_less_limit:
                    klines = db.session.query(BinanceKlines). \
                        filter_by(symbol=params['symbol'], interval=params['interval']). \
                        filter(BinanceKlines.open_time >= binance_start_time). \
                        filter(BinanceKlines.open_time <= binance_end_time). \
                        order_by(BinanceKlines.open_time). \
                        all()

                    pred_kline = klines[0]
                    for kline in klines:
                        curr_datetime = datetime.fromtimestamp(kline.open_time / 1000)
                        pred_datetime = datetime.fromtimestamp(pred_kline.open_time / 1000)

                        while pred_datetime + interval_time < curr_datetime:
                            pred_datetime += interval_time

                            new_kline = BinanceKlines(
                                symbol=kline.symbol,
                                interval=kline.interval,
                                open_time=int(pred_datetime.timestamp() * 1000),
                                open=kline.close,
                                high=kline.close,
                                low=kline.close,
                                close=kline.close,
                                volume=0,
                                num_trades=0
                            )
                            db.session.merge(new_kline)
                            db.session.commit()

                        pred_kline = kline
                return

            curr_time = datetime.now().replace(minute=0, second=0, microsecond=0)

            start_time = end_time
            end_time = min(start_time + interval_time * (limit_loads - 1), curr_time)
