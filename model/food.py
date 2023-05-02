from psql_interface import Psql_interface
import os
import sys 

PGUSER = "postgres"
PGPASS_FILE = ".pgpass"
DB_NAME = "food_truck"
SRC_PATH = "../src"

here_abspath = os.path.dirname( os.path.realpath( sys.argv[0] ) )
src_path = os.path.abspath( os.path.join( here_abspath, SRC_PATH ) )
pgpass = open(os.path.join(here_abspath, PGPASS_FILE)).read().strip()
psql = Psql_interface(PGUSER, pgpass, DB_NAME, src_path)

