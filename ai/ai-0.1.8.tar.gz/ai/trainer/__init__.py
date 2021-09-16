# -*- coding: utf-8 -*-
""" ai.trainer """
import os
import logging
import random
import numpy as np
import subprocess
import time
import torch
from torch.utils.tensorboard import SummaryWriter
from multiprocessing import Queue
from ai.helper import ensure_dir


def set_seed(seed, n_gpu=1):
    os.environ['PYTHONHASHSEED'] = str(seed)
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if n_gpu > 0:
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = True


class Timer(object):
    def __init__(self):
        self.start_time = time.time()

    def now(self, n=3600):
        return (time.time() - self.start_time) / n


class GPUManager(object):
    def __init__(self, num_gpus=1):
        self.queue = Queue()
        for device_id in range(num_gpus):
            self.queue.put(device_id)

    def require(self, timeout=60*5):
        try:
            return self.queue.get(timeout=timeout)
        except:
            return None

    def add(self, device_id):
        self.queue.put(device_id)


def process(cmd_groups, shell=True):
    """ 组内并行，组间串行
    """
    try:
        for cmd_group in cmd_groups:
            ps = [subprocess.Popen(cmd, shell=shell) for cmd in cmd_group]
            for p in ps:
                p.wait()
        return True
    except:
        return False


class Pipeline():
    """ Pipeline
    """
    def __init__(self, task='pipeline', num_gpus=1, log_dir='log'):
        ensure_dir(log_dir)
        logging.basicConfig(
            format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            level=logging.INFO,
            filename=f"{log_dir}/{task}.txt",
            filemode='w'
        )
        self.logger = logging.getLogger(task)
        self.timer = Timer()
        self.gpu_manager = GPUManager(num_gpus=num_gpus)
    
    def run_on_gpu(self, cmd, max_time=80, log_file=None):
        if log_file:
            cmd = f"nohup {cmd} > {log_file} 2>&1 &"
        while True:
            if self.timer.now() >= max_time:
                self.logger.warning(f'{cmd} 超时，不执行')
                return
            device_id = self.gpu_manager.require()
            if device_id is not None:
                try:
                    cmd = f"export CUDA_VISIBLE_DEVICES={device_id} && {cmd}"
                    self.logger.info(f"{cmd} 开始")
                    os.system(cmd)
                    self.logger.info(f"{cmd} 结束")
                except:
                    self.logger.warning(f'{cmd} failed')
                self.gpu_manager.add(device_id)
                break


class FGM():
    """ emb_name 为模型中 embedding 的参数名
    """
    def __init__(self, model):
        self.model = model
        self.backup = {}

    def attack(self, epsilon=1., emb_name='word_embedding'):
        for name, param in self.model.named_parameters():
            if param.requires_grad and emb_name in name:
                self.backup[name] = param.data.clone()
                norm = torch.norm(param.grad)
                if norm != 0 and not torch.isnan(norm):
                    r_at = epsilon * param.grad / norm
                    param.data.add_(r_at)

    def restore(self, emb_name='word_embedding'):
        for name, param in self.model.named_parameters():
            if param.requires_grad and emb_name in name:
                assert name in self.backup
                param.data = self.backup[name]
        self.backup = {}


class PGD():
    """ emb_name 为模型中 embedding 的参数名
    """
    def __init__(self, model, k=3):
        self.model = model
        self.emb_backup = {}
        self.grad_backup = {}
        self.k = k

    def attack(self, epsilon=1., alpha=0.33, emb_name='word_embedding', is_first_attack=False):
        for name, param in self.model.named_parameters():
            if param.requires_grad and emb_name in name:
                if is_first_attack:
                    self.emb_backup[name] = param.data.clone()
                norm = torch.norm(param.grad)
                if norm != 0 and not torch.isnan(norm):
                    r_at = alpha * param.grad / norm
                    param.data.add_(r_at)
                    param.data = self.project(name, param.data, epsilon)

    def restore(self, emb_name='word_embedding'):
        for name, param in self.model.named_parameters():
            if param.requires_grad and emb_name in name: 
                assert name in self.emb_backup
                param.data = self.emb_backup[name]
        self.emb_backup = {}

    def project(self, param_name, param_data, epsilon):
        r = param_data - self.emb_backup[param_name]
        if torch.norm(r) > epsilon:
            r = epsilon * r / torch.norm(r)
        return param_data + r

    def backup_grad(self):
        for name, param in self.model.named_parameters():
            if param.requires_grad:
                self.grad_backup[name] = param.grad

    def restore_grad(self):
        for name, param in self.model.named_parameters():
            if param.requires_grad:
                param.grad = self.grad_backup[name]