from .schema_components import (
    ebb_job_init_fields,
    ebb_job_eloqua_metadata,
    ebb_worker_task_fields,
    eloqua_cdo_record,
    eloqua_cdo_record_unique_field,
    eloqua_contact_record)

ebb = {
    "name": "EloquaBulkBatcher",
    "type": "record",
    "fields": [
        {"name": "controller_job_id", "type": "string", "default": ""},
        {"name": "controller_job_status_update", "type": "string", "default": ""},
        {"name": "job_init_fields", "type": ebb_job_init_fields},
        {"name": "job_eloqua_metadata", "type": ebb_job_eloqua_metadata},
        {"name": "worker_task_fields", "type": ebb_worker_task_fields}
    ]
}

eloqua_cdo_record_data = {
    "name": "EloquaCdoRecordData",
    "type": "record",
    "fields": [
        {"name": "eloqua_cdo_record", "type": eloqua_cdo_record}
    ]
}

eloqua_cdo_record_update_data = {
    "name": "EloquaCdoRecordUpdateData",
    "type": "record",
    "fields": [
        {"name": "eloqua_cdo_record", "type": eloqua_cdo_record},
        {"name": "eloqua_cdo_record_unique_field", "type": eloqua_cdo_record_unique_field}
    ]
}

eloqua_contact_record_data = {
    "name": "EloquaContactRecordData",
    "type": "record",
    "fields": [
        {"name": "eloqua_contact_record", "type": eloqua_contact_record}
    ]
}


eloqua_form = {
    "name": "EloquaForm",
    "type": "record",
    "fields": [
        {"name": "form_data", "type": {"type": "map", "values": "string"}, "default": "{}"}
    ]
}

post_eloqua_form = {
    "name": "PostEloquaForm",
    "type": "record",
    "fields": [
        {"name": "url", "type": "string", "doc": "Eloqua form endpoint URL", "default": "{}"},
        {"name": "form_data", "type": {"type": "map", "values": "string"}, "default": "{}"}
    ]
}