#!/usr/bin/env python3
TU_DATA_API_TOKEN = 'KpxGRTg8d6DMsjuYiKx81YB6bczPOFKCnN0zm27QsAhRhJxPh18NXV2fIITy'
#
# the following code demonstrates how to easily convert & upload
# a pandas dataframe by way of enijo-connector to the TU Data
# research data repository.
#

import datetime

import logging
LOGFORMAT = '%(module)s:%(lineno)d %(levelname)s: %(message)s'
logging.basicConfig(level=logging.WARNING, format=LOGFORMAT)
logger = logging.getLogger(__name__)

import enijo.connector
from enijo.connector import AT_AC_TUWIEN_RESEARCHDATA_TEST
from enijo.connector.builders import RecordNewBuilder

# create an EnijoConnector instance:
datarepo = enijo.connector.EnijoConnector()

datarepo.set_repository_url(url=AT_AC_TUWIEN_RESEARCHDATA_TEST)
datarepo.set_auth_token(token=TU_DATA_API_TOKEN)
# Http Header: f"Authorization: Bearer {TU_DATA_API_TOKEN}"


#  1) create new stand-alone draft record with properties
record_new = (RecordNewBuilder
                .with_defaults()
                .metadata()
                  .set(title="asdf hello world test")
                  .creator()
                    .person()
                      .set(given_name="test")
                      .set(family_name="py")
                      .return_up()
                    .return_up()
                  .return_up()
                .build())
draft_record = datarepo.create_draft_record(record=record_new)

#  2) add new draft file to draft record and upload file content:
draft_file = draft_record.create_draft_file(filename="my-data.csv")
draft_file.upload_content(data)

#  3) publish the draft record
record = draft_record.publish()

print("have created published record", record._record.id)
print("show in browser at url:", record._record.links.self_html)
