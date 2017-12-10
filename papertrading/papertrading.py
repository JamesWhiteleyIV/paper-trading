import sys
import os.path
import re
import portfolio as port
from tabulate import tabulate

class Paper_Trading():
   ''' main menu functionality to call Portfolio class '''

   def __init__(self):
      ''' init a portfolio and set the current portfolio '''
      self.DIR = os.path.join(os.path.dirname(__file__), 'portfolios')
      self.cur_port = None  #portfolio filename with .pkl extension
      self.port = None #Portfolio object

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
         '3': self.port.buy_stock,
         '4': self.port.sell_stock,
         '5': self.port.show_portfolio,
         '6': self.port.show_past_trades,
         '7': self.port.add_price_target,
         '8': self.port.add_stop_loss,
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
      ''' Sets self.cur_port and current Portfolio object '''
      self.cur_port = portfolio
      name = self.cur_port.split('.')[0]
      print 'Using portfolio: ', name 
      full_path =  os.path.join(self.DIR, self.cur_port)
      self.port = port.Portfolio(full_path)

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
      pkl_files = self._get_all_pkl_files()
      if len(pkl_files) <= 1:
         print "There is no other portfolio to switch to."
      else:
         print 'Which portfolio would you like to use?'
         options = {}
         i = 1
         for f in pkl_files:
            options[str(i)] = f.split('.')[0]
            i += 1
         for key in options:
            print key, '-', options[key]
         choice = raw_input('> ')
         while choice not in options:
            print 'Invalid option.'
            choice = raw_input('> ')
         self._set_portfolio(options[choice]+'.pkl')

   def _select_option(self, option):
      ''' call a function from dict '''
      try:
         self.options[option]()
      except SystemExit as e:
         pass
      except:
         print 'Invalid option'
      
   def start(self):
      ''' displays menu '''
      choice = None
      while (choice != '0'):
         print tabulate([['0 - Exit'],
            ['1 - Create new portfolio'],
            ['2 - Switch portfolio'],
            ['3 - Buy stock'],
            ['4 - Sell stock'],
            ['5 - Show Portfolio'],
            ['6 - Show Past Trades'],
            ['7 - Add Price Target'],
            ['8 - Add Stop Loss'],
            ], tablefmt="fancy_grid")
         choice = raw_input('> ')
         self._select_option(choice)


if __name__ == '__main__':
   pt = Paper_Trading()
   pt.start()

