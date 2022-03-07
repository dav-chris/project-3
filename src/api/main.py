# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Import
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Standard
import sys

# Custom
from api import api



# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Classes
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class App():

   def __init__(self, api):
      self.api = api


   def run(self, **srvOpts):
      self.api.run(
         **srvOpts
      )


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Functions
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def main(argv):

   # # Instanciate the application
   app = App(api)

   # Récupérer le settings

   # # Start the api server
   srvOpts = {
         'host'         : '0.0.0.0'
      ,  'port'         : 5000
      ,  'debug'        : None
      ,  'load_dotenv'  : False
      ,  'use_reloader' : True
   }
   app.run(**srvOpts)





########################################################################################################################
#
# MAIN PROGRAME starts here...
#
########################################################################################################################

if __name__ == '__main__':
   main(sys.argv)