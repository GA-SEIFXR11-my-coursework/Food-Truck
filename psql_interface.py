import subprocess
import json
import psycopg2

PGUSER = "postgres"
PGPASS_FILE = ".pgpass"
DB_NAME = "food_truck"
DB_TEMPLATE_JSON = "food_db_table_format.json"
DB_SEED_DATA_JSON = "seed_food_db_data.json"
SRC_PATH = "./src"

class Psql_interface():
    table_name: str
    table_fields: list[dict]
    password: str
    db_name: str
    sh_command: str
    
    def __init__(self):
        self.password = open(PGPASS_FILE).read().strip()
        self.db_name = DB_NAME
        self.sh_command = f"PGPASSWORD={self.password} psql -U {PGUSER} -d {self.db_name}"
        self.table_fields = []
        self.table_name = ""
        return
    
    def psql_shell_query(self, sql_query: str, verbose:bool = None):
        proc = subprocess.Popen(self.sh_command, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate(input=sql_query.encode())
        stdout = stdout.decode()
        stderr = stderr.decode()
        ret = (stdout,stderr)
        if verbose != None and verbose:
            print(*ret)
        proc.terminate()
        return ret  

    def check_dbexist(self):
        proc = subprocess.Popen(self.sh_command, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate()
        err = stderr.decode()
        proc.terminate()
        if f'database "{DB_NAME}" does not exist' in err:
            return False
        return True
    
    def drop_db(self):
        if self.check_dbexist():
            sh_command = f"PGPASSWORD={self.password} psql -U postgres"
            proc = subprocess.Popen(sh_command, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = proc.communicate(input=f"DROP DATABASE {DB_NAME}".encode())
            proc.terminate()
        return
    
    def create_db(self):
        if not self.check_dbexist():
            sh_command = f"PGPASSWORD={self.password} createdb {DB_NAME}"
            proc = subprocess.Popen(sh_command, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = proc.communicate(input=f"\q".encode())
            proc.terminate()
        return
    
    def setup_db(self):
        if not self.check_dbexist():
            raise Exception("DB has not been created yet. Cannot populate DB that does not exist.")
        connection = psycopg2.connect(dbname=DB_NAME, user=PGUSER, password=self.password)
        cursor = connection.cursor()
        with open(f"{SRC_PATH}/{DB_TEMPLATE_JSON}") as fp:
            setup_info = json.load(fp)
        table =  setup_info["db_table"]
        self.table_name = table['name']
        psql_command = f"CREATE TABLE {self.table_name}"
        psql_command += "("
        for column, type in table["columns"].items():
            self.table_fields.append({"column":column,"type":type})
            psql_command += f"{column} {type}," 
        psql_command = psql_command[:-1]    # remove last comma
        psql_command += ");"
        cursor.execute(psql_command)
        connection.commit()
        connection.close()
        return
    
    def populate_table_from_json(self):
        if not self.check_dbexist():
            raise Exception("DB has not been created yet. Cannot populate DB that does not exist.")
        connection = psycopg2.connect(dbname=DB_NAME, user=PGUSER, password=self.password)
        cursor = connection.cursor()
        with open(f"{SRC_PATH}/{DB_SEED_DATA_JSON}") as fp:
            data = json.load(fp)
        for entry in data['entries']:
            field_values = []
            field_names = []
            for field in self.table_fields:
                if "PRIMARY KEY" in field["type"]:
                    continue
                try:
                    value = entry[ field["column"] ]
                except:
                    continue
                field_names.append( field["column"] )
                if any( substring in field["type"].lower() for substring in ["text", "char"] ):
                    field_values.append( str(value) )
                elif( "int" in field["type"].lower() ):
                    field_values.append( int(value) )
                else:
                    field_values.append( value )
            placeholders_str = ", ".join([ "%s" for x in range(len(field_names)) ])
            psql_command = f"""
                INSERT INTO {self.table_name}({', '.join(field_names)})
                VALUES ({placeholders_str})
                ;
            """
            cursor.execute(psql_command, field_values)
        connection.commit()
        connection.close()
        return
    
    def regenerate_db(self):
        self.drop_db()
        self.create_db()
        self.setup_db()
        self.populate_table_from_json()
        return
    
if __name__ == "__main__":
    psql = Psql_interface()
    psql.regenerate_db()
    pass