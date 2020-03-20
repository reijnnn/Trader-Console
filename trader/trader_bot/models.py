from ..extensions import db

class Binance_klines(db.Model):
   __tablename__ = 'binance_klines'

   symbol     = db.Column(db.String,  nullable=False, primary_key=True)
   interval   = db.Column(db.String,  nullable=False, primary_key=True)
   open_time  = db.Column(db.Integer, nullable=False, primary_key=True)
   open       = db.Column(db.String)
   high       = db.Column(db.String)
   low        = db.Column(db.String)
   close      = db.Column(db.String)
   volume     = db.Column(db.String)
   num_trades = db.Column(db.Integer)

   def __repr__(self):
      return "<Kline(symbol='%s', interval='%s', open_time='%s', open='%s', high='%s', low='%s', close='%s')>" % (
                self.symbol, self.interval, self.open_time, self.open, self.high, self.low, self.close)
