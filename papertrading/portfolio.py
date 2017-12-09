import pandas_datareader.data as web
import pandas as pd
import datetime as dt
from dateutil.relativedelta import relativedelta
import pickle
import numpy as np
import os

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class Stock():
   def __init__(self, ticker, shares):
        buy_price = self._get_buy_price(ticker)
        self.data = {
                "ticker": ticker,
                "shares": shares,
                "is_sold": False,    #update
                "sell_price": None,  #update
                "sell_date": None,   #update
                "total_gain": 0.0,     #update
                "cur_price": buy_price, #update 
                "cur_value": buy_price * shares, #update 
                "buy_price": buy_price,
                "buy_date": dt.date.today(),
                "price_target": None,
                "stop_loss": None,
                }


   def _get_buy_price(self, ticker):       
      ''' returns buy price for stock, will get last available price if market not open '''
      buy_date = dt.date.today()
      start = buy_date - relativedelta(days=10)
      prices = web.DataReader(ticker, "yahoo", start, buy_date)
      return prices.ix[-1, 'Adj Close']


   def sell(self):
        '''sells stock on current date, uses close price'''
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
           print e






   """

    def _add_stop_loss(self, prices):
        '''
        NEW SL IMPLEMENTATION
        adds stop loss series to prices df
        '''
        prices['gain'] = (prices['Close'] / self.data['buy_price'] - 1.0) * 100.0 

        prices['sl'] = np.where(prices['gain'] >= 7.0, 0, None) #lowest gain is now buy price 
        prices['sl'] = np.where(prices['gain'] >= self.data['one_std'] * 5.0 * 100.0, self.data['one_std'] * 2.0, prices['sl']) 
        prices['sl'] = np.where(prices['gain'] >= self.data['one_std'] * 6.0 * 100.0, self.data['one_std'] * 4.0, prices['sl']) 
        prices['sl'] = np.where(prices['gain'] >= self.data['one_std'] * 7.0 * 100.0, self.data['one_std'] * 5.0, prices['sl']) 
        prices['sl'] = np.where(prices['gain'] >= self.data['one_std'] * 8.0 * 100.0, self.data['one_std'] * 7.0, prices['sl'])

        prices['sl'] = (1.0 + prices['sl']) * self.data['buy_price']
        prices['sl'] = np.where(prices['gain'] < 7.0, self.data['stop_loss'], prices['sl'])
        prices['sl'] = prices['sl'].expanding(min_periods=1).max() 

        self.data['cur_stop_loss'] = prices.ix[-1, 'sl']
        prices['sl'] = prices['sl'].shift() 
        return prices



    def _add_profit_target(self, prices):
        '''
        NEW PT IMPLEMENTATION
        adds price target series to prices df

        dsb = days since buy:
         first 5 days buy price + 10%
         next 5 days buy price + 15%
         next 5 days buy price + 20%
         everything after 15 days regular price target

        big_gain:
         prev_close + 10%

        org_pt:
         the orginal 9 std sell signal

        pt:
          the min of the three columns to designate price target
        '''
        prices['dsb'] = self.data['buy_price'] * 1.10 
        if len(prices) > 5:
          prices.ix[5:, 'dsb'] = self.data['buy_price'] * 1.15 
        if len(prices) > 10:
          prices.ix[10:, 'dsb'] = self.data['buy_price'] * 1.20 
        if len(prices) > 15:
          prices.ix[15:, 'dsb'] = self.data['price_target'] 
         
        prices['big_gain'] = prices['Close'].shift() * 1.10
        prices['price_target'] = self.data['price_target']

        prices['pt'] =  prices[['dsb','big_gain', 'price_target']].min(axis=1)

        return prices


    def check_sell(self):
        '''updates data based on sell, only works if stock hasn't sold'''
        if self.data["is_sold"]: #no updates if stock is sold
            return

        end = dt.date.today()
        start = self.data["buy_date"]
        ticker = self.data["ticker"]
        self.prices = web.DataReader(ticker, "yahoo", start, end)
        self.prices = self.prices.ix[start:]
        self.data['cur_price'] = self.prices.ix[-1, 'Close']

        #add profit target and stop loss calculations to prices frame
        self.prices = self._add_stop_loss(self.prices)
        self.prices = self._add_profit_target(self.prices)

        '''  PLOTS each stock vs PT and vs SL
        prices['pt'].plot(kind='line', linewidth=0.5, color='Green')
        prices['Open'].plot(kind='line', linewidth=0.5, color='Grey')
        prices['High'].plot(kind='line', linewidth=0.5, color='Blue')
        prices['Close'].plot(kind='line', linewidth=0.5, color='Black')
        plt.title("{}   PT, Open, High, Close".format(ticker))
        plt.tight_layout()
        plt.show()
        plt.close()

        prices['sl'].plot(kind='line', linewidth=0.5, color='Red')
        prices['Open'].plot(kind='line', linewidth=0.5, color='Grey')
        prices['Low'].plot(kind='line', linewidth=0.5, color='Blue')
        prices['Close'].plot(kind='line', linewidth=0.5, color='Black')
        plt.title("{}   SL, Open, Low, Close".format(ticker))
        plt.tight_layout()
        plt.show()
        plt.close()
        ''' #check if price target or stop loss occurred first or neither
        pt = self.prices[self.prices['High'] > self.prices['pt']]
        sl = self.prices[self.prices['Low'] < self.prices['sl']]

        pt_date = None
        sl_date = None
        sold_date = None
        sell_price = None
        if len(pt) > 0:
            pt_date = pt.index[0]
        if len(sl) > 0:
            sl_date = sl.index[0]

        #if both pt and sl have hit
        if pt_date and sl_date:
            if pt_date > sl_date:
                sold_date = sl_date
                sell_price = self.prices.ix[sold_date, 'sl']
                open_price = self.prices.ix[sold_date, 'Open']
                if sell_price > open_price: #if it opens lower than SL
                  sell_price = open_price
            else:
                sold_date = pt_date
                sell_price = self.prices.ix[sold_date, 'pt']
                open_price = self.prices.ix[sold_date, 'Open']
                if sell_price < open_price: #if it opens higher than PT
                  sell_price = open_price
        elif pt_date:  #only pt
            sold_date = pt_date
            sell_price = self.prices.ix[sold_date, 'pt']
            open_price = self.prices.ix[sold_date, 'Open']
            if sell_price < open_price: #if it opens higher than PT
              sell_price = open_price
        elif sl_date: #only sl
            sold_date = sl_date
            sell_price = self.prices.ix[sold_date, 'sl']
            open_price = self.prices.ix[sold_date, 'Open']
            if sell_price > open_price:
               sell_price = open_price

        if sold_date:
            self.data["sell_price"] = sell_price
            self.data['sell_date'] = sold_date.date()
            self.data["is_sold"] = True
            self.data["total_gain"] = (self.data["sell_price"] / self.data["buy_price"] - 1) * 100.0
        else:
            self.data["total_gain"] = (self.prices.ix[-1, 'Close'] / self.data["buy_price"] - 1) * 100.0
   """
       

