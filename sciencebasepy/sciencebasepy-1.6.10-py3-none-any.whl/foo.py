from sciencebasepy import SbSession
from io import StringIO
import json

def upload_as_file_and_upsert_item(sb, item, contents, filename, scrape_file=True):
    url = sb._base_upload_file_url
    files =  {'file': (filename, StringIO(contents))}
    data = {'item': json.dumps(item)}
    params = {} if scrape_file is True else {'scrapeFile':'false'}
    if 'id' in item and item['id']:
        data['id'] = item['id']
    ret = sb._session.post(url, params=params, files=files, data=data)
    return sb._get_json(ret)

sb = SbSession().loginc("jllong@usgs.gov")
item = sb.create_item({
    "title": "String as File Test",
    "parentId": sb.get_my_items_id()
})

print(upload_as_file_and_upsert_item(sb, item, json.dumps({"test": "Test JSON"}), "test.json"))