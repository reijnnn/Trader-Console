from ..extensions   import db, logger

from ..task.tasks_service import get_task, complete_task
from ..utils.helper import wrap_code
from ..telegram_bot.notifications_service import add_notification
from .indicators    import moving_average_envelope, stochrsi
from .models        import Binance_klines

from sqlalchemy     import desc
from sqlalchemy.sql import func

from json     import loads
from datetime import datetime, timedelta

class Strategies():

	def __init__(self, api):
		self.binance_api = api

	@staticmethod
	def get_envelope_config():
		config = {
			'params': {
				'strategy': {
					'required': 1
					},

				'symbol' : {
					'required': 1,
					'check_function': 'check_symbol'
					},
				'interval': {
					'required': 1,
					'check_function': 'check_interval'
					},
				'calc_period' : {
					'default': 20,
					'check_function': 'check_calc_period'
					},
				'channels_env_percentage' : {
					'default' : '4,9,14',
					'check_function': 'check_comma_separated_ints'
					},
				'cross_channel_lvl' : {
					'required': 1,
					'check_function': 'check_channel_lvl'
				},

				'period' : {
					'default' : '3m',
					'check_function': 'check_period'
					},
				'duration' : {
					'default' : '1M',
					'check_function': 'check_duration'
					},
				'id' : {
					}
			},
			'help'  : {
				'examples'  : [
					'/task help strategy=envelope',
					'/task list strategy=envelope',
					'/task create strategy=envelope symbol=BTCUSDT interval=5m cross_channel_lvl=-1',
					'/task cancel id=[id]',
					'/task display id=[id]',
					'/task edit id=[id] period=1m duration=1w',
					'/task edit id=[id] channels_env_percentage=3,8,12'
				]
			}
		}
		return config

	@staticmethod
	def get_alert_config():
		config = {
			'params': {
				'strategy': {
					'required': 1
					},

				'symbol' : {
					'required': 1,
					'check_function': 'check_symbol'
					},
				'condition': {
					'required': 1,
					'check_function': 'check_condition'
					},
				'price' : {
					'required': 1,
					'check_function': 'check_price'
					},

				'period' : {
					'default' : '2m',
					'check_function': 'check_period'
					},
				'duration' : {
					'default' : '1M',
					'check_function': 'check_duration'
					},
				'id' : {
					}
			},
			'help'  : {
				'examples'  : [
					'/task help strategy=alert',
					'/task list strategy=alert',
					'/task create strategy=alert symbol=ETHUSDT condition=< price=180',
					'/task cancel id=[id]',
					'/task display id=[id]',
					'/task edit id=[id] price=190',
					'/task edit id=[id] period=1m duration=1w'
				]
			}
		}
		return config

	@staticmethod
	def get_price_config():
		config =  {
			'params': {
				'strategy': {
					'required': 1
					},

				'symbol' : {
					'required': 1,
					'check_function': 'check_symbol'
					},
				'interval': {
					'default' : '4h',
					'check_function': 'check_interval'
					},

				'id' : {
					}
			},
			'help'  : {
				'examples'  : [
					'/task create strategy=price symbol=ETHUSDT',
					'/task create strategy=price symbol=ETHUSDT interval=1h'
				]
			}
		}
		return config

	@staticmethod
	def get_volume_config():
		config =  {
			'params': {
				'strategy': {
					'required': 1
					},

				'symbol' : {
					'required': 1,
					'check_function': 'check_symbol'
					},
				'interval': {
					'required': 1,
					'check_function': 'check_interval'
					},
				'change_percentage' : {
					'default' : 1.2,
					'check_function': 'check_percentage'
					},

				'period' : {
					'default' : '2m',
					'check_function': 'check_period'
					},
				'duration' : {
					'default' : '1M',
					'check_function': 'check_duration'
					},
				'id' : {
					}
			},
			'help'  : {
				'examples'  : [
					'/task create strategy=volume symbol=ETHUSDT interval=1h',
					'/task edit id=[id] period=1m duration=1w'
				]
			}
		}
		return config

	@staticmethod
	def get_dump_price_history_config():
		config =  {
			'params': {
				'strategy': {
					'required': 1
					},

				'symbol' : {
					'required': 1,
					'check_function': 'check_symbol'
					},
				'interval': {
					'required': 1,
					'check_function': 'check_interval'
					},
				'start_date' : {
					'default' : '20190101',
					'check_function': 'check_date'
					},

				'period' : {
					'default' : '10m',
					'check_function': 'check_period'
					},
				'duration' : {
					'default' : '1M',
					'check_function': 'check_duration'
					},
				'id' : {
					}
			},
			'help'  : {
				'examples'  : [
					'/task create strategy=dump_price_history symbol=BTCUSDT interval=1h start_date=20190101',
					'/task edit id=[id] period=15m duration=1Y start_date=20180101'
				]
			}
		}
		return config

	def load_klines(self, symbol, interval, limit=250, start_time=None, end_time=None):
		if start_time and end_time:
			res, err = self.binance_api.klines(symbol=symbol, interval=interval, start_time=start_time, end_time=end_time, limit=limit)
		elif start_time:
			res, err = self.binance_api.klines(symbol=symbol, interval=interval, start_time=start_time, limit=limit)
		else:
			last_open_time = db.session.query(func.max(Binance_klines.open_time)).filter_by(symbol=symbol, interval=interval).scalar()
			res, err = self.binance_api.klines(symbol=symbol, interval=interval, start_time=last_open_time, limit=limit)

		if err:
			raise Exception("load_klines(symbol={}, interval={}, limit={}). Error: {}".format(symbol, interval, limit, err))

		for k in res:
			kline = Binance_klines(
				symbol     = symbol,
				interval   = interval,
				open_time  = k[0],
				open       = k[1],
				high       = k[2],
				low        = k[3],
				close      = k[4],
				volume     = k[5],
				num_trades = k[8]
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

		res   = res[0]
		kline = Binance_klines(
			symbol     = symbol,
			interval   = interval,
			open_time  = res[0],
			open       = res[1],
			high       = res[2],
			low        = res[3],
			close      = res[4],
			volume     = res[5],
			num_trades = res[8]
		)
		return kline

	def load_price(self, symbol):
		res, err = self.binance_api.price(symbol)
		if err:
			raise Exception("load_price(symbol={}). Error: {}".format(symbol, err))
		return res['price']

	def strategy_envelope(self, task_id):
		task    = get_task(task_id)
		params  = loads(task.task_params)

		period                  = int(params['calc_period'])
		symbol                  = params['symbol']
		interval                = params['interval']
		channels_env_percentage = params['channels_env_percentage']
		cross_channel_lvl       = int(params['cross_channel_lvl'])

		is_actual_klines = self.load_klines(symbol=symbol, interval=interval)
		if not is_actual_klines:
			return

		klines = db.session.query(Binance_klines).\
							filter_by(symbol=symbol, interval=interval).\
							order_by(desc(Binance_klines.open_time)).\
							limit(period * 3).\
							offset(0).\
							all()

		curr_price = float(klines[0].close)
		curr_time  = datetime.fromtimestamp(float(klines[0].open_time) / 1000).strftime('%Y-%m-%d %H:%M:%S')

		klines = [float(kline.close) for kline in klines]
		klines = klines[::-1]

		channels_env  = channels_env_percentage.split(',')
		channel_num   = 0
		for channel in channels_env:
			lb, cb, ub = moving_average_envelope(klines, period, int(channel) / 100)
			stoch_rsi  = stochrsi(klines, period)

			if abs(cross_channel_lvl) == channel_num + 1:

				if cross_channel_lvl < 0 and lb[-1] > curr_price or \
						cross_channel_lvl > 0 and ub[-1] < curr_price:

					notif_text = ("Task with id={} completed."        + "\n\n" +
									wrap_code("Time: {}"              + "\n"   +
											"Symbol: {}"              + "\n"   +
											"Interval: {}"            + "\n"   +
											"Price: {}"               + "\n"   +
											"Channel level: {}"       + "\n"   +
											"Stoch RSI: {}"           + "\n"   +
											"Envelope: {}, {}, {}")).format(
										task.task_id,
										curr_time,
										symbol,
										interval,
										round(curr_price, 3),
										cross_channel_lvl,
										round(stoch_rsi[-1], 3),
										round(lb[-1], 3), round(cb[-1], 3), round(ub[-1], 3)
									)
					complete_task(task_id)
					add_notification(text=notif_text,
									chat_id=task.chat_id,
									task_id=task.task_id,
									reply_to_message_id=task.reply_to_message_id)
				break
			channel_num += 1

	def strategy_alert(self, task_id):
		task    = get_task(task_id)
		params  = loads(task.task_params)

		curr_price = self.load_price(params['symbol'])

		if params['condition'] == '>' and float(curr_price) > float(params['price']) or \
				params['condition'] == '<' and float(curr_price) < float(params['price']):
			complete_task(task_id)
			add_notification(text=('Task "alert" with id={} completed.' + "\n\n" +
									wrap_code('Price: {}')
									).format(task_id, float(curr_price)),
							 chat_id=task.chat_id,
							 task_id=task.task_id,
							 reply_to_message_id=task.reply_to_message_id)

	def strategy_price(self, task_id):
		task    = get_task(task_id)
		params  = loads(task.task_params)

		kline = self.load_last_kline(params['symbol'], params['interval'])
		complete_task(task_id)
		add_notification(text=('Task "price" with id={} completed. '  + "\n\n" +
								wrap_code('Inverval: {}'              + "\n"   +
										'Current price: {}'           + "\n"   +
										'Low price: {}'               + "\n"   +
										'High price: {}'              + "\n"   +
										'Count trades: {}')
								).format(task_id, kline.interval, float(kline.close), float(kline.low), float(kline.high), kline.num_trades),
						 chat_id=task.chat_id,
						 task_id=task.task_id,
						 reply_to_message_id=task.reply_to_message_id)

	def strategy_volume(self, task_id):
		task    = get_task(task_id)
		params  = loads(task.task_params)

		is_actual_klines = self.load_klines(symbol=params['symbol'], interval=params['interval'], limit=12)
		if not is_actual_klines:
			return

		klines = db.session.query(Binance_klines).\
							filter_by(symbol=params['symbol'], interval=params['interval']).\
							order_by(desc(Binance_klines.open_time)).\
							limit(1).\
							all()

		curr_time   = datetime.fromtimestamp(float(klines[0].open_time) / 1000).strftime('%Y-%m-%d %H:%M:%S')
		open_price  = float(klines[0].open)
		close_price = float(klines[0].close)

		if abs((open_price - close_price) / open_price * 100) > float(params['change_percentage']):
			notif_text = ("Task with id={}"        + "\n"   +
							"Open position."       + "\n\n" +
							wrap_code("Time: {}"   + "\n"   +
									"Symbol: {}"   + "\n"   +
									"Interval: {}" + "\n"   +
									"Price: {}")
							).format(
								task.task_id,
								curr_time,
								params['symbol'],
								params['interval'],
								round(close_price, 3)
							)

			complete_task(task.task_id)
			add_notification(text=notif_text, chat_id=task.chat_id, task_id=task.task_id, reply_to_message_id=task.reply_to_message_id)

	def strategy_dump_price_history(self, task_id):
		task    = get_task(task_id)
		params  = loads(task.task_params)

		interval_type = params['interval'][-1]
		interval_val  = int(params['interval'][:-1])

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
		start_year  = int(params['start_date'][0:4])
		start_month = int(params['start_date'][4:6])
		start_day   = int(params['start_date'][6:8])

		start_time  = datetime(start_year, start_month, start_day, 0, 0)
		end_time    = start_time + interval_time * (limit_loads - 1)

		while True:
			binance_start_time = int(start_time.timestamp()) * 1000
			binance_end_time   = int(end_time.timestamp()) * 1000

			count_klines = db.session.query(Binance_klines).\
								filter_by(symbol=params['symbol'], interval=params['interval']).\
								filter(Binance_klines.open_time >= binance_start_time).\
								filter(Binance_klines.open_time <= binance_end_time).\
								count()

			if count_klines < limit_loads:
				is_less_limit = self.load_klines(symbol=params['symbol'], interval=params['interval'], limit=limit_loads, start_time=binance_start_time, end_time=binance_end_time)
				if is_less_limit:
					klines = db.session.query(Binance_klines).\
										filter_by(symbol=params['symbol'], interval=params['interval']).\
										filter(Binance_klines.open_time >= binance_start_time).\
										filter(Binance_klines.open_time <= binance_end_time).\
										order_by(Binance_klines.open_time).\
										all()

					pred_kline = klines[0]
					for kline in klines:
						curr_datetime = datetime.fromtimestamp(kline.open_time / 1000)
						pred_datetime = datetime.fromtimestamp(pred_kline.open_time / 1000)

						while pred_datetime + interval_time < curr_datetime:
							pred_datetime += interval_time

							new_kline = Binance_klines(
								symbol     = kline.symbol,
								interval   = kline.interval,
								open_time  = int(pred_datetime.timestamp() * 1000),
								open       = kline.close,
								high       = kline.close,
								low        = kline.close,
								close      = kline.close,
								volume     = 0,
								num_trades = 0
							)
							db.session.merge(new_kline)
							db.session.commit()

						pred_kline = kline
				return

			curr_time  = datetime.now().replace(minute=0, second=0, microsecond=0)

			start_time = end_time
			end_time   = min(start_time + interval_time * (limit_loads - 1), curr_time)

class Check_functions:

	@staticmethod
	def check_symbol(symbol):
		return symbol in [
				'BTCUSDT',
				'ETHUSDT',
				'BNBUSDT',
				'BCCUSDT',
				'NEOUSDT',
				'LTCUSDT',
				'XRPUSDT',
				'EOSUSDT',
				'IOTAUSDT',
				'XLMUSDT',
				'BCHABCUSDT',
				'BCHSVUSDT',
				'WAVESUSDT',
				'XMRUSDT',
				'ZECUSDT',
				'DASHUSDT',
				'ATOMUSDT'
				]

	@staticmethod
	def check_interval(interval):
		return interval in ['1m', '5m', '1h', '2h', '4h', '8h', '12h' , '1d', '1w', '1M']

	@staticmethod
	def check_condition(condition):
		return condition in ['>', '<']

	@staticmethod
	def check_calc_period(period):
		try:
			period = int(period)
			if period > 0 and period < 1000:
				return True
			return False
		except ValueError:
			return False

	@staticmethod
	def check_price(price):
		try:
			float(price)
			return True
		except ValueError:
			return False

	@staticmethod
	def check_percentage(percentage):
		try:
			percentage = float(percentage)
			if percentage >= 0.1 and percentage <= 100:
				return True
			return False
		except ValueError:
			return False

	@staticmethod
	def check_int(value):
		try:
			int(value)
			return True
		except ValueError:
			return False

	@staticmethod
	def check_period(period):
		period_type = period[-1]
		if period_type not in ['s', 'm', 'h', 'd']:
			return False

		try:
			period_value = period[:-1]
			int(period_value)
			return True
		except ValueError:
			return False

	@staticmethod
	def check_duration(duration):
		duration_type = duration[-1]
		if duration_type not in ['m', 'h', 'd', 'w', 'M', 'Y']:
			return False

		try:
			duration_value = duration[:-1]
			int(duration_value)
			return True
		except ValueError:
			return False

	@staticmethod
	def check_comma_separated_ints(str):
		for val in str.split(','):
			try:
				int(val)
			except ValueError:
				return False
		return True

	@staticmethod
	def check_date(date):
		try:
			if len(date) != 8:
				return False

			year  = int(date[0:4])
			month = int(date[4:6])
			day   = int(date[6:8])

			if year < 2010:
				return False
			if month == 0 or month > 12:
				return False
			if day == 0 or day > 31:
				return False

			datetime.strptime(date, '%Y%m%d')

		except ValueError:
			return False
		return True

	@staticmethod
	def check_channel_lvl(lvl):
		try:
			lvl = int(lvl)
			if abs(lvl) > 3 or lvl == 0:
				return False
		except ValueError:
			return False
		return True
