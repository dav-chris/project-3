# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Import
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Standard
import json
import os

# 3rd Party
from flask import Flask, make_response
from flask_pydantic import validate
from pydantic import BaseModel
import bson.json_util as json_util
from flask_pymongo import ObjectId

# Custom
from dbDriver import getMongoSettings, MongoEngine



# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Constants
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

APP_NAME = 'project3:db'


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# DB
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

settings = getMongoSettings()

# Instanciating Mongo driver
try:
   mongo = MongoEngine(settings)
except Exception as err:
   raise Exception('ERROR: Failed to instanciate MongoDB driver.\nReason: ', str(err))

schema = settings.getSchemaOpts()
if schema:
   db   = mongo.get_database(schema['database'])
   coll = db.get_collection(schema['collection'])
else:
   raise Exception('ERROR: Failed to retrieve "schema" field from mongo settings')


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# API
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

api = Flask(APP_NAME)


# ~~~ Routes ~~~~~~~

@api.route('/status')
def get_status():
   '''
   DESCRIPTION
      Cette route est une route de test permettant de vérifier la disponibilité de l'API depuis une machine cliente.
      En cas de succès un document JSON est renvoyé avec un champ "status" à "ok".
      Le test effectué par cette route n'inclut pas la base de données. Le test est donc uniquement réalisé sur la
      partie WEB de l'API.
   RETURN
      La fonction renvoie un dictionnaire.
   '''
   return {
         'context': 'formation Data Engineer'
      ,  'api'    : 'project #3: Database'
      ,  'authors': ['Christelle PATTYN', 'David CHARLES-ELIE-NELSON']
      ,  'status' : 'ok'
   }


@api.route('/status/db')
def get_db_test():
   '''
   DESCRIPTION
      Cette route est une route de test permettant de vérifier depuis une machine cliente à la fois:
         - la disponibilité WEB de l'API
         - ainsi que la connexion à la base de données depuis l'API
   RETURN
      La fonction renvoie un dictionnaire:
      - { 'ok': True } : si le test est concluant (la connexion à la base de données est opérationnelle)
      - {   'ok'    : False
          , 'reason': <un message d'erreur correspondant>
        } : s'il y a un souci avec la connexion à la base de données
   '''
   data = None
   try:
      res = db.command("serverStatus")
      if isinstance(res, dict):
         # Keeping only keys: 'uptime' and 'ok'
         # from the dictionary returned by the above mongodb command
         data = { k:res[k] for k in ('uptime', 'ok') if k in res }
         data['ok'] = int(data.get('ok')) == 1
      else:
         raise TypeError(f'ERROR: data received in an invalid type: expected type <dictionary>, got type <{type(res)}>')
   except Exception as err:
      data = {
            'ok': False
         ,  'reason': str(err)
      }
   finally:
      return {
         "data": data
      }


@api.route('/players/count')
def get_players_count():
   '''
   DESCRIPTION
      Cette route renvoie le nombre de joueurs référencés dans la base de données.
   RETURN
      La fonction renvoie un dictionnaire avec
         - key  : 'nb_players'
         - value: le nombre de joueurs référencés dans la base de données
   '''
   try:
      cnt = coll.count_documents(filter={})
      return {
         'nb_players': cnt
      }
   except Exception as err:
      print(str(err))
      data = {
         'reason': str(err)
      }
      make_response('ERROR: An error occurred while trying to process the request', 500, data)


@api.route('/player/find_one')
def get_one_player():
   '''
   DESCRIPTION
      Cette route renvoie le premier joueur trouvé en base de données.
   RETURN
      La fonction renvoie un dictionnaire avec l'intégralité des informations contenues en base à propos du joueur.
   '''
   data = []
   cursor = coll.find_one(filter={})
   data.append(cursor)
   return {
      "data" : json.loads(json_util.dumps(data))
   }


@api.route('/player/id/<string:id>')
def get_player_per_id(id):
   '''
   DESCRIPTION
      Cette route renvoie les informations concernant le joueur correspondant à l'ID fourni en argument.
   RETURN
      La fonction renvoie un dictionnaire avec l'intégralité des informations contenues en base à propos du joueur.
   '''
   data = []
   try:
      cursor = coll.find(filter = {"_id" : ObjectId(id)})
      '''
      data.append(cursor)
      return {
         "data" : json.loads(json_util.dumps(data))
      }
      '''
      data = list(cursor)
      return {
         "data": json.loads(json_util.dumps(data))
      }
   except Exception as err:
      return {
            "data": None
         ,  "error": str(err)
      }


