import cnvrg.helpers.libs_helper as libs_helper
from keras.callbacks import Callback
from cnvrg.modules.experiment import Experiment
class CnvrgKerasCallback(Callback):
    def __init__(self):
        self.experiment = Experiment()
        super(CnvrgKerasCallback, self).__init__()

    def on_epoch_begin(self, epoch=None, logs=None):
        self.experiment.log("Train began")
        self.losses = []

    def on_epoch_end(self, epoch=None, logs=None):
        xs = []
        ys = []
        grouping = []
        for group, value in logs.items():
            if group == 'epoch': continue
            grouping.append(group)
            ys.append(value)
            xs.append(epoch)
        self.experiment.log_metric("Train", ys, xs, grouping)
        print("Sending cnvrg logs", logs)
        self.losses = []


    def on_batch_begin(self, batch, logs=None):
        self.losses.append(logs.get('loss'))


    def on_batch_end(self, batch, logs=None):
        self.losses.append(logs.get('loss'))

    def on_train_begin(self, logs=None):
        print(logs)

    def on_train_end(self, logs=None):
        print(logs)