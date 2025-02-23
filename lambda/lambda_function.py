import json
import sys
import logging
import redis
import pymysql


DB_HOST = "database-1.cluster-c7iwis0ge5r4.us-east-1.rds.amazonaws.com" # Add DB end point
DB_USER = "admin" # Add your database user
DB_PASS = "KesavarAdmin" # Add your database password
DB_NAME = "superhero_db" # Add your database name
DB_TABLE = "superheroes" # Add your table name
REDIS_URL = "redis://redis-oss-cache.ef1kkf.ng.0001.use1.cache.amazonaws.com:6379" # Add redis end point "redis://<end point>"

TTL = 60

class DB:
    def __init__(self, **params):
        params.setdefault("charset", "utf8mb4")
        params.setdefault("cursorclass", pymysql.cursors.DictCursor)

        self.mysql = pymysql.connect(**params)

    def query(self, sql):
        with self.mysql.cursor() as cursor:
            cursor.execute(sql)
            return cursor.fetchall()

    def record(self, sql, values):
        with self.mysql.cursor() as cursor:
            cursor.execute(sql, values)
            return cursor.fetchone()

    def get_idx(self, table_name):
        with self.mysql.cursor() as cursor:
            cursor.execute(f"SELECT MAX(id) as id FROM {table_name}")
            idx = str(cursor.fetchone()['id'] + 1)
            return idx

    def insert(self, idx, data, table_name):
        with self.mysql.cursor() as cursor:
            hero = data["hero"]
            power = data["power"]
            name = data["name"]
            xp = data["xp"]
            color = data["color"]
            
            sql = f"INSERT INTO {table_name} (`id`, `hero`, `power`, `name`, `xp`, `color`) VALUES ('{idx}', '{hero}', '{power}', '{name}', '{xp}', '{color}')"
            cursor.execute(sql)
            self.mysql.commit()

def read(use_cache, xps, Database, Cache):
    # Lazy Loading Strategy
    result = []

    for xp in xps:
        xp_str = str(xp)  # Redis key must be a string

        if use_cache:
            cached_data = Cache.get(xp_str)
            if cached_data:
                try:
                    row = json.loads(cached_data)  # Parse JSON from Redis
                    result.append(row)
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON from Redis: {e}")
                    # Handle the error, perhaps by querying the DB
                    sql = f"SELECT * FROM superheroes WHERE xp = {xp}"
                    rows = Database.query(sql)
                    if rows:
                        row = rows[0]
                        result.append(row)
                        Cache.set(xp_str, json.dumps(row), ex=TTL)  # Update Redis
            else:  # Cache miss
                sql = f"SELECT * FROM superheroes WHERE xp = {xp}"
                rows = Database.query(sql)
                if rows:
                    row = rows[0]
                    result.append(row)
                    Cache.set(xp_str, json.dumps(row), ex=TTL)  # Store in Redis
        else:  # No cache
            sql = f"SELECT * FROM superheroes WHERE xp = {xp}"
            rows = Database.query(sql)
            if rows:
                row = rows[0]
                result.append(row)

    return result

def write(use_cache, sqls, Database, Cache):
    # Write Through Strategy
    for data in sqls:
        idx = Database.get_idx(DB_TABLE)  # Get the next ID
        Database.insert(idx, data, DB_TABLE)  # Insert into the database

        if use_cache:  # Use cache (Write-Through)
            xp = data['xp']  # Assuming xp is a string
            try:
                # Retrieve the full row from the database to cache
                sql = f"SELECT * FROM {DB_TABLE} WHERE xp = {xp}"
                rows = Database.query(sql)

                if rows:  # Check if any rows were returned
                    row = rows[0]
                    Cache.set(str(xp), json.dumps(row), ex=TTL)  # Update Redis
                else:
                    print(f"Warning: No row found in database for xp: {xp} after insert.")
                    # Log the error or handle it appropriately. It's crucial not to let a 
                    # cache update failure prevent the database insert from completing.

            except Exception as e:
                print(f"Error updating cache for xp: {xp}: {e}")
                # Log the error or handle it appropriately. It's crucial not to let a 
                # cache update failure prevent the database insert from completing.

        else: # Do not use cache
            pass # No caching needed
        

def lambda_handler(event, context):
    
    USE_CACHE = (event['USE_CACHE'] == "True")
    REQUEST = event['REQUEST']
    
    # Initialize database
    try:
        Database = DB(host=DB_HOST, user=DB_USER, password=DB_PASS, db=DB_NAME)
    except pymysql.MySQLError as e:
        print("ERROR: Unexpected error: Could not connect to MySQL instance.")
        print(e)
        sys.exit()
        
    # Initialize cache
    Cache = redis.Redis.from_url(REDIS_URL)
    
    result = []
    if REQUEST == "read":
        # event["SQLS"] is a list of all xps for which you have to query the database or redis.
        result = read(USE_CACHE, event["SQLS"], Database, Cache)
        
    elif REQUEST == "write":
        # event["SQLS"] should be a list of jsons. You have to write these rows to the database.
        write(USE_CACHE, event["SQLS"], Database, Cache)
        result = "write success"
    
    
    return {
        'statusCode': 200,
        'body': result
    }
