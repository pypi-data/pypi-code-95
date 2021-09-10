import os
import torch as pt
import torch.distributed as dist
from torch.nn.parallel import DistributedDataParallel
from kaen.osds import BaseObjectStorageDataset

def get_worker_rank():
	rank = int(os.environ['KAEN_RANK'])	\
						if 'KAEN_RANK' in os.environ \
						else 0
	return rank

def get_num_replicas():
	replicas = int(os.environ['KAEN_WORLD_SIZE']) \
							if 'KAEN_WORLD_SIZE' in os.environ \
							else 1
	return replicas

def init_process_group(model, device_ids = [], init_method = "env://"):
	#pytorch distributed training requires MASTER_ADDR and MASTER_PORT to be set
	os.environ['MASTER_ADDR'] = os.environ['KAEN_JOB_MANAGER_IP'] \
			if 'KAEN_JOB_MANAGER_IP' in os.environ \
			else "127.0.0.1"    
	MASTER_ADDR = os.environ['MASTER_ADDR']
	
	os.environ['MASTER_PORT'] = os.environ['MASTER_PORT'] \
			if 'MASTER_PORT' in os.environ \
			else "12355"    
	MASTER_PORT = os.environ['MASTER_PORT']

	BACKEND = os.environ['KAEN_BACKEND'] \
			if 'KAEN_BACKEND' in os.environ \
			else "gloo"		
	RANK = get_worker_rank()
	WORLD_SIZE = get_num_replicas()
	if not dist.is_initialized():
			dist.init_process_group(init_method = init_method, 
															backend = BACKEND,                                     
															rank = RANK, 
															world_size = WORLD_SIZE)        
			model = DistributedDataParallel(model, device_ids=device_ids)


class ObjectStorageDataset(BaseObjectStorageDataset, pt.utils.data.IterableDataset):
	def __iter__(self):        		
		it = BaseObjectStorageDataset.__iter__(self)
		val = next(it)

		while val is not None:
			try:
				numpy_array = val._get_numeric_data().values

				pt_tensor = pt.from_numpy(numpy_array)        
				yield pt_tensor
				val = next(it)
			except ValueError as err:
				raise ValueError(f"Failed data type conversion, use header='infer' or header = True if the dataset has a header:  {err}")