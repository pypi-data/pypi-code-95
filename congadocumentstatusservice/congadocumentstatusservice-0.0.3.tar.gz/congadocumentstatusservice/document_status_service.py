import requests


class DocumentStatusService:

    def change_process_status(self, id, file_name: str, process_type: str, process_result: str, core_change_process_status_url: str) -> None:
        post_data = {'document_id': id, 'file_name': file_name,
                     "process_type": process_type, "process_result": process_result}
        requests.post(core_change_process_status_url, data=post_data)
