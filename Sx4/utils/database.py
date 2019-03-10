import rethinkdb as r

connection = r.connect(db="sx4")

class Database:
    def get_connection():
        return connection