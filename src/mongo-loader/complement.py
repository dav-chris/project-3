# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Import
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# 3rd Party
from pymongo import MongoClient



# users = list()


# def transformDoc(doc):

#    # Season
#    season = None
#    try:
#       seasonFields = doc.get('Season')
#       if seasonFields and len(seasonFields) == 2:
#          season = {
#                'beg_year':
#             ,  'end_year':
#          }
#          season[] = int(seasonFields[0])
#          season['end_year'] = seasonFields[0]
#    except Exception as e:
#       season = None

#    newDoc = {
#          'name': doc.get('Name')
#       ,  'transfers': list()
#    }

#    transfer = {
#          'age'       : doc.get('Age')
#       ,  'position'  : doc.get('Position')
#       ,  'league'    : {
#                'from': doc.get('League_from')
#             ,  'to'  : doc.get('League_to')
#          }
#       ,  'team'      : {
#                'from': doc.get('Team_from')
#             ,  'to'  : doc.get('Team_to')
#          }
#       ,  'season'    : {
#                'beg_year': doc.get('')
#          }
#    )




#             end_date:
#          }
#          cost: {
#             estimation:    <market_value>
#             real:          <transfer_fee>
#          }
#    }

#    name =
#    if name:
#       newDoc['name'] = name


#    position = doc.get('Position')



########################################################################################################################
#
# MAIN PROGRAM starts here...
#
########################################################################################################################

client = MongoClient(
      host       = 'localhost'
   ,  port       = 49153
   ,  username   = 'admin'
   ,  password   = 'admin'
   ,  authSource = 'admin'
)

db         = client['footballers']
collection = db['intial_data']

cursor = collection.find(
      filter = {}
   ,  projection = { '_id': False }
   ,  batch_size = 100000
)

cnt = 0
for doc in cursor:
   cnt += 1

print('count: ', cnt)