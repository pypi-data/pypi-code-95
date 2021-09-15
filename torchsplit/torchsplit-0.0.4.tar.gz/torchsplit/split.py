import torch
from torchvision import datasets, transforms
from sklearn.model_selection import train_test_split
import numpy as np

transform_original = transforms.Compose([transforms.Resize([1024, 1024]),
                                            transforms.ToTensor()])   

# transform
# transform = transforms.Compose(
#     [transforms.ToTensor(),
#      transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))])


def print_num_classes(numpified : np.array,
                      index_list,
                      name_of_set:str = 'train',
                      return_dict:bool = False):
  
  unique_values = torch.unique(torch.tensor(numpified[index_list].tolist()), return_counts=True)
  st = "class |" + " {} |"*13
  num = "number |" + " {} |"*13
  
  class_uniques = unique_values[0].tolist()
  ret1 = st.format(*class_uniques)
  
  number_uniques = unique_values[1].tolist()
  ret2 = num.format(*number_uniques)
  if return_dict:
    return {'classes' : class_uniques, 'numbers' : number_uniques}
  else:
    print(name_of_set, ret1, ret2, sep='\n')
  
def train_test_validation_split_with_equal_classes(dataset: torch.utils.data.Dataset,
                                                   label_name: str = 'targets',
                                                   verbose:bool = False, 
                                                   batch_size: int = 16,
                                                   num_workers: int = 16,
                                                   other_split: float = 0.2, 
                                                   validation_split: float = 0.5, 
                                                   shuffle: bool = False):
  """ Generate train, test and validation datasets and dataloaders for Pytorch ImageFolder dataset. Method relies on sklearn and pytorch. 

  Args:
      root (str, optional): Location of ImageFolder dataset. Defaults to './content/Multimini-dataset'.
      transforms (transforms.Compose, optional): List of trnasforms. Defaults to transform_original.
      verbose (bool, optional): Print out the class distributions of the devided datasets. Defaults to False.
      batch_size (int, optional): Batch size of dataloaders. Defaults to 16.
      num_workers (int, optional): Number of workers for dataloaders. Defaults to 16.
      other_split (float, optional): How much to split for test and validation. Defaults to 0.2.
      validation_split (float, optional): How much to split from other_split into validation set. Defaults to 0.5.
      shuffle (bool, optional): To shuffle data for DataLoaders. Defaults to False.

  Returns:
      Tuple(Dict[str, torch.utils.data.Subset], Dict[str, torch.utils.data.DataLoader]): 
      Returns dict of split subsets and dict of split dataloaders
  """
  #trainset = datasets.ImageFolder(root=root,
  #                                transform=transforms)
  try:
    targets = dataset.__getattribute__(label_name)
  except:
    raise Exception(f"Provided dataset doesn't have .targets implemented")
  # target array
  

  # stratified split for validation
  train_idx, other_idx= train_test_split(
      np.arange(len(targets)),
      test_size=other_split,
      shuffle=True,
      stratify=targets
  )

  #targets_other = np.array(targets)[other_idx].tolist()
  #print(torch.unique(torch.tensor(np.array(targets)[other_idx].tolist()), return_counts=True))
  target_other = np.array(targets)[other_idx].tolist()
  #print(torch.unique(torch.tensor(target_other), return_counts=True))
  valid_idx, test_idx = train_test_split(
    np.arange(len(target_other)),
    test_size=validation_split,
    shuffle=True,
    stratify=target_other
  )
  
  #print(torch.unique(torch.tensor(np.array(targets)[other_idx[valid_idx]].tolist()), return_counts=True))
  
  from torch.utils.data import SubsetRandomSampler, Subset
  if (verbose):
    numpified = np.array(targets)
    print_num_classes(numpified, train_idx)
    print_num_classes(numpified, other_idx[valid_idx], name_of_set='valid')
    print_num_classes(numpified, other_idx[test_idx], name_of_set='test')

  train_sampler = SubsetRandomSampler(train_idx)
  test_sampler = SubsetRandomSampler(other_idx[test_idx])
  valid_sampler = SubsetRandomSampler(other_idx[valid_idx])

  data_dict = {'train' : Subset(dataset, train_idx), 'valid' : Subset(dataset, other_idx[valid_idx]), 'test': Subset(dataset, other_idx[valid_idx])}
  
  trainloader = torch.utils.data.DataLoader(data_dict['train'], batch_size=batch_size, num_workers=num_workers, shuffle=shuffle)
  validloader = torch.utils.data.DataLoader(data_dict['valid'], batch_size=batch_size, num_workers=num_workers, shuffle=shuffle)
  testloader = torch.utils.data.DataLoader(data_dict['test'], batch_size=batch_size, num_workers=num_workers, shuffle=shuffle)

  
  loader_dict = {'train': trainloader, 'valid': validloader, 'test':testloader}
  
  return data_dict, loader_dict