@api.route('/player/names')
def get_player_names():
   '''
   DESCRIPTION
      Cette route renvoie le noms de tous les joueurs référencés dans la base de données.
   RETURN
      La fonction renvoie un tableau avec l'ensemble des noms de joueurs.
   '''
   data = []
   cursor = coll.find(
         filter = {}
      ,  projection = {'_id':0, 'transfers':0}
   ).sort([('name', 1)])
   for doc in cursor:
      data.append(doc['name'])
   return {
      "data" : json.loads(json_util.dumps(data))
   }


@api.route('/player/name/<string:name>')
def get_player_per_name(name):
   '''
   DESCRIPTION
      Cette route renvoie les joueurs dont le nom contient <pattern>.
      La recherche de <pattern> dans le nom du joueur ne prend pas en compte la casse.
   '''
   data = []
   cursor = coll.find({"$text": {"$search": name}})
   data += list(cursor)
   return {
      "data" : json.loads(json_util.dumps(data))
   }


# Count the nb of transfers per player, for all players
@api.route('/transfer/count/per_player')
def get_transfer_count_per_player():
   '''
   DESCRIPTION
      Cette route renvoie le nombre de transfers réalisés par joueur.
   RETURN
      La fonction renvoie un dictionnaire avec:
         - key  : correspondant au nom du joueur
         - value: correspondant au nombre de transfers réalisés par le joueur
   '''
   data = {}
   pipeline = [
      {   "$unwind": "$transfers" },
      {   "$group":
         {   "_id": {
               "_id": "$_id",
               "name": "$name"
            }
            ,  "count": { "$sum": 1}
         }
      },
      {  "$project": {
            "player": {
                  "_id": "$_id._id.oid"
               ,  "name": "$_id.name"
               ,  "nb_transfers": "$count"
            }
            ,  "_id": 0
         }
      }
   ]
   cursor = coll.aggregate(pipeline = pipeline)
   for doc in cursor:
      player_name  = doc['player']['name']
      nb_transfers = doc['player']['nb_transfers']
      data[player_name] = nb_transfers
   return {
      "data" : json.loads(json_util.dumps(data))
   }


@api.route('/league/names')
def get_league_names():
   '''
   DESCRIPTION
      Cette route renvoie l'ensemble des noms de league référencés dans la base de données.
   RETURN
      Un tableau avec tous les noms de league.
   '''
   data = []
   pipeline = [
         {  "$unwind": "$transfers" }
      ,  {  "$project": {
                  "_id": 0
               ,  "transfers.league.from": 1
            }
         }
      ,  {  "$replaceWith": { "league_name": "$transfers.league.from" } }
      ,  {  "$unionWith": {
                  "coll": "users"
               ,  "pipeline": [
                        {  "$unwind": "$transfers" }
                     ,  {  "$project": {
                                 "_id": 0
                              ,  "transfers.league.to": 1
                           }
                        }
                     ,  {  "$replaceWith": {
                              "league_name": "$transfers.league.to"
                           }
                        }
                  ]
            }
         }
      ,  {  "$group": { "_id": "$league_name" } }
      ,  {  "$replaceWith": { "league_name": "$_id" } }
      ,  {  "$sort": { "league_name": 1 } }
   ]
   cursor = coll.aggregate(pipeline = pipeline)
   for doc in cursor:
      data.append(doc['league_name'])
   return {
      "data" : json.loads(json_util.dumps(data))
   }



@api.route('/team/names')
def get_team_names():
   '''
   DESCRIPTION
      Cette route renvoie l'ensemble des noms d'équipes référencés dans la base de données.
   RETURN
      Un tableau avec tous les noms d'équipe.
   '''
   data = []
   pipeline = [
         {  "$unwind": "$transfers" }
      ,  {  "$project": {
                  "_id": 0
               ,  "transfers.team.from": 1
            }
         }
      ,  {  "$replaceWith": { "team_name": "$transfers.team.from" } }
      ,  {  "$unionWith": {
                  "coll": "users"
               ,  "pipeline": [
                        {  "$unwind": "$transfers" }
                     ,  {  "$project": {
                                 "_id": 0
                              ,  "transfers.team.to": 1
                           }
                        }
                     ,  {  "$replaceWith": { "team_name": "$transfers.team.to" } }
                  ]
            }
         }
      ,  {  "$group": {
               "_id": "$team_name"
            }
         }
      ,  {  "$replaceWith": { "team_name": "$_id" } }
      ,  {  "$sort": { "team_name": 1 } }
   ]
   cursor = coll.aggregate(pipeline = pipeline)
   for doc in cursor:
      data.append(doc['team_name'])
   return {
      "data" : json.loads(json_util.dumps(data))
   }

