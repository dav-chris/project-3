# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Import
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Standard
import csv
import json
import os
import sys

# 3rd Party
from pymongo import MongoClient
from pprint import pprint

# Custom
from params import SETTINGS_FILEPATH



# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Classes
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class InvalidSyntaxError(Exception):
   pass


class UserModel():

   @classmethod
   def create(cls, name, transfers = None):

      if name is None:
         raise Exception('ERROR: Invalid value for "name": a non empty string is expected')

      if transfers is None:
         transfers = list()
      else:
         if not isinstance(transfers, list):
            raise Exception('ERROR: Invalid type for field "transfers": a list is expected')

      return {
            'name': name
         ,  'transfers': transfers
      }


   @classmethod
   def mergeTransfers(cls, fromUser, toUser):
      if fromUser.get('name') != toUser.get('name'):
         raise Exception('ERROR !!!')

      data = toUser.copy()

      srcTransfers = fromUser.get('transfers')
      if srcTransfers:
         if data.get('transfers') is None:
            data['transfers'] = srcTransfers
         else:
            data['transfers'].extend(srcTransfers)

      return data


   @classmethod
   def createFromCsvRec(cls, origData):

      #
      # Original Data
      #

      # Retrieving fileds
      name        = origData.get('Name')
      position    = origData.get('Position')
      age         = origData.get('Age')
      leagueFrom  = origData.get('League_from')
      leagueTo    = origData.get('League_to')
      teamFrom    = origData.get('Team_from')
      teamTo      = origData.get('Team_to')
      origSeason  = origData.get('Season')
      marketValue = origData.get('Market_value')
      transferFee = origData.get('Transfer_fee')

      #
      # Transformed Data
      #

      transfers = list()
      transfer  = dict()
      league    = dict()
      team      = dict()
      season    = dict()
      cost      = dict()

      if age is not None:
         transfer['age'] = int(age)
      if position:
         transfer['position'] = str(position)
      # League
      if leagueFrom:
         league['from'] = str(leagueFrom)
      if leagueTo:
         league['to'] = str(leagueTo)
      if league:
         transfer['league'] = league
      # Team
      if teamFrom:
         team['from'] = str(teamFrom)
      if teamTo:
         team['to'] = str(teamTo)
      if team:
         transfer['team'] = team
      # Season
      if origSeason:
         fields = str(origSeason).split(sep = '-')
         if len(fields) == 2:
            season['begYear'] = int(fields[0])
            season['endYear'] = int(fields[1])
            transfer['season'] = season
      # Cost
      if marketValue:
         try:
            value = float(marketValue)
         except:
            value = None
         finally:
            if value:
               cost['estimation'] = value
      if transferFee:
         try:
            value = float(transferFee)
         except:
            value = None
         finally:
            if value:
               cost['real'] = value
      if cost:
         transfer['cost'] = cost

      transfers.append(transfer)

      return UserModel.create(name, transfers = transfers)




