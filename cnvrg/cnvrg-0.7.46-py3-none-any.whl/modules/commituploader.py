from cnvrg.modules.base_module import CnvrgBase
from cnvrg.helpers.parallel_helper import safe_parallel
from cnvrg.helpers.status_helpers import CommitStatus
import cnvrg.helpers.files_helper as files_helper
import cnvrg.helpers.apis_helper as apis_helper
from typing import Dict
from threading import Thread
import os
import time


class CommitUploader(CnvrgBase):
    def __init__(self, storage, status: Dict):
        self.storage = storage
        self.element = storage.element
        self.sha1 = None
        self.status = status
        self.added_files = []
        self.saved_files = []
        self.finish_adding = False
        self.finish_saving = False


    def __base_url(self):
        return os.path.join(self.element.get_base_url(), "commits", self.sha1)


    def start_commit(self, force=False, new_branch=False):
        self.sha1 = self.element.start_commit(force=force, new_branch=new_branch)


    def upload_files(self):
        ## init
        delete_thread = Thread(target=self.__delete_files_thread)
        upload_thread = Thread(target=self.__upload_files_thread)
        ## start
        delete_thread.start()
        upload_thread.start()
        ## join
        delete_thread.join()
        upload_thread.join()


    def end_commit(self):
        self.element.end_commit(sha1=self.sha1)

    def __upload_files_thread(self):
        add_files = Thread(target=self.__add_files_thread)
        add_files.run()
        save_files = Thread(target=self.__save_files_thread)
        save_files.run()
        safe_parallel(func=self.storage.upload_file, list=self.__upload_files_gen, progressbar={"total": len(self.files_to_upload()), "desc": "uploading files"})
        add_files.join()
        self.finish_saving = True
        save_files.join()


    def __upload_files_gen(self, chunk_size=1000):
        while True:
            if len(self.added_files) == 0 and self.finish_adding:
                break
            to_add = self.added_files[:chunk_size]
            self.added_files = self.added_files[chunk_size:]
            yield to_add
            self.saved_files.extend(to_add)

    def files_to_upload(self):
        return self.status[CommitStatus.UPDATED_ON_LOCAL]

    def __add_files_thread(self, chunk_size=1000):
        files_to_add = self.files_to_upload()
        for i in range(0, len(files_to_add), chunk_size):
            files = files_to_add[i:i+chunk_size]
            added_files = self._add_files_call(files)
            self.added_files.extend(added_files)
        self.finish_adding = True


    def _add_files_call(self, files):
        mapped_files = list(map(self.__map_file, files))
        resp = apis_helper.post(os.path.join(self.__base_url(), 'add'), data={"files": mapped_files})
        return resp.get('blobs')

    def __map_file(self,file):
        return files_helper.get_file_props(file, self.element.working_dir)


    def __save_file_call(self, files):
        apis_helper.post(os.path.join(self.__base_url(), 'save'), data={"files": files})

    def __save_files_thread(self, chunk_size=1000):
        while True:
            if self.finish_saving and len(self.saved_files) == 0:
                break
            elif len(self.saved_files) == 0:
                time.sleep(5)
            to_save = self.saved_files[:chunk_size]
            self.__save_file_call(to_save)
            self.saved_files = self.saved_files[chunk_size:]

    def __delete_files_call(self, files):
        apis_helper.post(os.path.join(self.__base_url(), 'delete'), data={"files": files})

    def __delete_files_thread(self, chunk_size=1000):
        files_to_delete = self.status[CommitStatus.DELETED_ON_LOCAL]
        for i in range(0, len(files_to_delete), chunk_size):
            self.__delete_files_call(files_to_delete[i:i+chunk_size])





