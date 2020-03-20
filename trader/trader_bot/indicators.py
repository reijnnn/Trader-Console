import numpy as np

def fill_for_noncomputable_vals(input_data, result_data):
   non_computable_values = np.repeat(
      np.nan, len(input_data) - len(result_data)
   )
   filled_result_data = np.append(non_computable_values, result_data)
   return filled_result_data

def check_for_period_error(data, period):
   """
   Check for Period Error.
   This method checks if the developer is trying to enter a period that is
   larger than the data set being entered. If that is the case an exception is
   raised with a custom message that informs the developer that their period
   is greater than the data set.
   """
   period = int(period)
   data_len = len(data)
   if data_len < period:
      raise Exception("Error: data_len < period")

def simple_moving_average(data, period):
   """
   Simple Moving Average.
   Formula:
   SUM(data / N)
   """
   check_for_period_error(data, period)

   sma = [np.mean(data[idx-(period-1):idx+1]) for idx in range(0, len(data))]
   sma = fill_for_noncomputable_vals(data, sma)
   return sma

def moving_average_envelope(data, period, env_percentage):
   """
   Center Band.
   Formula:
   SMA(data)
   """
   cb = simple_moving_average(data, period)

   """
   Upper Band.
   Formula:
   ub = cb(t) * (1 + env_percentage)
   """
   ub = [val * (1 + float(env_percentage)) for val in cb]

   """
   Lower Band.
   Formula:
   lb = cb * (1 - env_percentage)
   """
   lb = [val * (1 - float(env_percentage)) for val in cb]

   return lb, cb, ub

def stochastic(data, period):
   """
   %K.
   Formula:
   %k = data(t) - low(n) / (high(n) - low(n))
   """
   check_for_period_error(data, period)

   percent_k = [((data[idx] - np.min(data[idx+1-period:idx+1])) /
                 (np.max(data[idx+1-period:idx+1]) -
                  np.min(data[idx+1-period:idx+1]))) for idx in range(period-1, len(data))]
   percent_k = fill_for_noncomputable_vals(data, percent_k)

   """
   %D.
   Formula:
   %D = SMA(%K, 3)
   """
   percent_d = simple_moving_average(percent_k, 3)

   return percent_k, percent_d

def relative_strength_index(data, period):
   """
   Relative Strength Index.
   Formula:
   RSI = 100 - (100 / 1 + (prevGain/prevLoss))
   """
   check_for_period_error(data, period)

   period = int(period)
   changes = [data_tup[1] - data_tup[0] for data_tup in zip(data[::1], data[1::1])]

   filtered_gain = [val < 0 for val in changes]
   gains = [0 if filtered_gain[idx] is True else changes[idx] for idx in range(0, len(filtered_gain))]

   filtered_loss = [val > 0 for val in changes]
   losses = [0 if filtered_loss[idx] is True else abs(changes[idx]) for idx in range(0, len(filtered_loss))]

   avg_gain = np.mean(gains[:period])
   avg_loss = np.mean(losses[:period])

   rsi = []
   if avg_loss == 0:
      rsi.append(100)
   else:
      rs = avg_gain / avg_loss
      rsi.append(100 - (100 / (1 + rs)))

   for idx in range(1, len(data) - period):
      avg_gain = ((avg_gain * (period - 1) +
               gains[idx + (period - 1)]) / period)
      avg_loss = ((avg_loss * (period - 1) +
               losses[idx + (period - 1)]) / period)

      if avg_loss == 0:
         rsi.append(100)
      else:
         rs = avg_gain / avg_loss
         rsi.append(100 - (100 / (1 + rs)))

   rsi = fill_for_noncomputable_vals(data, rsi)

   return rsi

def stochrsi(data, period):
   """
   StochRSI.
   Formula:
   SRSI = ((RSIt - RSI LOW) / (RSI HIGH - LOW RSI)) * 100
   """
   rsi = relative_strength_index(data, period)[period:]
   stochrsi = [100 * ((rsi[idx] - np.min(rsi[idx+1-period:idx+1])) / (np.max(rsi[idx+1-period:idx+1]) - np.min(rsi[idx+1-period:idx+1]))) for idx in range(period-1, len(rsi))]
   stochrsi = fill_for_noncomputable_vals(data, stochrsi)
   return stochrsi