class Portfolio():
   def __init__(self, filename):
        
        self.filename = filename
        self.data = {
            'start_value': None,
            'cur_value': None,
            'cash': None,
            'stocks': [], 
        }

        '''
        self.data = {
                "next_id": 0,
                "win_pct": None,
                "avg_gain": None,
                "avg_loss": None,
                "avg_ratio": None,
                "avg_dur_win": 0,
                "avg_dur_loss": 0,
                "num_wins": 0,
                "num_loss": 0,
                "num_even": 0,
                }

        '''

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
            print "You must enter a numeric value."
         else:
            return value
        
   def _save_port(self):
      ''' dumps self.data into .pkl file '''
      with open(self.filename, 'w') as outfile:
         pickle.dump(self.data, outfile)

   def buy_stock(self):
      ''' adds stock to portfolio current date '''
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
            if self.data['cash'] < new_stock.data['cur_value']: #not enough money in portfolio
               print "Not enough cash to buy stock."
            else:
               self.data['cash'] -= new_stock.data['cur_value'] 
               self.data['stocks'].append(new_stock)
               self._save_port()
               print ticker, "added to portfolio successfully"
            success = True
           

   def sell_stock(self):
      ''' sells stock from portfolio on current date '''
      if len(self.data['stocks']) < 1:
         print "No stocks to sell"
      else:
         print "Select stock to sell"
         stocks = {}
         i = 1
         for stock in self.data['stocks']:
            if not stock.data['is_sold']:
               stocks[str(i)] = stock
               i += 1
         if len(stocks) > 0:
            for key in stocks:
               print key, '-', stocks[key].data['ticker']
            choice = raw_input('> ')
            while choice not in stocks:
               print 'Invalid option.'
               choice = raw_input('> ')
            stocks[choice].sell()
            self.data['cash'] += stocks[choice].data['cur_value']
            self._save_port()
            print stocks[choice].data['ticker'], "sold from portfolio successfully"
         else:
            print "No stocks to sell"
            

   def show_portfolio(self):
      ''' displays stock holdings '''
      if len(self.data['stocks']) < 1:
         print "No stocks in portfolio"
      else:
         for stock in self.data['stocks']:
            if not stock.data['is_sold']:
               print stock.data['ticker'], stock.data['buy_price'],  stock.data['is_sold']


   def show_past_trades(self):
      ''' displays past holdings '''
      if len(self.data['stocks']) < 1:
         print "No stocks in portfolio"
      else:
         for stock in self.data['stocks']:
            if stock.data['is_sold']:
               print stock.data['ticker'], stock.data['buy_price'], stock.data['is_sold']


   """
    def update(self):
        '''iterate through each stock, if it hasn't sold check it for sell
        update file'''
        win_pct = 0
        num_win = 0
        num_loss = 0
        avg_gain = 0
        avg_loss = 0
        avg_ratio = 0
        sold_stocks = 0 
        non_sold_stocks = 0
        num_days_win = 0
        num_days_loss = 0
        break_even = 0

        for stock in self.data["stocks"]:
            stock.check_sell()
            gain = stock.data["total_gain"]
            if stock.data["is_sold"]:
                sold_stocks += 1.0
                if gain > 1.0:
                    num_days_win += (stock.data['sell_date'] - stock.data['buy_date']).days
                    num_win += 1.0
                    avg_gain += gain
                elif gain < -1.0:
                    num_days_loss += (stock.data['sell_date'] - stock.data['buy_date']).days
                    num_loss += 1.0
                    avg_loss += gain
                else:
                    break_even += 1.0
            else:
                non_sold_stocks += 1.0

        self.data["num_even"] = break_even 
        self.data["num_wins"] = num_win
        self.data["num_loss"] = num_loss

        if num_win > 0:
         self.data['avg_dur_win'] = num_days_win / num_win 
        else:
         self.data['avg_dur_win'] = None 
        if num_loss > 0:
         self.data['avg_dur_loss'] = num_days_loss / num_loss 
        else:
         self.data['avg_dur_loss'] = None 


        if sold_stocks > 0:
            if num_loss == 0:
                self.data["win_pct"] = 100.0
                self.data["avg_loss"] = 0.0 
            else:
                self.data["win_pct"] = (num_win / sold_stocks) * 100.0
                self.data["avg_loss"] = avg_loss / num_loss
            if num_win == 0:
                self.data["avg_gain"] = 0.0 
            else:
                self.data["avg_gain"] = avg_gain / num_win
            if avg_loss == 0:
                self.data["avg_ratio"] = avg_gain 
            else:
                self.data["avg_ratio"] = self.data['avg_gain']/ abs(self.data['avg_loss'])

        #add updates to txt file
        self.save_port()
    
    def simple_stats(self):
      ''' Display gain of all sold stocks + ticker '''
      print "************************************************************"
      s = []
      for stock in self.data["stocks"]:
         if stock.data['is_sold']:
            s.append([stock.data["ticker"],stock.data['total_gain']])
      s = sorted(s, key=lambda x: x[1], reverse=True)
      for stock in s:
         print stock[0], round(stock[1],2), '%'

      print "************************************************************"


    def display_pt_sl(self):
      ''' Display current pt and sl for all currently held stocks + ticker '''
      print "************************************************************"
      for stock in self.data["stocks"]:
         if not stock.data['is_sold']:
            print "----------------------------------------"
            print bcolors.BOLD + stock.data["ticker"] + bcolors.ENDC
            print "Buy Price: ", round(stock.data['buy_price'],2)
            print "Current Price", round(stock.data['cur_price'],2)
            print "Current Gain/Loss:", round(stock.data['total_gain'],2), "%"
            cur_pt = stock.prices.ix[-1, 'pt']
            print bcolors.OKGREEN + "Current Price Target:", str(round(cur_pt,2)) + bcolors.ENDC
            print bcolors.FAIL + "Current Stop Loss:", str(round(stock.data['cur_stop_loss'],2)) + bcolors.ENDC
            print "Change at cur Profit Target", round((cur_pt / stock.data['buy_price'] - 1) * 100.0, 2), "%"
            print "Change at cur Stop Loss", round((stock.data['cur_stop_loss'] / stock.data['buy_price'] - 1) * 100.0, 2), "%"
      print "************************************************************"
     

    def stats(self):
        '''Display stats for portfolio and stocks'''

        print "************************************************************"
        weighted_alpha = 0.0
        num_stocks = 0.0
        total_cash_made = 0.0

        for stock in self.data["stocks"]:
            print "----------------------------------------"
            print "ID:", stock.data['id']
            print stock.data["ticker"]
            print "Buy Date:", stock.data["buy_date"], "Buy Price:", round(stock.data['buy_price'],2) 

            if stock.data['is_sold']:
                print "Sell Date:", stock.data['sell_date'], "Sell Price:", round(stock.data['sell_price'], 2)
                print "Total Change:", round(stock.data['total_gain'],2), "%"
                total_cash_made += (stock.data['total_gain'] * 10.0)
                spy = self.spy['Close']
                start = spy.iloc[spy.index.get_loc(stock.data['buy_date'], method='nearest')]
                #start = self.spy.ix[stock.data['buy_date'], 'Close', method='nearest']
                #end = self.spy.ix[stock.data['sell_date'], 'Close', method='nearest']
                end = spy.iloc[spy.index.get_loc(stock.data['sell_date'], method='nearest')]
                chg = (end / start - 1.0) * 100.0
                alpha = stock.data['total_gain'] - chg
                weighted_alpha += alpha
                num_stocks += 1.0
                print "SPY over same period:", round(chg, 2), "%"

            else:
                print "Current Price", round(stock.data['cur_price'],2)
                print "Current Gain/Loss:", round(stock.data['total_gain'],2), "%"
                print "Main Price Target:", round(stock.data['price_target'],2)
                print "Gain at Price Target", round((stock.data['price_target'] / stock.data['buy_price'] - 1) * 100.0, 2), "%"
                cur_pt = stock.prices.ix[-1, 'pt']
                print "Current Price Target:", round(cur_pt,2)
                print "Current Stop Loss:", round(stock.data['cur_stop_loss'],2)
                print "Change at cur Profit Target", round((cur_pt / stock.data['buy_price'] - 1) * 100.0, 2), "%"
                print "Change at cur Stop Loss", round((stock.data['cur_stop_loss'] / stock.data['buy_price'] - 1) * 100.0, 2), "%"
            
            
        weighted_alpha = round(weighted_alpha / num_stocks,2)
        print "************************************************************"
        print "Win Percentage:", round(self.data["win_pct"],2), "%"
        print "Number of Winning Trades:", int(self.data["num_wins"])
        print "Number of Losing Trades:", int(self.data["num_loss"])
        print "Number of Break Even Trades:", int(self.data["num_even"])
        print bcolors.OKGREEN + "Average Gain Winning Trade: " + str(round(self.data["avg_gain"],2)) + "%" + bcolors.ENDC
        print "Average Days Held Winning Trade:", self.data['avg_dur_win']
        print bcolors.FAIL + "Average Loss Losing Trade: " + str(round(self.data["avg_loss"],2)) + "%" + bcolors.ENDC

        print "Average Days Held Losing Trade:", self.data['avg_dur_loss']
        print bcolors.OKGREEN + "Average Gain / Average Loss Ratio: " + str(round(self.data["avg_ratio"],2)) + bcolors.ENDC
        print "Average Alpha Sold Stocks:", weighted_alpha, "%"
        print ""
        print "Total Cash Made Assuming $1,000 Investment In Each:"
        print "$" + str(round(total_cash_made, 2))
        print "************************************************************"



      """ 

