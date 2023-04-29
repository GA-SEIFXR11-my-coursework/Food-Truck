from psql_interface import Psql_interface
import os
import sys 

PGUSER = "postgres"
PGPASS_FILE = ".pgpass"
DB_NAME = "food_truck"
DB_TEMPLATE_JSON = "food_db_table_format.json"
DB_SEED_DATA_JSON = "seed_food_db_data.json"
SRC_PATH = "../src"

if __name__ == "__main__":
    here_abspath = os.path.dirname( os.path.realpath( sys.argv[0] ) )
    src_path = os.path.abspath( os.path.join( here_abspath, SRC_PATH ) )
    pgpass = open(os.path.join(here_abspath, PGPASS_FILE)).read().strip()
    psql = Psql_interface(PGUSER, pgpass, DB_NAME, src_path, DB_TEMPLATE_JSON, DB_SEED_DATA_JSON)
    psql.regenerate_db()