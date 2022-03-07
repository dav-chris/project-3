# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Import
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Standard
import json
import os

# 3rd Party
from pymongo import MongoClient

# Custom
import params


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Classes
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class MongoSettings:

   def __init__(self
      ,  host       = 'project3-mongo-server'
      ,  port       = '27017'
      ,  username   = 'admin'
      ,  password   = 'admin'
      ,  authSource = 'admin'
      ,  database   = 'football'
      ,  collection = 'users'
   ):
      self.data = {
            'server': {
                  'host': host
               ,  'port': port
            }
         ,  'cnx': {
                  'username': username
               ,  'password': password
               ,  'authSource': authSource
            }
         ,  'schema': {
                  'database': database
               ,  'collection': collection
            }
      }


   def _updateField(self, fieldName, otherSettings):

      if isinstance(otherSettings, dict):
         settings = self.data.get(fieldName)
         for key in settings.keys():
            if key in otherSettings:
               settings[key] = otherSettings[key]


   def update(self, dictSettings):

      for fieldName in self.data.keys():
         self._updateField(fieldName, dictSettings.get(fieldName))


   def updateFromEnv(self):

      # Field: "server"
      for envVarName, fieldName in ( ('MONGO_HOST', 'host'), ('MONGO_PORT', 'port') ):
         if envVarName in os.environ:
            self.data['server'][fieldName] = os.environ[envVarName]

      # Field "cnx"
      for envVarName, fieldName in ( ('MONGO_USER', 'username'), ('MONGO_PWD', 'password'), ('MONGO_AUTHENT_DB', 'authSource')):
         if envVarName in os.environ:
            self.data['cnx'][fieldName] = os.environ[envVarName]

      # Field "schema"
      for envVarName, fieldName in ( ('MONGO_DATABASE', 'database'), ('MONGO_COLLECTION', 'collection')):
         if envVarName in os.environ:
            self.data['schema'][fieldName] = os.environ[envVarName]


   def getServerOpts(self):
      return self.data.get('server')


   def getCnxOpts(self):
      return self.data.get('cnx')


   def getSchemaOpts(self):
      return self.data.get('schema')


   def get(self):
      return self.data




# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Functions
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def getMongoSettings(confFilepath = params.SETTINGS_FILEPATH):

   # Retrieving default settings
   settings = MongoSettings()

   # Loading settings from conf file
   with open(confFilepath, 'r') as jsonFile:
      conf = json.load(jsonFile)

   # Settings from conf file takes precedence over default settings
   settings.update(conf)

   # Settings from environment variables takes precedences over conf file settings
   settings.updateFromEnv()

   return settings



def MongoEngine(settings: MongoSettings):

   serverOpts, cnxOpts = settings.getServerOpts(), settings.getCnxOpts()

   driver = MongoClient(
         host       = serverOpts.get('host')
      ,  port       = int(serverOpts.get('port'))
      ,  username   = cnxOpts.get('username')
      ,  password   = cnxOpts.get('password')
      ,  authSource = cnxOpts.get('authSource')
   )

   return driver




