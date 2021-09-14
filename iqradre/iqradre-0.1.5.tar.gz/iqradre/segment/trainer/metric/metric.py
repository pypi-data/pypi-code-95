import torch
import torch.nn as nn
from pytorch_lightning.metrics import Metric
from . import functional as F

class DiceLoss(Metric):
    def __init__(self, smooth=1.0, epsilon=1e-6, use_sigmoid=True, dist_sync_on_step=False):
        super().__init__(dist_sync_on_step=dist_sync_on_step)
        self.add_state("dice_loss", default=torch.tensor(0, dtype=torch.float64), dist_reduce_fx="sum")
        self.add_state("total", default=torch.tensor(0, dtype=torch.float64), dist_reduce_fx="sum")
        self.use_sigmoid = use_sigmoid
        self.epsilon = epsilon
        self.smooth = smooth

    def update(self, preds: torch.Tensor, masks: torch.Tensor):
        batch_size = preds.size(0)
        if self.use_sigmoid: preds = torch.sigmoid(preds)
        for idx in range(batch_size):
            dice_loss = F.dice_loss(preds[idx], masks[idx], smooth=self.smooth, epsilon=self.epsilon)
            self.dice_loss += dice_loss
        self.total += batch_size
        
    def compute(self):
        return self.dice_loss.float() / self.total 
    
    
class DiceCoeff(Metric):
    def __init__(self, smooth=1.0, epsilon=1e-6, use_sigmoid=True, dist_sync_on_step=False):
        super().__init__(dist_sync_on_step=dist_sync_on_step)
        self.add_state("dice_coeff", default=torch.tensor(0, dtype=torch.float64), dist_reduce_fx="sum")
        self.add_state("total", default=torch.tensor(0, dtype=torch.float64), dist_reduce_fx="sum")
        self.use_sigmoid = use_sigmoid
        self.epsilon = epsilon
        self.smooth = smooth

    def update(self, preds: torch.Tensor, masks: torch.Tensor):
        batch_size = preds.size(0)
        if self.use_sigmoid: preds = torch.sigmoid(preds)
        for idx in range(batch_size):
            dice_coeff = F.dice_coeff(preds[idx], masks[idx], smooth=self.smooth, epsilon=self.epsilon)
            self.dice_coeff += dice_coeff
        self.total += batch_size
        
    def compute(self):
        return self.dice_coeff / self.total 

    
class JaccardLoss(Metric):
    def __init__(self, smooth=1.0, use_sigmoid=True, dist_sync_on_step=False):
        super().__init__(dist_sync_on_step=dist_sync_on_step)
        self.add_state("jaccard_loss", default=torch.tensor(0, dtype=torch.float64), dist_reduce_fx="sum")
        self.add_state("total", default=torch.tensor(0, dtype=torch.float64), dist_reduce_fx="sum")
        self.use_sigmoid = use_sigmoid
        self.smooth = smooth
        
    def update(self, preds: torch.Tensor, masks: torch.Tensor):
        batch_size = preds.size(0)
        if self.use_sigmoid: preds = torch.sigmoid(preds)
        for idx in range(batch_size):
            jaccard = F.jaccard_loss(preds, masks, smooth=self.smooth)
            self.jaccard_loss += jaccard
        self.total += batch_size
        
    def compute(self):
        return self.jaccard_loss.float() / self.total 
    
    

class JaccardCoeff(Metric):
    def __init__(self, smooth=1.0, use_sigmoid=True, dist_sync_on_step=False):
        super().__init__(dist_sync_on_step=dist_sync_on_step)
        self.add_state("jaccard_coeff", default=torch.tensor(0, dtype=torch.float64), dist_reduce_fx="sum")
        self.add_state("total", default=torch.tensor(0, dtype=torch.float64), dist_reduce_fx="sum")
        self.use_sigmoid = use_sigmoid
        self.smooth = smooth
        
    def update(self, preds: torch.Tensor, masks: torch.Tensor):
        batch_size = preds.size(0)
        if self.use_sigmoid: preds = torch.sigmoid(preds)
        for idx in range(batch_size):
            jaccard_coeff = F.jaccard_coeff(preds, masks, smooth=self.smooth)
            self.jaccard_coeff += jaccard_coeff
        self.total += batch_size
        
    def compute(self):
        return self.jaccard_coeff.float() / self.total 
    


  