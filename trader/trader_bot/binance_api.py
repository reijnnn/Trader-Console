import hmac
import hashlib
import time
import requests

class Binance_api():
	def __init__(self, key, secret):
		self.public_api_url  = 'https://api.binance.com/api/v1/'
		self.private_api_url = 'https://api.binance.com/api/v3/'
		self.key	 = key
		self.secret  = bytearray(secret, encoding='utf-8')

	def public_request(self, method, api_method, **payload):
		url = self.public_api_url + api_method
		try:
			r = requests.request(method, url, params=payload)
			r.raise_for_status()

			if r.status_code == 200:
				return r.json(), None
			else:
				return None, 'Public request error. Status code = '.format(r.status_code)
		except Exception as e:
			return None, 'Public request exception: {}'.format(str(e))

	def private_request(self, method, api_method, **payload):
		url = self.private_api_url + api_method

		payload['timestamp'] = self.current_time()
		payload['signature'] = self.signature(**payload)

		headers = {
			'X-MBX-APIKEY': self.key
		}

		try:
			r = requests.request(method, url, params=payload, headers=headers)
			r.raise_for_status()

			if r.status_code == 200:
				return r.json(), None
			else:
				return None, 'Private request error. Status code = '.format(r.status_code)
		except Exception as e:
			return None, 'Private request exception'

	def signature(self, **payload):
		params = ''
		for i in payload:
			params += '&' + i + '=' + str(payload[i])
		params = params.lstrip('&').encode('utf-8')

		return hmac.new(self.secret, params, digestmod=hashlib.sha256).hexdigest()

	def ping(self):
		return self.public_request('GET', 'ping')

	def current_time(self):
		return int(time.time() - 1) * 1000

	def time(self):
		return self.public_request('GET', 'time')

	def klines(self, symbol, interval, start_time = None, end_time = None, limit = 10):
		payload = {
			'symbol'     : symbol,
			'interval'   : interval,
			'limit'      : limit,
			'startTime'  : start_time,
			'endTime'	 : end_time
		}
		return self.public_request('GET', 'klines', **payload)

	def price(self, symbol):
		payload = {
			'symbol' : symbol
		}
		return self.public_request('GET', 'ticker/price', **payload)

	def all_orders(self, symbol):
		payload = {
			'symbol' : symbol
		}
		return self.private_request('GET', 'allOrders', **payload)

	def account(self):
		return self.private_request('GET', 'account')

	def my_trades(self, symbol):
		payload = {
			'symbol' : symbol
		}
		return self.private_request('GET', 'allOrders', **payload)
