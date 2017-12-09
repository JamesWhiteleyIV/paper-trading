import sys
import os.path
import re

class Paper_Trading():
   ''' main menu functionality to call Portfolio class '''

   def __init__(self):
      ''' init a portfolio and set the current portfolio '''
      self.cur_port = None
      self.DIR = os.path.join(os.path.dirname(__file__), 'portfolios')

      #get list of portfolio names if they exist
      pkl_files = self._get_all_pkl_files()
      if len(pkl_files) < 1: #no portfolios exist, create new and set current portfolio
         self._create_portfolio()
      elif len(pkl_files) == 1: #only one portfolio, auto load it
         self._set_portfolio([name for name in os.listdir(self.DIR) if name.endswith('.pkl')][0]) # only one .pkl file
      else: #multiple portfolio's, ask which to use
         self._switch_portfolio()

      self.options = {
         '0': self._exit,
         '1': self._create_portfolio,
         '2': self._switch_portfolio,
         '3': self._buy_stock,
         '4': self._sell_stock,
         '5': self._rm_stock
      }

   def _get_all_pkl_files(self):
      ''' returns list of all .pkl files in portfolio directory ''' 
      return [name for name in os.listdir(self.DIR)
         if name.endswith('.pkl') and os.path.isfile(os.path.join(self.DIR, name))]

   def _valid_filename(self, filename):
      ''' validates that a file name is alphanumeric '''
      if re.match("^[A-Za-z0-9]*$", filename):
         return True
      else:
         return False

   def _exit(self):
      ''' Exits program '''
      print 'Goodbye!'
      sys.exit(0)

   def _set_portfolio(self, portfolio):
      ''' Sets self.cur_port '''
      self.cur_port = portfolio
      print 'Using portfolio: ', self.cur_port

   def _create_portfolio(self):
      ''' Create a new portfolio as .pkl file '''
      print 'What would you like to name new portfolio?'
      name = raw_input('> ')
      while not self._valid_filename(name): 
         print "Invalid name, name must only have letters and numbers."
         print 'What would you like to name your portfolio?'
         name = raw_input('> ')
      self._set_portfolio(name + '.pkl')
         
   def _switch_portfolio(self):
      ''' Change current portfolio self.cur_port '''
      # for pkl files in portfolios/
      # create dict, show choices then switch based on option
      print 'Which portfolio would you like to use?'
      pkl_files = self._get_all_pkl_files()
      options = {}
      i = 1
      for f in pkl_files:
         options[str(i)] = f
         i += 1
      for key in options:
         print key, '-', options[key]
      choice = raw_input('> ')
      while choice not in options:
         print 'Invalid option.'
         choice = raw_input('> ')
      self._set_portfolio(options[choice])
      
      
   def _buy_stock(self):
      ''' add a new stock to portfolio '''
      print 'buy stock'

   def _sell_stock(self):
      ''' sell a stock from portfolio '''
      # if # investments in portfolio < 1, return
      print 'sell stock'

   def _rm_stock(self):
      ''' remove a stock from portfolio completely '''
      # if # investments in portfolio < 1, return
      print 'rm stock'

   def _select_option(self, option):
      ''' call a function from dict '''
      try:
         self.options[option]()
      except SystemExit as e:
         pass
      except:
         print 'invalid option'
      
   def start(self):
      ''' displays menu '''
      choice = None
      while (choice != '0'):
         print '---------------------------'
         print 'Enter a number:'
         print '0 - Exit'
         print '1 - Create new portfolio'
         print '2 - Switch portfolio'
         print '3 - Buy stock'
         print '4 - Sell stock'
         print '5 - Remove stock'
         choice = raw_input('> ')
         self._select_option(choice)



if __name__ == '__main__':
   pt = Paper_Trading()
   pt.start()
