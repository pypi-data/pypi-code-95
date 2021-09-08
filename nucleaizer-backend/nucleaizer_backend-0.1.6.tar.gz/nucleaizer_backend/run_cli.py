from pathlib import Path
from .training import NucleaizerTraining; 
from . import cli_config

def main(presegment, clustering, style, train, a_nucleaizer_dir=None, a_workflow_dir=None, a_inputs_dir=None):
    if a_nucleaizer_dir is None:
        nucleaizer_dir = Path(cli_config.nucleaizer_dir)                                    # Where are the downloaded models, config files, etc.
    else:
        nucleaizer_dir = a_workflow_dir

    if a_workflow_dir is None:
        workflow_dir = Path(cli_config.workflow_dir)                                        # Where to put the intermediate results
    else:
        workflow_dir = a_workflow_dir

    if a_inputs_dir is None:
        inputs_dir = Path(cli_config.inputs_dir)                                            # The dataset directory
    else:
        inputs_dir = a_inputs_dir

    trainer = NucleaizerTraining(
        inputs_dir=str(inputs_dir),
        workflow_dir=str(workflow_dir),
        nucleaizer_dir=str(nucleaizer_dir))

    if presegment:
        trainer.copy_input()
        presegment_model = nucleaizer_dir/'mask_rcnn_presegmentation.h5'                # Use this model for presegmentation.
        presegment_config = nucleaizer_dir/'presegment.json'   # Use this config for presegmentation.
        trainer.presegment(
            model_path=str(presegment_model), 
            config_path=str(presegment_config))
        trainer.measure_cells()
        trainer.setup_db()
    
    if clustering:
        trainer.clustering()
    
    if style:
        trainer.create_style_train()
        trainer.style_transfer()

    if train:
        trainer.create_mask_rcnn_train()
        train_config = nucleaizer_dir/'train.json'                                      # Use this configuration to the training.
        initial_model = nucleaizer_dir/'mask_rcnn_coco.h5'                              # Use this model as an inital model for training
        trainer.train_maskrcnn(
            config_path=train_config, 
            initial_model=initial_model)

if __name__ == '__main__':
    main(*([True]*4))
    #main(False, False, True, False)
