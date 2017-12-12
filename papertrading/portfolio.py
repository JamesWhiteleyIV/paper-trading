import pandas_datareader.data as web
import pandas as pd
import datetime as dt
from dateutil.relativedelta import relativedelta
import pickle
import numpy as np
import os
from tabulate import tabulate
import time
from colors import colors

class Stock():
   def __init__(self, ticker, shares):
        buy_price = self._get_buy_price(ticker)
        self.data = {
                "id": None,
                "ticker": ticker,
                "shares": shares,
                "is_sold": False,    #update
                "sell_price": None,  #update
                "sell_date": None,   #update
                "total_gain": 0.0,     #update
                "cur_price": buy_price, #update 
                "cur_value": buy_price * shares, #update 
                "buy_price": buy_price,
                "start_value": buy_price * shares,
                "buy_date": dt.date.today(),
                "price_target": None,
                "price_target_set_date": None,
                "stop_loss": None,
                "stop_loss_set_date": None,
                }

   def _get_buy_price(self, ticker):       
      ''' returns buy price for stock, will get last available price if market not open '''
      buy_date = dt.date.today()
      start = buy_date - relativedelta(days=10)
      prices = web.DataReader(ticker, "yahoo", start, buy_date)
      return prices.ix[-1, 'Adj Close']


   def set_sl(self, sl):
      if sl <  self.data['cur_price']:
         self.data['stop_loss'] = sl 
         self.data['stop_loss_set_date'] = dt.date.today() 
         print colors.green + self.data['ticker'], 'stop loss updated successfully' + colors.end
      else:
         print colors.red + "Stop loss must be lower than current price" + colors.end


   def set_pt(self, pt):
      if pt > self.data['cur_price']:
         self.data['price_target'] = pt
         self.data['price_target_set_date'] = dt.date.today() 
         print colors.green + self.data['ticker'], 'price target updated successfully' + colors.end
      else:
         print colors.red + "Price target must be higher than current price" + colors.end

   def sell(self):
        '''sells stock on current date, uses most recent  adj close price'''
        try:
           end = dt.date.today()
           start = end - relativedelta(days=10)
           ticker = self.data["ticker"]
           prices = web.DataReader(ticker, "yahoo", start, end)
           sell_price = prices.ix[-1, 'Adj Close']
           self.data['cur_price'] = sell_price
           self.data['is_sold'] = True
           self.data['sell_date'] = end 
           self.data['sell_price'] = sell_price 
           self.data['cur_value'] = sell_price * self.data['shares']
           self.data['total_gain'] = (sell_price / self.data['buy_price'] - 1) * 100.0
        except Exception as e:
           pass


   def update(self):
      ''' updates cur_price, cur_value, and total_gain '''
      try:
           #checks if price target or stop loss have been hit
           self._check_sell()
           if not self.data['is_sold']: #stop loss and price target not hit
              end = dt.date.today()
              start = end - relativedelta(days=10)
              ticker = self.data["ticker"]
              prices = web.DataReader(ticker, "yahoo", start, end)
              cur_price = prices.ix[-1, 'Adj Close']
              self.data['cur_price'] = cur_price
              self.data['cur_value'] = cur_price * self.data['shares']
              self.data['total_gain'] = (cur_price / self.data['buy_price'] - 1) * 100.0
      except Exception as e:
           pass


   def _check_sell(self):
      ''' checks if price target or stop loss has been hit since it was set '''
      pt = self.data['price_target']
      sl = self.data['stop_loss']
      if not pt and not sl:
         return #no price target or stop loss set, don't check sell
      pt_date = None 
      sl_date = None 
      try:
         prices = web.DataReader(self.data['ticker'], "yahoo", self.data['buy_date'], dt.date.today())
      except: #not enough data to calculate
         print 'invalid date range'
         return
      if pt and dt.date.today() > self.data['price_target_set_date']:  #get all dates where pt was hit since pt was set , must have at least one holding day 
         try:
            pt_set_date = self.data['price_target_set_date'] 
            idx = prices.index.get_loc(pt_set_date)
            pt_dates = prices.ix[idx+1:]
            pt_dates = pt_dates[pt_dates['High'] > pt]
            pt_date = pt_dates.index[0]
         except Exception as e:
            pass
      if sl and dt.date.today() > self.data['stop_loss_set_date']:  #get all dates where sl was hit since sl was set  
         try:
            sl_set_date = self.data['stop_loss_set_date'] 
            idx = prices.index.get_loc(sl_set_date)
            sl_dates = prices.ix[idx+1:]
            sl_dates = sl_dates[sl_dates['Low'] < sl]
            sl_date = sl_dates.index[0]
         except Exception as e:
            pass       
         
      sold_date = None
      sell_price = None
      if pt_date and sl_date: #if both pt and sl have hit
         if pt_date > sl_date: # sl hit first
             sold_date = sl_date
             sell_price = sl 
             open_price = prices.ix[sold_date, 'Open']
             if sell_price > open_price: #if it opens lower than SL
               sell_price = open_price
         else:
             sold_date = pt_date
             sell_price = pt 
             open_price = prices.ix[sold_date, 'Open']
             if sell_price < open_price: #if it opens higher than PT
               sell_price = open_price
      elif pt_date:  #only pt
         sold_date = pt_date
         sell_price = pt 
         open_price = prices.ix[sold_date, 'Open']
         if sell_price < open_price: #if it opens higher than PT
           sell_price = open_price
      elif sl_date: #only sl
         sold_date = sl_date
         sell_price = sl 
         open_price = prices.ix[sold_date, 'Open']
         if sell_price > open_price:
               sell_price = open_price

      if sold_date:
         self.data["is_sold"] = True
         self.data["sell_price"] = sell_price
         self.data['sell_date'] = sold_date.date()
         self.data["total_gain"] = (sell_price / self.data["buy_price"] - 1) * 100.0
         self.data["cur_price"] = sell_price
         self.data["cur_value"] = sell_price * self.data['shares']



      


        