@api.route('/teams_per_league')
def get_teams_per_league():
   '''
   DESCRIPTION
      Cette route renvoie l'ensemble des noms de clubs référencés dans la base de données par league.
   RETURN
      La fonction renvoie un dictionnaire avec:
         - key  : le nom de la league
         - value: un tableau avec le nom de tous les clubs qui composent cette league
   '''
   data = {}
   pipeline = [
         {  "$unwind": "$transfers" }
      ,  {  "$project": {
                  "_id": 0
               ,  "transfers.league.from": 1
               ,  "transfers.team.from": 1
            }
         }
      ,  {  "$replaceWith": {
                  "league_name": "$transfers.league.from"
               ,  "team_name"  : "$transfers.team.from"
            }
         }
      ,  {  "$unionWith": {
                  "coll": "users"
               ,  "pipeline": [
                        {  "$unwind": "$transfers" }
                     ,  {  "$project": {
                                 "_id": 0
                              ,  "transfers.league.to": 1
                              ,  "transfers.team.to": 1
                           }
                        }
                     ,  {  "$replaceWith": {
                                 "league_name": "$transfers.league.to"
                              ,  "team_name": "$transfers.team.to"
                           }
                        }
                  ]
            }
         }
      ,  {  "$group": {
               "_id": {
                     "league_name": "$league_name"
                  ,  "team_name": "$team_name"
               }
            }
         }
      ,  {  "$project": {
                  "league_name": "$_id.league_name"
               ,  "team_name": "$_id.team_name"
            }
         }
      ,  {  "$sort": {
                  "league_name": 1
               ,  "team_name": 1
            }
         }
   ]
   cursor = coll.aggregate(pipeline = pipeline)
   for doc in cursor:
      league_name = doc['league_name']
      team_name   = doc['team_name']
      if league_name in data:
         data[league_name].append(team_name)
      else:
         data[league_name] = [ team_name ]
   return {
      "data" : json.loads(json_util.dumps(data))
   }


class LeftLeagueInput(BaseModel):
   league_name:str
   beg_year:int
   end_year:str

@api.route('/players_left_league_on_period', methods=["POST"])
@validate()
def get_players_left_league_on_period(body:LeftLeagueInput):
   '''
   DESCRIPTION
      Cette route renvoie l'ensemble des noms de joueurs ayant quittés une league donnée sur une période donnée.
      La période est renseignée par:
         beg_year: année de début de période (incluse)
         end_year: année de fin de période (incluse)
   RETURN
      La fonction renvoie un tableau avec le noms des joueurs identifiés
   '''
   if not isinstance(body, LeftLeagueInput):
      return make_response('ERROR: Invalid input', 500)
   data = []
   league_name = body.league_name
   beg_year    = body.beg_year
   end_year    = body.end_year
   print('league_name: ',  league_name)
   cursor = coll.find(
      {
         "transfers": {
            "$elemMatch": {
                  "league.from": league_name
               ,  "league.to"  : { "$ne": league_name}
               ,  "season.begYear": { "$gte": beg_year }
               ,  "season.endYear": { "lte" : end_year }
            }
         }
      }
   )
   print(list(cursor))
   return {}
   data.append(cursor)

class NewPlayer(BaseModel):
   name:str
   transfers:list

@api.route("/player/add",methods=["POST"])
@validate()
def addaplayer(body:NewPlayer):
   '''
   DESCRIPTION
      Cette route ajoute un joueur et son ou ses transferts si le joueur n'existe pas déjà,
      sinon il ajoute le transfert.
   RETURN
      La fonction renvoie un dictionnaire avec:
         - data inserted ou data updated  : si le joueur n'existait pas ou si le joueur existait déjà
         - les données complètes du joueur après l'insert ou l'update
         
   '''

   name = body.name
   transfers = body.transfers
   data = {"name":body.name,"transfers":body.transfers} 
   try:
      list_bdd = list(coll.find(filter={'name':  name}))
      if len(list_bdd) == 0:
         result = coll.insert_one(data)
         return {"data inserted" : json.loads(json_util.dumps(data))}
      else:
         id_concerned = list(coll.find(filter={'name':  name}))[0]["_id"]
         data_before = list(coll.find(filter={'name':  name}))[0]
         data_after = data_before
         data_after["transfers"].append(data["transfers"])
         coll.replace_one({'_id': id_concerned}, data_after)  
         result = coll.find(filter={'name':  name})
         return {"data updated" : json.loads(json_util.dumps(result))}
   except Exception as err:
      raise Exception('ERROR: Failed')

class PerName(BaseModel):
    PlayerName:str

