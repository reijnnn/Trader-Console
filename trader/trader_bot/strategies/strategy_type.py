class StrategyType:
    ALERT = 'alert'
    PRICE = 'price'
    ENVELOPE = 'envelope'
    VOLUME = 'volume'
    DUMP_PRICE_HISTORY = 'dump_price_history'

    @staticmethod
    def get_strategy_type_list():
        return ['alert', 'dump_price_history', 'envelope', 'price', 'volume']