class Portfolio():
   def __init__(self, filename):
        
        self.last_update = None
        self.filename = filename
        self.data = {
            'next_id': 1,
            'start_value': None,
            'cur_value': None,
            'cash': None,
            'stocks': [], 
        }


        #create pkl file if doesn't exist
        #else: open the pkl file and store in self.data
        if not os.path.isfile(self.filename):
            self.data['cur_value'] = self._get_start_value()  #set start value of portfolio if new portfolio
            self.data['cash'] = self.data['cur_value']
            self.data['start_value'] = self.data['cur_value']
            self._save_port()
        else:
            with open(self.filename, 'r') as infile:
                try:
                  self.data = pickle.load(infile)
                except Exception as e:
                  print e


   def _get_start_value(self):
      ''' sets start value of portfolio, validates numeric input '''
      while(1):
         try:
            print "What would you like the starting value of your portfolio to be?"
            value  = float(raw_input('> '))
         except ValueError:
            print colors.red + "You must enter a numeric value." + colors.end
         else:
            return value
        

   def _save_port(self):
      ''' dumps self.data into .pkl file '''
      with open(self.filename, 'w') as outfile:
         pickle.dump(self.data, outfile)

   def buy_stock(self):
      ''' adds stock to portfolio current date '''
      day_of_week = dt.date.today().weekday()
      cur_time = dt.datetime.now().time()
      if day_of_week >= 5: # 5 and 6 == sat and sun, market closed
         print colors.red + "Market Closed" + colors.end
      elif cur_time <= dt.time(6, 30) or cur_time >= dt.time(13,00):
         print colors.red + "Market Closed" + colors.end
      else:
         success = None
         while not success:
            try:
               ticker = str(raw_input('Enter Ticker: '))
               shares = int(raw_input('Enter # Shares: '))
            except ValueError:
               print "Invalid input."
            else:
               ticker = ticker.upper()
               new_stock = Stock(ticker, shares)
               new_stock.data['id'] = self.data['next_id']
               if self.data['cash'] < new_stock.data['cur_value']: #not enough money in portfolio
                  print colors.red + "Not enough cash to buy stock." + colors.end
               else:
                  self.data['next_id'] += 1
                  self.data['cash'] -= new_stock.data['cur_value'] 
                  self.data['stocks'].append(new_stock)
                  self._save_port()
                  print colors.green + ticker + " added to portfolio successfully" + colors.end
               self.last_update = None
               success = True
           

   def sell_stock(self):
      ''' sells stock from portfolio on current date '''
      day_of_week = dt.date.today().weekday()
      cur_time = dt.datetime.now().time()
      if day_of_week >= 5: # 5 and 6 == sat and sun, market closed
         print colors.red + "Market Closed" + colors.end
      elif cur_time <= dt.time(6, 30) or cur_time >= dt.time(13,00):
         print colors.red + "Market Closed" + colors.end
      elif len(self.data['stocks']) < 1:
         print colors.red + "No stocks to sell" + colors.end
      else:
         self.show_portfolio()
         print "Enter stock ID to sell"
         try:
            choice = int(raw_input('> '))
         except ValueError:
            print colors.red + "Invalid input." + colors.end
         else:
            for stock in self.data['stocks']:
               if stock.data['id'] == choice and not stock.data['is_sold']:
                  stock.sell()
                  self.data['cash'] += stock.data['cur_value']
                  self._save_port()
                  print colors.green + stock.data['ticker'] +  " sold from portfolio successfully" + colors.end
                  return
           

   def show_portfolio(self):
      ''' displays stock holdings '''
      if len(self.data['stocks']) < 1:
         print colors.red +  "No stocks in portfolio" + colors.end
      else:
         if not self.last_update:
            self.update() #this will update cur_value of portfolio
         elif time.time() - self.last_update > 60: #only update at most once every minute
            self.update()
         tab_data = []
         for stock in self.data['stocks']:
            if not stock.data['is_sold']:
               tab_data.append([
                  stock.data['id'], stock.data['ticker'], stock.data['buy_date'], stock.data['buy_price'], stock.data['cur_price'],                   stock.data['price_target'], stock.data['stop_loss'], 
                  stock.data['shares'], stock.data['start_value'],  stock.data['cur_value'], stock.data['total_gain'],   
                  ])
         print 'Current Holdings'
         print tabulate(tab_data,  headers=['ID', 'Ticker', 'Buy Date', 'Buy Price', 'Cur Price', 'Price Target', 'Stop Loss', 'Shares', 'Start Value', 'Cur Value', 'Total Gain %'], tablefmt="fancy_grid", floatfmt=(".2f"))
         tabs = [ 
            ['Total Portfolio Value: $', self.data['cur_value']], ['Available Cash: $', self.data['cash']], ['Total Portfolio Gain:', (self.data['cur_value'] / self.data['start_value'] - 1.0) * 100.0  ]]
         print tabulate(tabs, tablefmt="fancy_grid", floatfmt=(".2f"))


   def show_past_trades(self):
      ''' displays past holdings '''
      if len(self.data['stocks']) < 1:
         print colors.red + "No stocks in portfolio" + colors.end
      else:
         tab_data = []
         for stock in self.data['stocks']:
            if stock.data['is_sold']:
               tab_data.append([
                  stock.data['id'], stock.data['ticker'], stock.data['buy_date'],  stock.data['sell_date'], stock.data['buy_price'], stock.data['sell_price'],                   
                  stock.data['shares'], stock.data['start_value'],  stock.data['cur_value'], stock.data['total_gain'],   
                  ])
         print 'Past Trades'
         print tabulate(tab_data,  headers=['ID', 'Ticker', 'Buy Date', 'Sell Date', 'Buy Price', 'Sell Price', 'Shares', 'Start Value', 'End Value', 'Total Gain %'], tablefmt="fancy_grid", floatfmt=(".2f"))


   def update(self):
      '''iterate through each stock, update current value if not sold '''
      print "Updating portfolio..."
      self.data['cur_value'] = 0
      for stock in self.data["stocks"]:
         if not stock.data["is_sold"]:
            stock.update()
            if stock.data["is_sold"]: #price target or stop loss hit during update
               self.data['cash'] += stock.data['cur_value']
               print colors.green + stock.data['ticker'] +  " sold from portfolio successfully" + colors.end
            else:
               self.data['cur_value'] += stock.data['cur_value']
      self.data['cur_value'] += self.data['cash']
      self.last_update = time.time()
      self._save_port()


   def add_price_target(self):
      ''' update a stock's price target '''
      if len(self.data['stocks']) < 1:
         print colors.red + "No stocks in portfolio" + colors.end
      else: 
         self.show_portfolio()
         print "Enter stock ID to add price target"
         try:
            choice = int(raw_input('> '))
            pt = float(raw_input('Price Target: '))
         except ValueError:
            print colors.red + "Invalid input." + colors.end
         else:
            for stock in self.data['stocks']:
               if stock.data['id'] == choice and not stock.data['is_sold']:
                  stock.set_pt(pt)
                  self._save_port()
                  return
          

   def add_stop_loss(self):
      ''' update a stock's stop loss '''
      if len(self.data['stocks']) < 1:
         print colors.red + "No stocks in portfolio" + colors.end
      else:
         self.show_portfolio()
         print "Enter stock ID to add stop loss"
         try:
            choice = int(raw_input('> '))
            sl = float(raw_input('Stop Loss: '))
         except ValueError:
            print colors.red + "Invalid input." + colors.end
         else:
            for stock in self.data['stocks']:
               if stock.data['id'] == choice and not stock.data['is_sold']:
                  stock.set_sl(sl)
                  self._save_port()
                  return
      