@api.route("/player/byname",methods=["POST"])
@validate()
def playerbyname(body:PerName):
   '''
   DESCRIPTION
      Cette route recherche un joueur par son nom exact
   RETURN
      La fonction renvoie un dictionnaire avec:
         - data inserted ou data updated  : si le joueur n'existait pas ou si le joueur existait déjà
         - les données complètes du joueur après l'insert ou l'update
         - le retour ci-dessous en cas de valeur manquante en entrée : 
         {"result":"No name sent so no name can be found"}
         - le retour ci-dessous en cas de joueur non trouvé
         {"result":"No name sent so no name can be found"}
         
   '''
   my_name = body.PlayerName
   if len(my_name) == 0:
      return {"result":"No name sent so no name can be found"}
   else:  
      try:
         cursor = list(coll.find({"name": my_name }))
         if len(cursor) == 0:
            return {"result":"No player found with this name"}
         else: 
            data = []
            
            cursor = list(coll.find({"name": my_name }))
            data.append(cursor)  
            return {"data" : json.loads(json_util.dumps(data))}
      except Exception as err:
         print(str(err))
         data = {
            'reason': str(err)
         }
         make_response('ERROR: An error occurred while trying to process the request', 500, data)


# Count the nb of transfers per origin team, for all players
@api.route('/TransfersNbPerTeamFrom')
def transfersCountPerTeamFrom():
   '''
   DESCRIPTION
      Cette route compte le nombre de transfert par équipe d'origine
   RETURN
      La fonction renvoie un dictionnaire avec:
         - _id : le nom de chaque équipe
         - count : le nombre total de transferts des joueurs ayant quitté cette équipe
         
   '''
   pipeline = [
      {"$unwind": "$transfers" },
      {"$unwind": "$transfers.team" },
      {"$unwind": "$transfers.team.from" },
      {"$group": 
         {"_id": "$transfers.team.from",
            "count": { "$sum": 1}} },
      {"$sort": { "_id": 1 }}
         ]
   try:
      results = list(coll.aggregate(pipeline=pipeline))
      return {"data" : json.loads(json_util.dumps(results))}
   
   except Exception as err:
      print(str(err))
      data = {
         'reason': str(err)
      }
      make_response('ERROR: An error occurred while trying to process the request', 500, data)

# Count the nb of transfers per target team, for all players
@api.route('/TransfersNbPerTeamTo')
def transfersCountPerTeamTo():
   '''
   DESCRIPTION
      Cette route compte le nombre de transfert par équipe cible du transfert
   RETURN
      La fonction renvoie un dictionnaire avec:
         - _id : le nom de chaque équipe
         - count : le nombre total de transferts des joueurs ayant rejoint cette équipe
         
   '''

   pipeline = [
      {"$unwind": "$transfers" },
      {"$unwind": "$transfers.team" },
      {"$unwind": "$transfers.team.to" },
      {"$group": 
         {"_id": "$transfers.team.to",
            "count": { "$sum": 1}} },
      {"$sort": { "_id": 1 }}
         ]
   try:   
      results = list(coll.aggregate(pipeline=pipeline))
      return {"data" : json.loads(json_util.dumps(results))}
   
   except Exception as err:
      print(str(err))
      data = {
         'reason': str(err)
      }
      make_response('ERROR: An error occurred while trying to process the request', 500, data)


# Count the transfers cost max per team
@api.route('/TransfersCostMaxPerTeam')
def transfersCostMaxPerTeamTo():
   '''
   DESCRIPTION
      Cette route compte le transfert le plus cher par équipe
   RETURN
      La fonction renvoie un dictionnaire avec:
         - _id : le nom de chaque équipe
         - max : le transfert le plus couteux que l'équipe a déboursé
   '''
   pipeline = [
      {"$unwind": "$transfers" },
      {"$unwind": "$transfers.team" },
      {"$unwind": "$transfers.team.to" },
      {"$group": 
         {"_id": "$transfers.team.to",
            "max": { "$max": "$transfers.cost.real"}} },
      {"$sort": { "max": -1 }}
         ]
   try:   
      results = list(coll.aggregate(pipeline=pipeline))
      return {"data" : json.loads(json_util.dumps(results))}

   except Exception as err:
      print(str(err))
      data = {
         'reason': str(err)
      }
      make_response('ERROR: An error occurred while trying to process the request', 500, data)



# db.users.find(
#    {
#       "transfers": {
#          "$elemMatch": {
#                "league.from": "Ligue 1"
#             ,  "league.to"  : { $ne: "Ligue 1"}
#             ,  "season.begYear": 2001
#          }
#       }
#    }
#    ,  { "name": 1}
# ).pretty()
