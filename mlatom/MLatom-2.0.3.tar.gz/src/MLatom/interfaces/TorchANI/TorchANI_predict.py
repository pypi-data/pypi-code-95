import torch
import torchani
import os
import math
import torch.utils.tensorboard
import tqdm
import numpy as np
import h5py

def predict(args):
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    species_order = sorted(set(args.atype), key=lambda x: args.atype.index(x))
    energyOffset = 0

    # if args.mlmodeltype.lower() == 'ani1x':
    #     model = torchani.models.ANI1x(periodic_table_index=True).to(device)
    # elif args.mlmodeltype.lower() == 'ani1ccx':
    #     model = torchani.models.ANI1ccx(periodic_table_index=True).to(device)
    # elif args.mlmodeltype.lower() == 'ani2x':
    #     model = torchani.models.ANI2x(periodic_table_index=True).to(device)
    if False:
        pass
    else:
        best_model = torch.load(args.mlmodelin)

        Rcr = best_model['args']['Rcr']
        Rca = best_model['args']['Rca']
        EtaR = best_model['args']['EtaR'].to(device)
        ShfR = best_model['args']['ShfR'].to(device)
        Zeta = best_model['args']['Zeta'].to(device)
        ShfZ = best_model['args']['ShfZ'].to(device)
        EtaA = best_model['args']['EtaA'].to(device)
        ShfA = best_model['args']['ShfA'].to(device)


        num_species = len(species_order)

        self_energies=best_model['args']['self_energies']
        energyOffset=best_model['args']['energyOffset']

        aev_computer = torchani.AEVComputer(Rcr, Rca, EtaR, ShfR, EtaA, Zeta, ShfA, ShfZ, num_species)
        aev_dim = aev_computer.aev_length
        networkdic = best_model['network']

        nn = torchani.ANIModel([networkdic[specie] for specie in species_order])
        nn.load_state_dict(best_model['nn'])
        
        model = torchani.nn.Sequential(aev_computer, nn).to(device)
    model.eval()

    batch_size = args.ani.batch_size
                
    if args.setname: args.setname='_'+args.setname
    testfile=h5py.File('ANI'+args.setname+'.h5','r')
    test=testfile.get('dataset').get('molecule')
    all_coordinates=torch.tensor(test.get('coordinates')[()]).to(device).float()

    with open(args.yestfile,'wb') as fy,  open(args.ygradxyzestfile,'wb') as fgrad:
        for i in range(math.ceil(len(all_coordinates)/batch_size)):
            coordinates=all_coordinates[batch_size*i:min(batch_size*(i+1),len(all_coordinates))].requires_grad_(True)

            species=test.get('species')[()]
            species=torch.tensor([[species_order.index(i.decode('ascii')) for i in species] for j in range(len(coordinates))]).to(device)

            _, predicted_energies = model((species, coordinates))
            predicted_forces = -torch.autograd.grad(predicted_energies.sum(), coordinates, create_graph=True, retain_graph=True)[0]
            if args.ygradxyzfile: 
                predicted_energies = np.array(predicted_energies.cpu().detach().numpy()).reshape(-1,1)+energyOffset
                predicted_forces = np.array(predicted_forces.cpu().detach().numpy()).reshape(-1, args.natom, 3)
            else: 
                predicted_energies = np.array(predicted_energies.cpu().detach().numpy()).reshape(-1,1)+energyOffset
                predicted_forces = np.array(predicted_forces.cpu().detach().numpy()).reshape(-1, args.natom, 3)
                        
            np.savetxt(fy, predicted_energies, fmt='%20.12f', delimiter=" ")
            line="%d\n\n" % args.natom
            for force in predicted_forces:
                fgrad.write(line.encode('utf-8'))
                np.savetxt(fgrad, -1*force, fmt='%20.12f', delimiter=" ")
                
    import time
    time.sleep(0.0000001) # Sometimes program hangs without no reason, adding short sleep time helps to exit this module without a problem / P.O.D., 2021-02-17
