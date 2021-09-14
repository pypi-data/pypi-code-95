import time, requests, os, json
import oss2
from dg_ai_platform.utils import get_b64_md5

SERVER_URL = "http://app-dev.bigwinepot.com:8801"
PULL_TASK =  SERVER_URL + "/Caldron/task/getTask"
UPDATE_TASK = SERVER_URL + "/Caldron/task/updateTask"
COMMIT_TASK = SERVER_URL + "/Caldron/task/finishTask"
GET_CONF = SERVER_URL + "/Caldron/task/signedUrl"

STATE_DOWNLOAD_DONE = 1
STATE_INFERENCE_DONE = 2
STATE_TASK_DONE = 7

class ITaskProcess:
    def inference(self, input_list, output_list, options=None):
        raise RuntimeError('You need overwrite inference function')

class CaldronAI:
    def __init__(self, task_class, pid, public_key, output_dir='output'):
        self.pid = pid
        self.p_key = public_key
        self.output_dir = output_dir
        self.temp_dir = '.dg_ai_temp'
        if not os.path.exists(self.output_dir):
            os.mkdir(self.output_dir)
        if not os.path.exists(self.temp_dir):
            os.mkdir(self.temp_dir)
        # func = getattr(task_obj, 'inference')
        # if func == None:
        #     raise RuntimeError('Class must be have a function with name inference')
        # else:
        #     self.task_obj = task_obj
        if task_class:
            if issubclass(task_class, ITaskProcess):
                self.task_obj = task_class()
            else:
                raise RuntimeError('Class must be implementation ITaskProcess')
        anonymous_auth = oss2.AnonymousAuth()
        self.host = 'https://oss-cn-zhangjiakou.aliyuncs.com'
        self.bucket_name = 'openapi-ai'
        self.bucket = oss2.Bucket(anonymous_auth, self.host, self.bucket_name)
        self.host_url = self.host.replace('https://', f'https://{self.bucket_name}.')

    def run(self):
        while True:
            self.pull_task()
            time.sleep(5)

    def pull_task(self):
        b64, md5_s = get_b64_md5(PULL_TASK, None, self.p_key)
        headers = {"token":self.pid, "md5":md5_s}
        try:
            response = requests.post(PULL_TASK, data=b64, headers=headers)
            task_data = response.json()
            # print(task_data)
            if ('code' in task_data) and (task_data['code'] != -1) and (task_data['code'] != 1):
                input_list = task_data['data']['inputs']
                task_id = task_data['data']['id']
                options = task_data['data']['options']
                self.file_download(task_id, input_list)
                output_types = task_data['data']['output_types']
                output_num = len(output_types)
                output_list = []
                local_input_list = self.get_input_local(task_id, input_list)
                d_outputs = None
                for i in range(output_num):
                    if output_types[i] == '1':
                        output_types[i] = 'jpg'
                    elif output_types[i] == '2':
                        output_types[i] = 'mp4'
                    elif output_types[i] == '3':
                        output_types[i] = 'mp3'
                    elif output_types[i] == '4':
                        output_types[i] = 'txt'
                    output_fn = os.path.join(self.output_dir, f"{task_id}_{i}.{output_types[i]}")
                    output_list.append(output_fn)
                try:
                    d_outputs = self.task_obj.inference(local_input_list, output_list, options)
                except Exception as e:
                    print('inference exception:', e)
                self.update_task_state(task_id, STATE_INFERENCE_DONE)
                try:
                    if d_outputs is not None:
                        output_list.extend(d_outputs)
                    output_urls = self.file_upload(output_list)
                    self.clean_local_cache(local_input_list, output_list)
                    self.task_done(task_id, output_urls)
                except Exception as e:
                    print("upload state error:", e)
            else:
                print('no task')
        except ConnectionError as e:
            print('ConnectionError:', e)
        except json.decoder.JSONDecodeError as e:
            print("JSONDecodeError:", e)

    def file_download(self, id, inputs):
        try:
            for fn, i in zip(inputs, range(len(inputs)) ):
                fn = fn["url"]
                ext = os.path.splitext(fn)[1]
                local_fn = os.path.join(self.temp_dir, f"{id}_{i}{ext}")
                if not os.path.exists(local_fn):
                    print('download file:', fn, local_fn)
                    req = requests.get(fn)
                    with open(local_fn, 'wb') as file:
                        file.write(req.content)
                else:
                    print('file was exists')
            self.update_task_state(id, STATE_DOWNLOAD_DONE)
        except Exception as e:
            print(e)

    def file_upload(self, outputs):
        keys = []
        for fn in outputs:
            keys.append(f'{os.path.basename(fn)}')
        # p_data = {"pid": self.pid, "filenames":keys}
        p_data = {"url":keys}
        # b64 = get_b64(json.dumps(p_data))
        b64, md5_s = get_b64_md5(GET_CONF, p_data, self.p_key)
        headers = {"token":self.pid, "md5":md5_s}
        response = requests.post(GET_CONF, data=b64, headers=headers)
        sign_urls = response.json()['data']
        file_urls = []
        for fn, sign_url in zip(outputs, sign_urls):
            server_url = sign_url[:sign_url.rfind('?')]
            print('upload to cloud', fn, '-->', server_url)
            try:
                # self.bucket.put_object_from_file(target_path, fn)
                self.bucket.put_object_with_url_from_file(sign_url, fn)
                # if (self.bucket.object_exists(target_path)):
                file_urls.append(server_url)
            except Exception as e:
                print('upload error:', e)
        if len(file_urls) != len(outputs):
            raise RuntimeError('Some file upload failed.')
        return file_urls

    def clean_local_cache(self, local_inputs, outputs):
        print('clean local files')
        for fn in local_inputs:
            if os.path.exists(fn):
                os.remove(fn)
        for fn in outputs:
            if os.path.exists(fn):
                os.remove(fn)

    def get_input_local(self, id, inputs):
        local_inputs = []
        try:
            for fn, i in zip(inputs, range(len(inputs))):
                fn = fn["url"]
                ext = os.path.splitext(fn)[1]
                local_inputs.append( os.path.join(self.temp_dir, f"{id}_{i}{ext}") )
        except Exception as e:
            print("get_input_local: ", e)
        return local_inputs

    def update_task_state(self, task_id, state_code):
        p_data = {"id": task_id, "status":state_code}
        b64, md5_s = get_b64_md5(UPDATE_TASK, p_data, self.p_key)
        headers = {"token":self.pid, "md5":md5_s}
        try:
            response = requests.post(UPDATE_TASK, data=b64, headers=headers)
            result_code = response.text
            print("update_task_state:", result_code)
        except Exception as e:
            print(e)

    def task_done(self, task_id, output_urls):
        print('task_done:', output_urls)
        # p_data = {"pid":self.pid, "taskid": task_id, "phase":STATE_TASK_DONE, "output_url": output_urls }
        p_data = {"id": task_id, "status":STATE_TASK_DONE, "url": output_urls }
        # b64 = get_b64(json.dumps(p_data))
        b64, md5_s = get_b64_md5(COMMIT_TASK, p_data, self.p_key)
        headers = {"token": self.pid, "md5": md5_s}
        try:
            response = requests.post(COMMIT_TASK, data=b64, headers=headers)
            result_code = response.text
            print(result_code)
        except Exception as e:
            print(e)