from psql_interface import Psql_interface
import os
import sys 

PGUSER = "postgres"
PGPASS_FILE = ".pgpass"
DB_NAME = "food_truck"
TEMPLATE_JSON = "db_tables_template.json"
FOODS_SEED_DATA_JSON = "db_food_seed_data.json"
SRC_PATH = "../src"

if __name__ == "__main__":
    here_abspath = os.path.dirname( os.path.realpath( sys.argv[0] ) )
    src_path = os.path.abspath( os.path.join( here_abspath, SRC_PATH ) )
    pgpass = open(os.path.join(here_abspath, PGPASS_FILE)).read().strip()
    psql = Psql_interface(PGUSER, pgpass, DB_NAME, src_path)
    psql.reset_db()
    psql.set_db_template_json_fname(TEMPLATE_JSON)
    psql.setup_tables_from_json()
    psql.set_db_seed_json_fname(FOODS_SEED_DATA_JSON)
    psql.populate_table_from_json()