import pymysql
import json
from datetime import (
    datetime,
    timedelta
)

from ..config import (
    DB_HOST,
    DB_USER,
    DB_PASSWORD
)


CURSOR_TYPE = pymysql.cursors.DictCursor
DB_CHARSET = "utf8mb4"


class RDSClient():
    """
    """
    
    def __init__(self):
        """
        """
        self._database = pymysql.connect(host=DB_HOST,
                                         db='ebdb',
                                         charset=DB_CHARSET,
                                         user=DB_USER,
                                         password=DB_PASSWORD,
                                         autocommit=True,
                                         cursorclass=CURSOR_TYPE)
        self._cursor = self._database.cursor()
        
    def select_query(self,
                     query: str,
                     fetchone: bool = False) -> object:
        """
        Executes a SELECT query. Returns one or all rows selected.
        :param query: the select query to execute.
        :param fetchone: if set to True, only returns the firt selected row.
                            If set to False, returns all rows.
        """
        print(f'select_query : INFO : Executing query {query}')
        try:
            self._cursor.execute(query)
            if fetchone:
                return self._cursor.fetchone()
            return self._cursor.fetchall()
        except Exception as e:
            print(f'select_query : ERROR : {e}')
    
    
    def update_query(self,
                     query: str) -> bool:
        """
        Executes an UPDATE query. Returns True if query is executed succesfully.
        :param query: the update query to execute. 
        """
        print(f'update_query : INFO : Executing query {query}')
        try:
            self._cursor.execute(query)
            self._database.commit()
            return True
        except Exception as e:
            print(f'select_query : ERROR : {e}')
            return False
        
        
    def delete_query(self,
                     query: str) -> bool:
        """
        Executes a DELETE query. Returns True if query is executed succesfully.
        :param query: the delete query to execute.
        """
        print(f'delete_query : INFO : Executing query {query}')
        try:
            self._cursor.execute(query)
            self._database.commit()
            return True
        except Exception as e:
            print(f'select_query : ERROR : {e}')
            return False

    def insert_query(self,
                     query: str) -> object:
        """
        Executes an INSERT query. Returns the primary key of the inserted row.
        :param query: the insert query to execute.
        """
        print(f'insert_query : INFO : Executing query {query}')
        try:
            self._cursor.execute(query)
            self._database.commit()
            return self._cursor.lastrowid
        except Exception as e:
            print(f'select_query : ERROR : {e}')
            return False
        
    def get_object(self,
                   table: str,
                   id: int) -> dict:
        """
        """
        if not table.startswith('neuralplatform_'):
            table = 'neuralplatform_' + table
        query = f"SELECT * FROM {table} WHERE id = {id};"
        return self.select_query(query, fetchone=True)
    
    def get_objects(self,
                    table: str,
                    ids: list) -> list:
        """
        """
        if not table.startswith('neuralplatform_'):
            table = 'neuralplatform_' + table
        query = f"SELECT * FROM {table} WHERE id IN {tuple(ids)};"
        return self.select_query(query, fetchone=False)    
        
    def get_project_version_documents(self,
                                      project_id: int,
                                      version_id: int) -> list:
        """
        """
        query = f"SELECT d.id, d.uri FROM neuralplatform_document d, neuralplatform_version v WHERE (d.project_id = {project_id} AND v.id = {version_id} AND (d.uploadDate BETWEEN v.startDate AND v.endDate));"
        return self.select_query(query, fetchone=False)

    def get_project(self,
                    project_id: int) -> dict:
        """
        """
        query = f"SELECT * FROM neuralplatform_project p WHERE p.id = {project_id};"
        return self.select_query(query, fetchone=True)
    
    def get_project_bucket(self,
                           project_id: int) -> str:
        """
        """
        query = f"SELECT s3Bucket FROM neuralplatform_account a, neuralplatform_project p WHERE p.id = {project_id} AND p.account_id = a.id"
        return self.select_query(query, fetchone=True)['s3Bucket']
    
    def update_version_status(self,
                              version_id: int,
                              status: str) -> bool:
        """
        """
        query = f"UPDATE neuralplatform_version v SET status = '{status}' WHERE v.id = {version_id};"
        return self.update_query(query)

    def get_document_name_and_uri(self,
                                  document_id: int) -> tuple:
        """
        """
        query = f"SELECT * FROM neuralplatform_document WHERE id = {document_id};"
        document = self.select_query(query, fetchone=True)
        return document['name'], document['uri']
        
    def insert_page(self,
                    document_id: int,
                    img_uri: str = "",
                    ocr_uri: str = "") -> int:
        """
        """
        query = f'INSERT INTO neuralplatform_page(imgUri, ocrUri, document_id) VALUES ("{img_uri}", "{ocr_uri}", {document_id});'
        return self.insert_query(query)
    
    def update_page_time(self,
                         page_id: int,
                         img_or_ocr: str,
                         start_or_end: str) -> bool:
        """
        """
        time = datetime.now()
        start_or_end = start_or_end[0].upper() + start_or_end[1:]
        query = f'UPDATE neuralplatform_page SET {img_or_ocr}{start_or_end}Time = "{time}" WHERE id = {page_id};'
        return self.insert_query(query)
    
    def update_page_img(self,
                        page_id: int,
                        img_uri: str) -> bool:
        """
        """
        query = f'UPDATE neuralplatform_page SET imgUri = "{img_uri}" WHERE id = {page_id};'
        return self.insert_query(query)
    
    def update_page_ocr(self,
                        page_id: int,
                        ocr_uri: str) -> bool:
        """
        """
        query = f'UPDATE neuralplatform_page SET ocrUri = "{ocr_uri}" WHERE id = {page_id};'
        return self.insert_query(query)
    
    def update_page_img_status(self,
                               page_id: int,
                               status: str) -> bool:
        """
        """
        query = f'UPDATE neuralplatform_page SET imgStatus = "{status}" WHERE id = {page_id};'
        return self.insert_query(query)
    
    def update_page_ocr_status(self,
                               page_id: int,
                               status: str) -> bool:
        """
        """
        query = f'UPDATE neuralplatform_page SET ocrStatus = "{status}" WHERE id = {page_id};'
        return self.insert_query(query)

    def get_page(self,
                 page_id: int):
        """
        """
        query = f"SELECT * FROM neuralplatform_page WHERE id = {page_id};"
        return self.select_query(query, fetchone=True)
    
    def get_pages(self,
                 page_ids: int):
        """
        """
        query = f"SELECT * FROM neuralplatform_page WHERE id IN {tuple(page_ids)};"
        return self.select_query(query, fetchone=False)
    
    def get_document_pages(self,
                           document_id: int) -> list:
        """
        """
        query = f"SELECT * FROM neuralplatform_page WHERE document_id = {document_id};"
        return self.select_query(query)
    
    def check_preprocessed_pages(self,
                                 page_ids: list,
                                 timeout: int = 15*60) -> tuple:
        """
        """
        img_status = list()
        ocr_status = list()
        preprocessed = list()
        
        for page in self.get_pages(page_ids):
            img_status.append(str(page['imgStatus']))
            ocr_status.append(str(page['ocrStatus']))
            # Check img
            img_done = False
            if (page['imgStatus'] in ("COMPLETED", "FAILED")):
                img_done = True
            elif page['imgStatus'] == "RUNNING":
                if (datetime.now() - page['imgStartTime'] > timedelta(seconds=timeout)):
                    self.update_page_img_status(page['id'], "FAILED")
            # Check ocr
            ocr_done = False
            if (page['ocrStatus'] in ("COMPLETED", "FAILED")):
                ocr_done = True
            elif page['ocrStatus'] == "RUNNING":
                if (datetime.now() - page['ocrStartTime'] > timedelta(seconds=timeout)):
                    self.update_page_ocr_status(page['id'], "FAILED")
            
            preprocessed.append(img_done and ocr_done)

        return all(preprocessed), preprocessed, img_status, ocr_status
    
    def get_preprocessed_pages(self,
                               page_ids: list):
        """
        """
        classes = []
        img_uris = []
        ocr_uris = []
        
        for page in self.get_pages(page_ids):
            if page['tagged'] and page['imgStatus'] == "COMPLETED" and page['ocrStatus'] == "COMPLETED":
                query = f"SELECT classDefinition_id FROM neuralplatform_classification WHERE page_id = {page['id']};"
                class_id = self.select_query(query, fetchone=True)['classDefinition_id']
                classes.append(class_id)
                img_uris.append(page['imgUri'])
                ocr_uris.append(page['ocrUri'])

        return classes, img_uris, ocr_uris

    def get_project_num_classes(self,
                                project_id: int) -> int:
        """
        """
        query = f"SELECT COUNT(*) AS count FROM neuralplatform_classdefinition WHERE project_id = {project_id};"
        return self.select_query(query, fetchone=True)['count']
    
    def get_project_classes(self,
                            project_id: int) -> list:
        """
        """
        query = f"SELECT * FROM neuralplatform_classdefinition WHERE project_id = {project_id};"
        return self.select_query(query)

    def insert_model(self,
                     version_id: int,
                     model_name: str,
                     hyperparams: str,
                     results_file_uri: str) -> int:
        """
        """
        query = f"INSERT INTO neuralplatform_model(name, hyperparams, resultsFileUri, version_id) VALUES('{model_name}', '{hyperparams}', '{results_file_uri}', {version_id});"
        return self.insert_query(query)
    
    def get_version_model(self,
                  version_id: int) -> dict:
        """
        """
        query = f"SELECT * FROM neuralplatform_model WHERE version_id = {version_id};"
        return self.select_query(query, fetchone=True)
    
    def insert_class_performance(self,
                                 model_id: int,
                                 class_id: int,
                                 acc_by_aut: dict,
                                 conf: float,
                                 aut: float):
        """
        """
        query = f"INSERT INTO neuralplatform_classperformance(model_id, classDefinition_id, accByAut, minConfidence, automatization) VALUES({model_id}, {class_id}, '{json.dumps(acc_by_aut)}', {conf}, {aut});"
        return self.insert_query(query)
    
    def get_version_confidences(self,
                                version_id: int) -> dict:
        """
        """
        query = f"SELECT id FROM neuralplatform_model WHERE version_id = {version_id};"
        model_id = self.select_query(query, fetchone=True) ['id']
        query = f"SELECT classDefinition_id, minConfidence FROM neuralplatform_classperformance WHERE model_id = {model_id};"
        return { r['classDefinition_id'] : r['minConfidence'] for r in self.select_query(query, fetchone=False) }
    
    ## Automlapi functions
    def get_pending_and_unblocked_steps(self):
        """
        """
        query = 'SELECT * FROM neuralplatform_step WHERE status = "pending";'
        pending_steps = self.select_query(query)
        # Get definition dependencies, 
        query = 'SELECT id, blockingStep_id FROM neuralplatform_stepdefinition;'
        dependencies = { sd['id']: sd['blockingStep_id'] for sd in self.select_query(query) }
        dependencies_satisfied = dict()
        # Check if dependencies satisfied
        for dependency, blocking_step_id in dependencies.items():
            query = f"SELECT * FROM neuralplatform_step WHERE status NOT IN ('succeeded', 'error') AND stepDefinition_id = {blocking_step_id}"
            satisfied = not ( bool( len(self.select_query(query)) ) )
            dependencies_satisfied[dependency] = satisfied
        # Return pending steps with dependencies satisfied
        return [ step for step in pending_steps if dependencies_satisfied[step['id']] ]
