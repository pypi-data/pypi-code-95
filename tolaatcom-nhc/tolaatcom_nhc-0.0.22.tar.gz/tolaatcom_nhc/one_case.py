import time
import threading
import json
import logging
import datetime

from tolaatcom_nhc import boto3factory
from tolaatcom_nhc import nethamishpat
from tolaatcom_nhc.diff  import Diff


class OneCase:

    def __init__(self, master_table=None, config=None):
        self.config = config or {}
        self.master = master_table or 'master_table'
        self.bucket = 'cloud-eu-central-1-q97dt1m5d4rndek'
        self.prefix = 'documents_v2/decision_documents'
        self.local = threading.local()
        self.nhc = None
        self.default_storage = 'ONEZONE_IA'
        self.storage = self.config.get('storage_class', self.default_storage)

        #
        # Means we are doing mass scrape
        #
        self.logger = logging.getLogger('onecase')
        self.skip_documents = self.config.get('skip_documents', False)


    def map_to_dynamo(self, m):
        d = {}
        for k, v in m.items():
            if v:
                d[k] = {'S': str(v)}
        return {'M': d}

    def list_to_dynamo(self, l):
        dl = []
        for s in l:
            del s['__type']
            dl.append(self.map_to_dynamo(s))

        return {'L': dl}

    def dynamo_to_list_of_maps(self, m):
        if not m or 'L' not in m:
            return []
        r = []
        for entry in m['L']:
            o = self.dynamo_to_map(entry)
            r.append(o)
        return r

    def dynamo_to_map(self, m):
        if not m or 'M' not in m:
            return []
        o = {}
        for k, v in m['M'].items():
            first = next(iter(v.values()))
            o[k] = first
        return o

    def upload_decisions(self, caseid, type, decisions, offset=0):
        s3 = boto3factory.client('s3')
        st = self.storage
        for index, decision in enumerate(decisions, offset):
            i = str(index).zfill(3)

            if decision.get('not-scraped'):
                self.logger.info('Not scraped')
                continue

            if 'images' in decision:
                key = f'{self.prefix}/{caseid}/{type}/{i}.json'
                j = json.dumps(decision['images'])
                self.logger.info('Writing to s3://%s/%s', self.bucket, key)
                s3.put_object(Bucket=self.bucket, Key=key, ContentType='application/json', Body=j, StorageClass=st)
                del decision['images']

            if 'pdf' in decision:
                key = f'{self.prefix}/{caseid}/{type}/{i}.pdf'
                self.logger.info('Writing to s3://%s/%s', self.bucket, key)
                s3.put_object(Bucket=self.bucket, Key=key, ContentType='application/pdf', Body=decision['pdf'],
                              StorageClass=st)
                decision['pdf'].close()
                del decision['pdf']

    def get_nhc(self):
        if not self.nhc:
            self.nhc = nethamishpat.NethamishpatApiClient(config=self.config)

        return self.nhc

    def remove_nhc(self):
        if self.nhc:
            del self.nhc

    def init_permissions(self, key):
        dynamo = boto3factory.client('dynamodb')
        dynamo.update_item(TableName=self.master, Key=key, UpdateExpression='SET #p = if_not_exists(#p, :empty)',
                           ExpressionAttributeNames={'#p': 'permissions'},
                           ExpressionAttributeValues={':empty': {'M': {}}})

    def set_permissions(self, key, permission_name, reason):
        dynamo = boto3factory.client('dynamodb')

        self.init_permissions(key)

        value = {'M': {'ts': {'N': str(int(time.time()))}, 'reason': {'S': reason}}}

        dynamo.update_item(TableName=self.master, Key=key,
                                UpdateExpression='SET #ps.#p=:v',
                                ExpressionAttributeNames={'#ps': 'permissions', '#p': permission_name},
                                ExpressionAttributeValues={':v': value})

    def get_permission(self, key, permission):
        dynamo = boto3factory.client('dynamodb')

        r = dynamo.get_item(TableName=self.master, Key=key,
                        ProjectionExpression='#permissions.#permission',
                       ExpressionAttributeNames={'#permissions': 'permissions', '#permission': permission}
        )

        if not r['Item']:
            return None
        p = r['Item']['permissions']['M'][permission]['M']
        return p

    def is_govblocked(self, key):
        return self.get_permission(key, 'govblock') is not None

    def fetch(self, key):
        dynamo = boto3factory.client('dynamodb')
        fields = ('api', 'permissions')
        attribute_names = {f'#{attr}': attr for attr in fields}
        projection_expr_list = [f'#{attr}' for attr in fields]
        projection_expr = ', '.join(projection_expr_list)
        r = dynamo.get_item(TableName=self.master, Key=key,
                            ProjectionExpression=projection_expr,
                            ExpressionAttributeNames=attribute_names)

        return r.get('Item')

    def can_scrape(self, key):
        r = self.fetch(key)

        if 'Item' not in r:
            return True

        item = r['Item']
        return 'api' not in item and 'permissions' not in r


    def mark_govblock(self, case):
        case_id = case['CaseDisplayIdentifier']
        ct = case['CaseType']
        key = {'case_id': {'S': f'{ct}:{case_id}'}}
        if self.is_govblocked(key):
            logging.info('Case %s is already govblocked', case)
            return
        keys = [key]
        dynamo = boto3factory.client('dynamodb')

        r= dynamo.batch_get_item(RequestItems={self.master: {'Keys': keys}})
        if len(r['Responses'][self.master]) != 1:
            return
        item = r['Responses'][self.master][0]
        key = {'case_id': item['case_id']}
        self.set_permissions(key, 'govblock', 'unavailable')


    def get_key(self, case):
        case_number = case['CaseDisplayIdentifier']
        t = case['CaseType']
        return {'case_id': {'S': f'{t}:{case_number}'}}


    def mass_scrape(self, case):
        if not self.can_scrape(self.get_key(case)):
            return

        self.handle(case)

    def smart_scrape(self, case):
        self.logger.info('Smart scrape %s', case)

        _1d = datetime.timedelta(days=1)
        now = datetime.datetime.now()
        key = self.get_key(case)
        r = self.fetch(key)
        if 'permissions' in r:
            permissions = r['permissions']['M']
            if 'govblock' in permissions:
                self.logger.info('govblock')
                return
        if 'api' in r:
            ts = int(r['api']['M']['ts']['S'])
            if 'checked' in r['api']['M']:
                checked = int(r['api']['M']['checked']['S'])
            else:
                checked = 0
            last_time = datetime.datetime.fromtimestamp(max(ts, checked))
            ago = now - last_time
            self.logger.info('Last time %s, now %s, time passed %s', last_time, now, ago)
            if ago < _1d:
                self.logger.info('Less than one day, skipping')
                return

            sittings = r['api']['M']['sittings']
            sittings = self.dynamo_to_list_of_maps(sittings)
            verdicts = r['api']['M']['verdicts']
            verdicts = self.dynamo_to_list_of_maps(verdicts)
            decisions = r['api']['M']['decisions']
            decisions = self.dynamo_to_list_of_maps(decisions)
            case = r['api']['M']['case']
            case = self.dynamo_to_map(case)
            caseId = case['CaseID']

            nhc = self.get_nhc()
            new_sittings = nhc.get_sittings(case)
            new_verdicts = nhc.get_verdicts(case)
            new_decisions = nhc.get_decisions(case)

            diff = Diff()
            sittings_changed  = diff.has_changed(sittings, new_sittings, 'sittings')
            verdicts_changed  = diff.has_changed(verdicts, new_verdicts, 'verdicts')
            decisions_changed = diff.has_changed(decisions, new_decisions, 'decisions')

            new_ts = int(time.time())
            dynamo_new_ts = {'S': str(new_ts)}


            old_dt = datetime.datetime.fromtimestamp(ts)
            new_dt = datetime.datetime.fromtimestamp(new_ts)
            self.logger.info('Updating ts from %s to %s [%s]', old_dt, new_dt, new_ts)

            update_expr = ['set #api.#checked=:checked']
            update_values = {':checked': dynamo_new_ts}
            update_names = {'#api': 'api', '#checked': 'checked'}

            something_changed = False

            if sittings_changed:
                something_changed = True
                diff.copy_extra_data(sittings, new_sittings, 'sittings')
                dynamo_new_sittings = self.list_to_dynamo(new_sittings)
                self.logger.info('Uploading sittings')
                update_expr.append('#api.#sittings=:sittings')
                update_values[':sittings'] = dynamo_new_sittings
                update_names['#sittings'] = 'sittings'
            else:
                self.logger.info('Not updating sittings')


            if decisions_changed:
                something_changed = True
                delta = diff.detect_changes(decisions, new_decisions, 'decisions')
                can_incremental = delta['can']
                if can_incremental:
                    start, end = delta['range']
                    self.logger.info('Incremental decision pdf scrape %s to %s', start, end)
                    nhc.get_pdfs(new_decisions[start:end])
                    self.upload_decisions(caseId, 'decisions', new_decisions[start:end], start)
                    diff.copy_extra_data(decisions, new_decisions, 'decisions')
                else:
                    self.logger.info('Parsing decision pdf from scratch')
                    nhc.get_pdfs(new_decisions)
                    self.upload_decisions(caseId, 'decision', new_decisions)
                dynamo_new_decisions = self.list_to_dynamo(new_decisions)
                self.logger.info('Writing decisions to dynamo')
                update_expr.append('#api.#decisions=:decisions')
                update_values[':decisions'] = dynamo_new_decisions
                update_names['#decisions'] = 'decisions'
            else:
                self.logger.info('Not updating decisions')

            if verdicts_changed:
                something_changed = True
                delta = diff.detect_changes(verdicts, new_verdicts, 'verdicts')
                can_incremental = delta['can']
                if can_incremental:
                    start, end = delta['range']
                    self.logger.info('Incremental verdict pdf scrape %s to %s', start, end)
                    nhc.get_pdfs(new_verdicts[start:end])
                    self.upload_decisions(caseId, 'verdicts', new_verdicts[start:end], start)
                    diff.copy_extra_data(verdicts, new_verdicts, 'verdicts')
                else:
                    self.logger.info('Parsing verdicts pdf from scratch')
                    nhc.get_pdfs(new_verdicts)
                    self.upload_decisions(caseId, 'verdicts', new_decisions)
                diff.copy_extra_data(verdicts, new_verdicts, 'verdicts')
                dynamo_new_verdicts = self.list_to_dynamo(new_verdicts)
                self.logger.info('Uploading verdicts')
                update_expr.append('#api.#verdicts=:verdicts')
                update_values[':verdicts'] = dynamo_new_verdicts
                update_names['#verdicts'] = 'verdicts'
            else:
                self.logger.info('Not updating verdicts')

            if something_changed:
                update_expr.append('#api.#ts=:ts')
                update_values[':ts'] = dynamo_new_ts
                update_names['#ts'] = 'ts'

            update_expr = ', '.join(update_expr)

            self.logger.info('')
            self.logger.info('Dynamo Update')
            self.logger.info('Update expr: %s', update_expr)
            for k, v in update_names.items():
                self.logger.info('Name: %s=%s', k, v)
            for k, v in update_values.items():
                self.logger.info('Value: %s', k)
                self.logger.info(v)

            dynamo = boto3factory.client('dynamodb')

            r = dynamo.update_item(
                TableName=self.master,
                Key=key,
                UpdateExpression=update_expr,
                ExpressionAttributeNames=update_names,
                ExpressionAttributeValues=update_values
            )

        status = r.get('ResponseMetadata', {}).get('HTTPStatusCode', -1)
        self.logger.info('Status %s', status)
        return

    def close(self):
        self.get_nhc().close()
        self.remove_nhc()


if __name__=='__main__':
    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger('botocore').setLevel(logging.WARN)
    logging.getLogger('urllib3').setLevel(logging.WARN)
    o=OneCase()


    o.smart_scrape({'CaseDisplayIdentifier': '67104-01-20', 'CaseType': 'n'})
    exit(0)
    o.mark_govblock({'CaseDisplayIdentifier': '46676-06-21', 'CaseType': 'n'})

    o.mark_govblock({'CaseDisplayIdentifier': '46676-06-21', 'CaseType': 'n'})
