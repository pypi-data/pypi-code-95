import torch
import torch.nn as nn
import torch.optim as optim
import pytorch_lightning as pl
from pytorch_lightning import loggers as pl_loggers
from pytorch_lightning.metrics import Accuracy
from . import metric


class TaskUNet(pl.LightningModule):
    def __init__(self, model, lr=0.005):
        super().__init__()
        self.model = model
        self.criterion = nn.BCEWithLogitsLoss()
        
        self.train_dice_loss = metric.DiceLoss()
        self.train_dice_coeff = metric.DiceCoeff()
        self.train_jaccard_loss = metric.JaccardLoss()
        self.train_jaccard_coeff = metric.JaccardCoeff()
        
        self.valid_dice_loss = metric.DiceLoss()
        self.valid_dice_coeff = metric.DiceCoeff()
        self.valid_jaccard_loss = metric.JaccardLoss()
        self.valid_jaccard_coeff = metric.JaccardCoeff()
        
        self.learning_rate = lr
        
    
    def forward(self, imgs):
        output = self.model(imgs)
        return output

    def backward(self, loss, optimizer, optimizer_idx):
        loss.backward()
        
    def shared_step(self, batch, batch_idx):
        images, masks = batch
        output = self.model(images)
        loss = self.criterion(output, masks)
        return loss, output, masks
        
    def training_step(self, batch, batch_idx):
        loss, output, mask = self.shared_step(batch, batch_idx)
        dice_loss = self.train_dice_loss(output, mask)
        dice_coeff = self.train_dice_coeff(output, mask)
        jaccard_loss = self.train_jaccard_loss(output, mask)
        jaccard_coeff = self.train_jaccard_coeff(output, mask)
        
        self.log('trn_loss_step', loss, prog_bar=True, logger=True)
        self.log('trn_dice_loss_step', dice_loss,  prog_bar=True, logger=True)
        self.log('trn_dice_coeff_step', dice_coeff,  prog_bar=True, logger=True)
        self.log('trn_jaccard_loss_step', jaccard_loss,  prog_bar=True, logger=True)
        self.log('trn_jaccard_coeff_step', jaccard_coeff,  prog_bar=True, logger=True)
        
        return loss
    
    def training_epoch_end(self, outs):
        self.log('trn_dice_loss_epoch', self.train_dice_loss.compute(), logger=True)
        self.log('trn_dice_coeff_epoch', self.train_dice_coeff.compute(), logger=True)
        self.log('trn_jaccard_loss_epoch', self.train_jaccard_loss.compute(), logger=True)
        self.log('trn_jaccard_coeff_epoch', self.train_jaccard_coeff.compute(), logger=True)
    
    def validation_step(self, batch, batch_idx):
        loss, output, mask = self.shared_step(batch, batch_idx)
        dice_loss = self.valid_dice_loss(output, mask)
        dice_coeff = self.valid_dice_coeff(output, mask)
        jaccard_loss = self.valid_jaccard_loss(output, mask)
        jaccard_coeff = self.valid_jaccard_coeff(output, mask)
        
        self.log('val_loss_step', loss, prog_bar=True, logger=True)
        self.log('val_dice_loss_step', dice_loss,  prog_bar=True, logger=True)
        self.log('val_dice_coeff_step', dice_coeff,  prog_bar=True, logger=True)
        self.log('val_jaccard_loss_step', jaccard_loss,  prog_bar=True, logger=True)
        self.log('val_jaccard_coeff_step', jaccard_coeff,  prog_bar=True, logger=True)
        return loss
    
    def validation_epoch_end(self, outs):
        self.log('val_dice_loss_epoch', self.valid_dice_loss.compute(), logger=True)
        self.log('val_dice_coeff_epoch', self.valid_dice_coeff.compute(), logger=True)
        self.log('val_jaccard_loss_epoch', self.valid_jaccard_loss.compute(), logger=True)
        self.log('val_jaccard_coeff_epoch', self.valid_jaccard_coeff.compute(), logger=True)
        
    def configure_optimizers(self):
        optimizer = optim.Adam(self.model.parameters(), lr=self.learning_rate)
        return optimizer