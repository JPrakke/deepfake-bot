import config
import pymongo

# Setup connection
mongo_user = config.mongo_user
mongo_pw = config.mongo_pw
mongo_url = config.mongo_url
conn = f'mongodb://{mongo_user}:{mongo_pw}@{mongo_url}'
client = pymongo.MongoClient(conn)

# Make this global so we can reuse the connection for each query
global db
db = client.heroku_v8cr4vbg

print('Connecting to database...')
print(db.list_collection_names())

# TODO....
def query1():
    return

def query2():
    return
