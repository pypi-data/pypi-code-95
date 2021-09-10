import torch
import torchani
import os
import sys
import math
import torch.utils.tensorboard
import tqdm
import numpy as np

def train(args):

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print('Training with %s'% device)

    Rcr = args.ani.Rcr
    Rca = args.ani.Rca
    EtaR = args.ani.EtaR.to(device)
    ShfR = args.ani.ShfR.to(device)
    Zeta = args.ani.Zeta.to(device)
    ShfZ = args.ani.ShfZ.to(device)
    EtaA = args.ani.EtaA.to(device)
    ShfA = args.ani.ShfA.to(device)



    max_epochs = args.ani.max_epochs
    early_stopping_learning_rate = args.ani.early_stopping_learning_rate
    if args.ygradxyzfile:
        force_coefficient = args.ani.force_coefficient
    best_model_checkpoint = args.mlmodelout 


    species_order = sorted(set(args.atype), key=lambda x: args.atype.index(x))
    num_species = len(species_order)
    energy_shifter = torchani.utils.EnergyShifter(None)


    trainfile = 'ANI_subtrain.h5'
    validaefile = 'ANI_validate.h5'

    batch_size = args.ani.batch_size
    if args.ygradxyzfile:
        training = torchani.data.load(trainfile, additional_properties=('forces',)).subtract_self_energies(energy_shifter, species_order).species_to_indices(species_order).shuffle()
        energyOffset=sum([np.array(energy_shifter.self_energies)[species_order.index(i)] for i in args.atype])
        validation= torchani.data.load(validaefile, additional_properties=('forces',)).subtract_self_energies(energy_shifter, species_order).species_to_indices(species_order).shuffle()
    else:
        training = torchani.data.load(trainfile).subtract_self_energies(energy_shifter, species_order).species_to_indices(species_order).shuffle()
        energyOffset=sum([np.array(energy_shifter.self_energies)[species_order.index(i)] for i in args.atype])
        validation = torchani.data.load(validaefile).subtract_self_energies(energy_shifter, species_order).species_to_indices(species_order).shuffle()
    
    training = training.collate(batch_size).cache()
    validation = validation.collate(batch_size).cache()

    # print('Self atomic energies: ', energy_shifter.self_energies)
    
    energyOffset1=sum([np.array(energy_shifter.self_energies)[species_order.index(i)] for i in args.atype])

    deltaOffset=energyOffset-energyOffset1

    argdic = {'Rcr': Rcr, 'Rca': Rca, 'EtaR': EtaR, 'ShfR': ShfR, 'Zeta': Zeta, 'ShfZ': ShfZ, 'EtaA': EtaA, 'ShfA': ShfA, 'self_energies': np.array(energy_shifter.self_energies),'energyOffset':energyOffset}


    aev_computer = torchani.AEVComputer(Rcr, Rca, EtaR, ShfR, EtaA, Zeta, ShfA, ShfZ, num_species)
    aev_dim = aev_computer.aev_length
    networkdic ={}
    for i, specie in enumerate(species_order):
        networkdic[specie] = torch.nn.Sequential(
            torch.nn.Linear(aev_dim, int(args.ani.Neuron_l1[i])),
            torch.nn.CELU(0.1),
            torch.nn.Linear(int(args.ani.Neuron_l1[i]), int(args.ani.Neuron_l2[i])),
            torch.nn.CELU(0.1),
            torch.nn.Linear(int(args.ani.Neuron_l2[i]), int(args.ani.Neuron_l3[i])),
            torch.nn.CELU(0.1),
            torch.nn.Linear(int(args.ani.Neuron_l3[i]), 1)
        )
    nn = torchani.ANIModel([networkdic[specie] for specie in species_order])

    def init_params(m):
        if isinstance(m, torch.nn.Linear):
            torch.nn.init.kaiming_normal_(m.weight, a=1.0)
            torch.nn.init.zeros_(m.bias)

    nn.apply(init_params)
    
    print('batch_size: %s' % batch_size)

    print('Neural Network Structure:\n', nn)


    model = torchani.nn.Sequential(aev_computer, nn).to(device)

    wlist2d = [
        [
            {'params': [networkdic[specie][0].weight]},
            {'params': [networkdic[specie][2].weight], 'weight_decay': 0.00001},
            {'params': [networkdic[specie][4].weight], 'weight_decay': 0.000001},
            {'params': [networkdic[specie][6].weight]},
        ]
        for specie in species_order
    ]

    AdamW = torch.optim.AdamW([i for j in wlist2d for i in j])

    blist2d = [
        [
            {'params': [networkdic[specie][0].bias]},
            {'params': [networkdic[specie][2].bias]},
            {'params': [networkdic[specie][4].bias]},
            {'params': [networkdic[specie][6].bias]},
        ]
        for specie in species_order
    ]

    SGD = torch.optim.SGD([i for j in blist2d for i in j], lr=1e-3)
  
    AdamW_scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(AdamW, factor=args.ani.lrfactor, patience=args.ani.patience, threshold=0)
    SGD_scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(SGD, factor=args.ani.lrfactor, patience=args.ani.patience, threshold=0)    

    latest_checkpoint = 'latest.pt'

    if os.path.isfile(latest_checkpoint):
        checkpoint = torch.load(latest_checkpoint)
        nn.load_state_dict(checkpoint['nn'])
        AdamW.load_state_dict(checkpoint['AdamW'])
        SGD.load_state_dict(checkpoint['SGD'])
        AdamW_scheduler.load_state_dict(checkpoint['AdamW_scheduler'])
        SGD_scheduler.load_state_dict(checkpoint['SGD_scheduler'])

    def validate():
        # run validation
        mse_sum = torch.nn.MSELoss(reduction='sum')
        total_mse = 0.0
        count = 0
        for properties in validation:
            species = properties['species'].to(device)
            coordinates = properties['coordinates'].to(device).float()
            true_energies = properties['energies'].to(device).float()
            _, predicted_energies = model((species, coordinates))
            # print(true_energies-deltaOffset,'\n\n',predicted_energies)
            total_mse += mse_sum(predicted_energies, true_energies-deltaOffset).item()
            count += predicted_energies.shape[0]
        return math.sqrt(total_mse / count)

    tensorboard = torch.utils.tensorboard.SummaryWriter()

    mse = torch.nn.MSELoss(reduction='none')

    print("training starting from epoch", AdamW_scheduler.last_epoch + 1)

    for _ in range(AdamW_scheduler.last_epoch + 1, max_epochs):
        rmse = validate()
        print('RMSE:', rmse, 'at epoch', AdamW_scheduler.last_epoch + 1)
        sys.stdout.flush()

        learning_rate = AdamW.param_groups[0]['lr']
        print('learning_rate:',learning_rate)

        if learning_rate < early_stopping_learning_rate:
            break

        if AdamW_scheduler.is_better(rmse, AdamW_scheduler.best):
            torch.save(
                {   
                    'network': networkdic,
                    'args': argdic,
                    'nn': nn.state_dict()
                }
                , best_model_checkpoint
            )
            print('best model saved')
        AdamW_scheduler.step(rmse)
        SGD_scheduler.step(rmse)

        tensorboard.add_scalar('validation_rmse', rmse, AdamW_scheduler.last_epoch)
        tensorboard.add_scalar('best_validation_rmse', AdamW_scheduler.best, AdamW_scheduler.last_epoch)
        tensorboard.add_scalar('learning_rate', learning_rate, AdamW_scheduler.last_epoch)
        for i, properties in tqdm.tqdm(
            enumerate(training),
            total=len(training),
            desc="epoch {}".format(AdamW_scheduler.last_epoch)
        ):
            species = properties['species'].to(device)

            if args.ygradxyzfile: 
                coordinates = properties['coordinates'].to(device).float().requires_grad_(True)
                true_energies = properties['energies'].to(device).float()
                true_forces = properties['forces'].to(device).float()
                num_atoms = (species >= 0).sum(dim=1, dtype=true_energies.dtype)
                _, predicted_energies = model((species, coordinates))
                forces = -torch.autograd.grad(predicted_energies.sum(), coordinates, create_graph=True, retain_graph=True)[0]
                energy_loss = (mse(predicted_energies, true_energies) / num_atoms.sqrt()).mean()
                force_loss = (mse(true_forces, forces).sum(dim=(1, 2)) / num_atoms).mean()
                loss = energy_loss + force_coefficient * force_loss
                # print('\n\n',true_energies+energyOffset,'\n\n',predicted_energies+energyOffset)
            else:
                coordinates = properties['coordinates'].to(device).float()
                true_energies = properties['energies'].to(device).float()
                num_atoms = (species >= 0).sum(dim=1, dtype=true_energies.dtype)
                _, predicted_energies = model((species, coordinates))
                loss = (mse(predicted_energies, true_energies) / num_atoms.sqrt()).mean()

            AdamW.zero_grad()
            SGD.zero_grad()
            loss.backward()
            AdamW.step()
            SGD.step()

            tensorboard.add_scalar('batch_loss', loss, AdamW_scheduler.last_epoch * len(training) + i)

        torch.save({
            'nn': nn.state_dict(),
            'AdamW': AdamW.state_dict(),
            'SGD': SGD.state_dict(),
            'AdamW_scheduler': AdamW_scheduler.state_dict(),
            'SGD_scheduler': SGD_scheduler.state_dict(),
        }, latest_checkpoint)
        
