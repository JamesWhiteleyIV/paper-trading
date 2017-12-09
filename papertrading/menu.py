import sys
import os.path
import re

class Menu():
   ''' main menu functionality to call Portfolio class '''

   def __init__(self):
      self.cur_port = None
      self.DIR = os.path.join(os.path.dirname(__file__), 'portfolios')

      pkl_files = [name for name in os.listdir(self.DIR) 
            if name.endswith('.pkl') and os.path.isfile(os.path.join(self.DIR, name))]

      if len(pkl_files) < 1:
         #no portfolios exist, create new 
         self._create_portfolio()
      elif len(pkl_files) == 1:
         self.cur_port = [name for name in os.listdir(self.DIR) if name.endswith('.pkl')][0] # only one .pkl file
         print self.cur_port
      else: #multiple pickle files ask which to use
         self._switch_portfolio()


      self.options = {
         '0': self._exit,
         '1': self._create_portfolio,
         '2': self._switch_portfolio,
         '3': self._buy_stock,
         '4': self._sell_stock,
         '5': self._rm_stock
      }

   def _valid_filename(self, filename):
      ''' validates that a file name is alphanumeric '''
      if re.match("^[A-Za-z0-9_-]*$", filename):
         return True
      else:
         return False

      
   def _exit(self):
      ''' Exits program '''
      print 'Goodbye!'
      sys.exit(1)

   def _create_portfolio(self):
      ''' Create a new portfolio as .pkl file '''
      print 'create portfolio'

   def _switch_portfolio(self):
      ''' Change current portfolio self.cur_port '''
      # for pkl files in portfolios/
      # create dict, show choices then switch based on option
      print 'switch portfolio'
      print 'Which portfolio would you like to use?'

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
   menu = Menu()
   menu.start()
