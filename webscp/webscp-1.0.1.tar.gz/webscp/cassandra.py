import cassandra
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider

#string = "USERS_DETAIL"
class cassandra:
    
    def __init__(self, loc, client_id, client_pass):

        cloud_config= {
        'secure_connect_bundle': '{}'.format(loc)
        }
        auth_provider = PlainTextAuthProvider('{}'.format(client_id), '{}'.format(client_pass))    
        cluster = Cluster(cloud=cloud_config, auth_provider=auth_provider)
        session = cluster.connect()
        row = session.execute("select release_version from system.local").one()
        
        if row:
            print(row[0])
        else:
            print("An error occurred.")
        self.session = session        

        
    def is_keyspace_present(self,query_keyspace="SELECT * FROM system_schema.keyspaces"):
        capture =  self.session.execute(query_keyspace)
        for i in capture:
            if i[0] == self.data:
                return True
        else:
            return False  
            
        
    def create_table(self, data):
        self.data = data
        query_create_table = f"CREATE TABLE IF NOT EXISTS ineuron.{data}(img_id int PRIMARY KEY , img_src text)"
        try:
            self.session.execute(query_create_table).one()
            print("TABLE CREATED")
        except:
            print("ERROR WHILE CREATING TABLE")

    
    def insert_into_table(self, image_data):
        query_insert_table=f"INSERT INTO ineuron.{self.data}(img_src)VALUES('{image_data}'"
        try:
            self.session.execute(query_insert_table).one()
            print("INSERTED")
        except:
            print("NOT ABLE TO INSERT")
       
        
    def fetch_records_img_src(self):
        query_fetch_user = f"SELECT img_src FROM ineuron.{self.data}"
        try:
            self.session.execute(query_fetch_user)
            print("DATA FETCHED")
        except:
            print("UNABLE TO FETCH DATA")