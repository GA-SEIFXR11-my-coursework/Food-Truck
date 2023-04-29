import subprocess
import json
import psycopg2

class Psql_interface():
    """
        src_path is where the json files are contained
        src_path should be an abspath
    """
    pguser: str
    _password: str
    db_name: str
    db_template_json_fpath: str
    db_seed_json_fpath: str
    src_path: str 
    sh_command: str
    table_name: str
    table_fields: list[dict]
    
    def __init__(self, pguser:str, pgpass:str, db_name:str,  src_path:str, db_template_json_fpath:str, db_seed_json_fpath:str,):
        self.pguser = pguser
        self._password = pgpass
        self.db_name = db_name
        self.db_template_json_fpath = db_template_json_fpath
        self.db_seed_json_fpath = db_seed_json_fpath
        self.src_path = src_path
        self.sh_command = f"PGPASSWORD={self._password} psql -U {pguser} -d {self.db_name}"
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
    
    def psql_psycopg2_query(self, sql_query: str, field_values: list = None):
        if not self.check_dbexist():
            raise Exception("DB has not been created yet. Cannot populate DB that does not exist.")
        connection = psycopg2.connect(dbname=self.db_name, user=self.pguser, password=self._password)
        cursor = connection.cursor()
        if field_values != None:
            cursor.execute(sql_query, field_values)
        else:
            cursor.execute(sql_query)
        try:
            results = cursor.fetchall()
        except:
            results = None
        connection.commit()
        connection.close()
        return results

    def check_dbexist(self):
        proc = subprocess.Popen(self.sh_command, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        _, stderr = proc.communicate()
        err = stderr.decode()
        proc.terminate()
        if f'database "{self.db_name}" does not exist' in err:
            return False
        return True
    
    def drop_db(self):
        if self.check_dbexist():
            sh_command = f"PGPASSWORD={self._password} psql -U postgres"
            proc = subprocess.Popen(sh_command, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            _, _ = proc.communicate(input=f"DROP DATABASE {self.db_name}".encode())
            proc.terminate()
        return
    
    def create_db(self):
        if not self.check_dbexist():
            sh_command = f"PGPASSWORD={self._password} createdb {self.db_name}"
            proc = subprocess.Popen(sh_command, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            _, _ = proc.communicate(input=f"\q".encode())
            proc.terminate()
        return
    
    def setup_db(self):
        with open(f"{self.src_path}/{self.db_template_json_fpath}") as fp:
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
        self.psql_psycopg2_query(psql_command)
        return
    
    def populate_table_from_json(self):
        with open(f"{self.src_path}/{self.db_seed_json_fpath}") as fp:
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
            self.psql_psycopg2_query(psql_command, field_values)

        return
    
    def regenerate_db(self):
        self.drop_db()
        self.create_db()
        self.setup_db()
        self.populate_table_from_json()
        return
    
if __name__ == "__main__":
    pass