class App():

   def __init__(self):

      # Load settings
      self.settings = self.loadSettings(SETTINGS_FILEPATH)

      # Instanciate a mongo driver
      self.mongo = self.mongoDriver()



   def loadSettings(self, filepath):

      with open(filepath, 'r') as jsonFile:
         return json.load(jsonFile)


   def getSettings(self):
      return self.settings


   def mongoDriver(self):

      settings = self.settings.get('mongo')
      if settings is None:
         raise Exception('ERROR: Failed to retrieve field "mongo" from settings')
      server = settings.get('server')
      cnx    = settings.get('cnx')
      if server is None:
         raise Exception('ERROR: Failed to retrieve field "mongo.server" from settings')
      if cnx is None:
         raise Exception('ERROR: Failed to retrieve field "mongo.cnx" from settings')
      mongo = MongoClient(
            host       = server.get('host')
         ,  port       = int(server.get('port'))
         ,  username   = cnx.get('username')
         ,  password   = cnx.get('password')
         ,  authSource = cnx.get('authSource')
      )
      return mongo



   def loadData(self, csvFilepath):

      def upsert(user, collection):

         name = user.get('name')
         if name:
            # If this user does not already exists in the collection, create it now
            if collection.get(name) is None:
               collection[name] = user
            # The user already exists in the collection: we merge the transfers
            else:
               collection[name] = UserModel.mergeTransfers(user, collection[name])


      # Retrieving settings for the load
      loadSettings   = self.settings.get('load')
      dbName         = loadSettings.get('target_db')
      collectionName = loadSettings.get('target_collection')
      drop           = loadSettings.get('drop')

      if dbName is None:
         raise Exception('ERROR: Failed to retrieve field "load.target_db" from settings')
      if collectionName is None:
         raise Exception('ERROR: Failed to retrieve field "load.target_collection" from settings')
      if drop is None:
         raise Exception('ERROR: Failed to retrieve field "load.drop" from settings')
      drop = str(drop).lower()
      if drop not in ['true', 'false']:
         raise Exception('ERROR: Invalid value for field "load.drop" from settings: expected value: "true" or "false"')

      print(f'Loading data from file: "{csvFilepath}" ...')

      # Initializing the document that will be created inside Mongo
      # Within this document:
      #   - then key will be the user's name
      #   - the value will be the user's transfers
      users = dict()

      with open(csvFilepath) as csvFile:
         reader = csv.DictReader(csvFile)
         line = 0
         for row in reader:
            if line == 0:
               pass
            user = UserModel.createFromCsvRec(row)
            upsert(user, users)
            line += 1
      print(f'   Processed {line} line(s)')

      db = self.mongo.get_database(dbName)

      # The collection alreday exists ?
      if db.list_collection_names(filter = {'name': collectionName}):
         if drop:
            print('Dropping collection: ', collectionName)
            db.drop_collection(collectionName)
            print('OK.')
         else:
            raise Exception(f'ERROR: collection already exists: "{collectionName}"')

      # Creating the target collection
      collection = db.create_collection(name = collectionName)

      # Populating the collection
      res = collection.insert_many(
            documents = list(users.values())
         ,  ordered   = True
      )

      if res:
         pprint(
            {     'acknowledged': res.acknowledged
               ,  'insertions'  : len(res.inserted_ids)
            }
         )





# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Functions
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def getSettings(argv, app):

   # Retrieving main program arguments
   if len(argv) != 2:
      raise InvalidSyntaxError()

   settings = app.getSettings()

   csvInputFilepath = argv[1]
   if not os.path.isfile(csvInputFilepath):
      raise FileNotFoundError(f'ERROR: file not found: "{csvInputFilepath}"')
   else:
      settings['csvInputFilepath'] = csvInputFilepath

   if 'MONGO_HOST' in os.environ.keys():
      settings['mongo']['server']['host'] = os.environ['MONGO_HOST']

   if 'MONGO_PORT' in os.environ.keys():
      settings['mongo']['server']['port'] = os.environ['MONGO_PORT']

   if 'MONGO_USER' in os.environ.keys():
      settings['mongo']['cnx']['username'] = os.environ['MONGO_USER']

   if 'MONGO_PWD' in os.environ.keys():
      settings['mongo']['cnx']['password'] = os.environ['MONGO_PWD']

   if 'MONGO_AUTHENT_DB' in os.environ.keys():
      settings['mongo']['cnx']['authSource'] = os.environ['MONGO_AUTHENT_DB']

   if 'TARGET_DATABASE' in os.environ.keys():
      settings['load']['target_db'] = os.environ['TARGET_DATABASE']

   if 'TARGET_COLLECTION' in os.environ.keys():
      settings['load']['target_collection'] = os.environ['TARGET_COLLECTION']

   return settings





def main(argv):

   print("coucou")
   
   # Instanciate App
   app = App()

   try:
      settings = getSettings(argv, app)

   except InvalidSyntaxError:
      print('ERROR: Invalid syntax', file = sys.stderr)
      print(f'USAGE:\n   {argv[0]} <input_csv_filepath>', file = sys.stderr)
      exit(1)

   except Exception as err:
      print('ERROR: the following exception occurred:')
      print(str(err))
      exit(1)

   csvInputFilepath = settings.get('csvInputFilepath')



   # Load the csv file input MongoDB
   try:
      app.loadData(csvInputFilepath)
   except:
      print("load non executé")

   

########################################################################################################################
#
# MAIN PROGRAM starts here...
#
########################################################################################################################

if __name__ == '__main__':
   main(sys.argv)
