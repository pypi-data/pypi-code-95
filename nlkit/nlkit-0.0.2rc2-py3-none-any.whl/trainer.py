import logging

import torch
from torch.utils.tensorboard import SummaryWriter

from .utils import Phase


logger = logging.getLogger(__name__)


class BaseTrainer(object):
    
    def __init__(
        self, model, train_data_loader, valid_data_loader, test_data_loader, 
        lr_scheduler, optimizer, weight_init, summary_path, device, criterion,
        total_epoch, model_path, 
    ):

        logger.warning("@param: 'criterion'  will  be deprecated soon.")
        
        self.device = device

        self.model = model.to(self.device)
        
        if weight_init is not None:
            self.model.apply(weight_init)

        self.train_data_loader = train_data_loader
        self.valid_data_loader = valid_data_loader
        self.test_data_loader = test_data_loader

        self.optimizer = optimizer
        self.lr_scheduler = lr_scheduler
        self.criterion = criterion
        
        self.total_epoch = total_epoch
        self.model_path = model_path

        logger.info(
            "Trainer: Count parameters:{}".format(
                sum(p.nelement() for p in self.model.parameters()),
            ),
        )

        logger.info("Trainer: model and data initialized")

        self.global_train_step = 0
        self.global_valid_step = 0
        self.global_test_step = 0

        self.summary_writer = SummaryWriter(summary_path)

        self.metric_record_on_valid = []
        self.train_record = []
 
    def train(self, epoch):
        self.model.train()
        return self.iteration(epoch, self.train_data_loader, phase=Phase.TRAIN)

    def valid(self, epoch):
        self.model.eval()
        return self.iteration(epoch, self.valid_data_loader, phase=Phase.VALID)

    def test(self, epoch):
        self.model.eval()
        return self.iteration(epoch, self.test_data_loader, phase=Phase.TEST)
    
    def iteration(self, epoch, data_loader, phase):
        raise NotImplementedError()
       
    def get_global_step(self, phase):
        if phase is Phase.TRAIN:
            global_step = self.global_train_step
        elif phase is Phase.VALID:
            global_step = self.global_valid_step
        elif phase is Phase.TEST:
            global_step = self.global_test_step
        else:
            raise ValueError(f"invalid phase:{phase.name}")
        
        return global_step
        
    def record_step(self, phase):           
        if phase == Phase.TRAIN:
            self.global_train_step += 1
        elif phase == Phase.VALID:
            self.global_valid_step += 1
        else:
            self.global_test_step += 1
    
    def save_state_dict(self, epoch, save_to):
        output_path = save_to + ".ep{}".format(epoch)

        state_dict = {
            "model": self.model.state_dict(),
            "optimizer": self.optimizer.state_dict(),
            "lr_scheduler": self.lr_scheduler.state_dict(),
        }

        torch.save(state_dict, output_path)

        logger.info("EP:{} state dict saved to {}".format(epoch, output_path))
        return output_path

    def load_state_dict(self, load_from):
        if torch.cuda.is_available():
            state_dict = torch.load(load_from)

        else:
            state_dict = torch.load(
                load_from,
                map_location=torch.device('cpu'),
            )

        self.model.load_state_dict(state_dict["model"])
        self.optimizer.load_state_dict(state_dict["optimizer"])
        self.lr_scheduler.load_state_dict(state_dict["lr_scheduler"])

        logger.info("State dict loaded from: {}".format(load_from))

    def handle_summary(self, phase: Phase, log_info: dict):
        raise NotImplementedError()
    
    def forward_model(self, data):
        raise NotImplementedError()
     
    def start_train(self):
        # start training
        try:
            for epoch in range(self.total_epoch):
                self.train(epoch)
                self.save_state_dict(epoch, self.model_path)

                early_stop = self.valid(epoch)
                if early_stop:
                    break
                
                self.test(epoch)

            for record in self.train_record:
                logger.info(record)
                logger.info("\n")

            if early_stop:
                return early_stop

            self._callback_finish_training()
            
        except KeyboardInterrupt:
            logger.info(
                "Early stopping by KeyboardInterrupt, "
                "training record:",
            )

            for record in self.train_record:
                logger.info(record)
                logger.info("\n")
                
            self._callback_caught_exception()
            
        finally:
            
            self._callback_finally()

    def _callback_finish_training(*args, **kwargs):
        pass
    
    def _callback_caught_exception(*args, **kwargs):
        pass
    
    def _callback_finally(*args, **kwargs):
        pass
