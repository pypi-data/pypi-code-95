import pymysql as mysql
import os
import hashlib
import json


BD_HOST = 'aaf8asdx5lx07e.cqioz7mocjad.eu-west-3.rds.amazonaws.com'
BD_PASS = 'Sca3Zp5#g'
BD_DATABASE = 'ebdb'
BD_USER = 'dbadmin'

def run_exists(query):

    exists = False

    try:
        db = mysql.connect(host=BD_HOST,
                database=BD_DATABASE,
                user=BD_USER,
                password=BD_PASS)
        cursor = db.cursor()
        cursor.execute(query)
        response = cursor.fetchall()
        exists = len(response) > 0
    except Exception as e:
        print(f"run_exists - ERROR - {e}")
    finally:
        db.close()

    return exists

def run_select(query):
    result = []

    try:
        db = mysql.connect(host=BD_HOST,
                database=BD_DATABASE,
                user=BD_USER,
                password=BD_PASS)
        cursor = db.cursor()
        cursor.execute(query)
        response = cursor.fetchall()
        field_names = [i[0] for i in cursor.description]
        for elem in response:
            result.append({})
            for index, value in enumerate(elem):
                result[-1][field_names[index]] = value
    except Exception as e:
        print(f"run_select - ERROR - {e}")
    finally:
        db.close()
    return result

def run_update(query):
	try:
		db = mysql.connect(host=BD_HOST,
							database=BD_DATABASE,
							user=BD_USER,
							password=BD_PASS)

		cursor = db.cursor()
		cursor.execute(query)
		db.commit()
	except Exception as e:
		print("run_update - ERROR " + str(e))
	finally:
		db.close()

def get_pending_and_unblocked_steps():
    query1 = 'SELECT * FROM neuralplatform_step WHERE status = "pending";'
    pending_steps = run_select(query1)
    unblocked_steps = []
    if len(pending_steps) > 0:
        pending_stepDefinitions = list(set([x['stepDefinition_id'] for x in pending_steps]))
        unblocked_stepDefinitions = []
        query2 = 'SELECT id, blockingStep_id FROM neuralplatform_stepdefinition;'
        stepDefinitions = run_select(query2)
        dependencies = {s['id']: s['blockingStep_id'] for s in stepDefinitions}
        for pending_stepDefinition in pending_stepDefinitions:
            sd_dependency = dependencies[pending_stepDefinition] or -1
            if not run_exists(f'SELECT id FROM neuralplatform_step WHERE status != "done" AND stepDefinition_id = {sd_dependency}'):
                unblocked_stepDefinitions.append(pending_stepDefinition)
        unblocked_steps = list(filter(lambda x: x['stepDefinition_id'] in unblocked_stepDefinitions, pending_steps))
    return unblocked_steps

def get_n_objects_by_key(objectName, n=1, key='id', keyValue=1):

    operator = '='
    if isinstance(keyValue, list):
        operator = 'IN'
        keyValue = '(' + str(keyValue)[1:-1] + ')'
    elif isinstance(keyValue, str):
        keyValue = '"' + keyValue + '"'
    query = f'SELECT * FROM neuralplatform_{objectName.lower()} WHERE {key} {operator} {keyValue};'
    elements = run_select(query)
    if len(elements) > 0:
        return elements[:n]
    return None

def update_object_by_key(objectName, key='id', keyValue=1, fields=None):

    if fields:
        operator = '='
        if isinstance(keyValue, list):
            operator = 'IN'
            keyValue = '(' + str(keyValue)[1:-1] + ')'
        elif isinstance(keyValue, str):
            keyValue = '"' + keyValue + '"'
        changes = ""
        for field in fields:
            value = fields[field]
            if isinstance(value, str):
                value = '"' + value + '"'
            changes += field + ' = ' + str(value) + ', '
        else:
            changes = changes[:-2]
        query = f'UPDATE neuralplatform_{objectName.lower()} SET {changes} WHERE {key} {operator} {keyValue};'
        run_update(query)

if __name__ == '__main__':
    update_object_by_key('StepDefinition', 'stepName', ['pdf2image', 'ocr', 'inference'], {'priority': 1})
