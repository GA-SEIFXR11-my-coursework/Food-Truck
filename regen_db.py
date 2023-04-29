from psql_interface import Psql_interface

if __name__ == "__main__":
    psql = Psql_interface()
    psql.regenerate_db()
    
    