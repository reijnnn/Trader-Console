from datetime import datetime


class CheckFunctions:

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
            'WAVESUSDT',
            'XMRUSDT',
            'DASHUSDT'
        ]

    @staticmethod
    def check_interval(interval):
        return interval in ['1m', '5m', '1h', '2h', '4h', '8h', '12h', '1d', '1w', '1M']

    @staticmethod
    def check_condition(condition):
        return condition in ['>', '<']

    @staticmethod
    def check_calc_period(period):
        try:
            period = int(period)
            if 0 < period < 1000:
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
            if 0.1 <= percentage <= 100:
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
    def check_comma_separated_ints(ints):
        for val in ints.split(','):
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

            year = int(date[0:4])
            month = int(date[4:6])
            day = int(date[6:8])

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
