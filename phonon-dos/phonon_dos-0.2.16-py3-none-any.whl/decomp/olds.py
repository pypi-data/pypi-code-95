# -*- coding: utf-8 -*-
"""
Created on Wed Oct 28 16:01:48 2020

@author: Gabriele Coiana
"""
from scipy.optimize import curve_fit
from scipy.interpolate import interp1d
from scipy import signal
import numpy as np
import os
import warnings
warnings.filterwarnings('ignore') 
from scipy.interpolate import interp1d
import matplotlib as mpl
# mpl.use('pgf')
import matplotlib.pyplot as plt
# from mpl_toolkits.mplot3d import Axes3D
import matplotlib.gridspec as gridspec
from matplotlib import animation
from scipy import interpolate

def read_phonopy(file_eigenvectors, n_atom_unit_cell):
    ## =============================================================================
    # Phonopy frequencies and eigenvectors
    data = yaml.load(open(file_eigenvectors))
    #D = data['phonon'][0]['dynamical_matrix']
    #D = np.array(D)
    #D_real, D_imag = D[:,0::2], 1j*D[:,1::2]
    #D = (D_real + D_imag)*21.49068**2#*0.964*10**(4)#
    
#    data2 = data['phonon']
#    qpoints_scaled = []
#    freqs = []
#    eigvecs = []
#    for element in data2:
#        qpoints_scaled.append(element['q-position'])
#        freq = []
#        eigvec = np.zeros((n_atom_unit_cell*3, n_atom_unit_cell*3),dtype=complex)
#        for j in range(len(element['band'])):
#            branch = element['band'][j]
#            freq.append(branch['frequency'])
#            
#            eigen = np.array(branch['eigenvector'],dtype=complex)
#            eigen_real = eigen[:,:,0]
#            eigen_imag = eigen[:,:,1]
#            eigen = eigen_real + 1j*eigen_imag
#            eigen = eigen.reshape(n_atom_unit_cell*3,)
#            eigvec[:,j] = eigen
#    
#        freqs.append(freq)
#        eigvecs.append(eigvec)
#    qpoints_scaled = np.array(qpoints_scaled)
#    freqs = np.array(freqs)
    c = 1.88973 #conversion to Bohrs
    Hk = np.array(data['reciprocal_lattice'])*2*np.pi*1/c
    distances = []
    qpoints_scaled = []
    dist = 0.0
    frequencies = []
    eigvecs = []
    for i in range(len(data['phonon'])):
        if(i==0):
            this_element = data['phonon'][i]
            this_qpoint_sc = this_element['q-position']
            dist = 0.0
            distances.append(dist)
        else:
            this_element = data['phonon'][i]
            previous_element = data['phonon'][i-1]
            this_qpoint_sc = this_element['q-position']
            previous_qpoint_sc =  previous_element['q-position']
            
            this_qpoint = np.dot(Hk,this_qpoint_sc)
            previous_qpoint = np.dot(Hk,previous_qpoint_sc)
            
            diff = this_qpoint - previous_qpoint
            
            dist = dist + np.linalg.norm(diff)
            distances.append(dist)
        
        prov = []
        eigvec = np.zeros((n_atom_unit_cell*3, n_atom_unit_cell*3),dtype=complex)
        for j in range(len(this_element['band'])):
            branch = this_element['band'][j]
            prov.append(branch['frequency'])
            eigen = np.array(branch['eigenvector'],dtype=complex)
            eigen_real = eigen[:,:,0]
            eigen_imag = eigen[:,:,1]
            eigen = eigen_real + 1j*eigen_imag
            eigen = eigen.reshape(n_atom_unit_cell*3,)
            eigvec[:,j] = eigen
            
        eigvecs.append(eigvec)
        frequencies.append(prov)
        qpoints_scaled.append(this_qpoint_sc)

    frequencies = np.array(frequencies)
    distances = np.array(distances)
    qpoints_scaled = np.array(qpoints_scaled)
    Nqpoints = len(qpoints_scaled[:,0])

    
    ks = np.dot(Hk,qpoints_scaled.T).T
    # =============================================================================
    return Nqpoints, qpoints_scaled, ks, frequencies, eigvecs, distances, Hk

def aaa_interpol_spectrum(ks_path, freq, freqs_from_spectrum, eigvecs, modes, ZQS, new_ks_in_between):
    num_ks = len(ks_path)
    num_modes = len(freqs_from_spectrum[0,:])
    num_freqs = len(ZQS[:,0,0])
    kk = np.linspace(0,1,num_ks)
    num_Gammas, indexes_Gammas, indexes_Gammas_withboundaries = find_Gammas(ks_path)
    df = freq[1] - freq[0]
    X, Y = np.meshgrid(kk,freq)
    
#    get_Force_Constants(eigvecs, freqs_from_spectrum.T)
    interp_freq = []
    INTERP = []
    for j in range(len(modes)):
        interp_freq_interm = np.array([])
        for m in range(len(indexes_Gammas)):
            this_G = indexes_Gammas_withboundaries[m]
            next_G = indexes_Gammas_withboundaries[m+1]+1
            kk_i = kk[this_G:next_G]
            f_i = freqs_from_spectrum[this_G:next_G,j]
            interp = interp1d(kk_i, f_i, 'cubic')
#            x_i = np.arange(kk_i[0], kk_i[-1], 0.001)
            INTERP.append(interp)
#            interp_freq_interm = np.concatenate((interp_freq_interm, interp(x_i)))
#        interp_freq_interm = np.array(interp_freq_interm)
#        interp_freq.append(interp_freq_interm)
#    interp_freq = np.array(interp_freq)

    ZQS_interp = np.zeros((num_freqs,num_modes, new_ks_in_between*(num_ks-1)+num_ks))
    
    
    ktot = 0
    for k in range(num_ks-1):
        sector = 0
        for l in indexes_Gammas_withboundaries[1::]:
            if(k >= l):
                sector = sector + 1
        count_k_in_between = 0
        for j in range(num_modes):  
            this_gaussian = ZQS[:,j,k]
            next_gaussian = ZQS[:,j,k+1]
            
#            import matplotlib.pyplot as plt
#            fig,ax = plt.subplots()
#            #to comment
#            popt_this, pcov_this = curve_fit(gaussian, freq, this_gaussian)
#            popt_next, pcov_next = curve_fit(gaussian, freq, next_gaussian)
            
            this_max = freqs_from_spectrum[k,j]
            next_max = freqs_from_spectrum[k+1,j]
            diff_maxima = next_max - this_max
            
            if(diff_maxima >= 0):
                this_gaussian_interp = interp1d(freq, this_gaussian, bounds_error=False, fill_value=0)
                next_gaussian_interp = interp1d(freq, next_gaussian, bounds_error=False, fill_value=0)
                this_gaussian_fit = this_gaussian_interp(freq-diff_maxima)
                next_gaussian_fit = next_gaussian_interp(freq)
                shift_interp = -next_max
            else:
                this_gaussian_interp = interp1d(freq, this_gaussian, bounds_error=False, fill_value=0)
                next_gaussian_interp = interp1d(freq, next_gaussian, bounds_error=False, fill_value=0)
                this_gaussian_fit = this_gaussian_interp(freq)
                next_gaussian_fit = next_gaussian_interp(freq+diff_maxima)
                shift_interp = -this_max
            
#            area_this_gaussian = np.trapz(this_gaussian_fit, freq)
#            area_next_gaussian = np.trapz(next_gaussian_fit, freq)

            this_k = kk[k]
            next_k = kk[k+1]
            interm_k = np.linspace(this_k, next_k, new_ks_in_between+2)[0:-1]

            interp = INTERP[sector+j*num_Gammas]
            intermediate_maxima = interp(interm_k)
            
            count_k_in_between = 0
            for m in range(new_ks_in_between+1):
                mi = intermediate_maxima[m]
                x = (interm_k[m] - interm_k[0])/(next_k-interm_k[0])
#                area_factor = area_this_gaussian+(area_next_gaussian-area_this_gaussian)*x
                interp_gaussian = this_gaussian_fit+(next_gaussian_fit-this_gaussian_fit)*x
                interp_gaussian_interp = interp1d(freq, interp_gaussian,bounds_error=False, fill_value=0)
                interp_gaussian_fit = interp_gaussian_interp(freq-(shift_interp+mi))
                ZQS_interp[:,j,ktot+count_k_in_between] = interp_gaussian_fit
                count_k_in_between = count_k_in_between + 1
                

#                popt = popt_this + (popt_next-popt_this)*x
#                interp_gaussian_fit = gaussian(freq, *popt)#1/(sig*np.sqrt(2*np.pi)) * np.exp(-.5*((freq-mi)/sig)**2) *area_factor

#                ax.plot(freq, interp_gaussian_fit, label='interp')
#            ax.plot(freq, this_gaussian, label='real this')
#            ax.plot(freq,next_gaussian, label='real next')
##            ax.plot(freq, this_gaussian_fit, label='real this fit')
##            ax.plot(freq,next_gaussian_fit, label='real next fit')
#            ax.legend()
            
        ktot = ktot + count_k_in_between
    ZQS_interp[:,:,-1] = ZQS[:,:,-1]
    return ZQS_interp

def aaa_get_real_branches(freqs, eigvecs, masses, Hk, qpoints_scaled):
    num_ks = len(freqs[0,:])
    num_branches = len(freqs[:,0])    
    
    freqs_until_now = freqs[:,0]
    indexes = np.tile(np.arange(num_branches), (2,1))
    new_indexes = np.arange(num_branches)
    for k in range(1,num_ks-1):
        kpoint = np.dot(Hk, qpoints_scaled[k])
        kpoint = kpoint/np.linalg.norm(kpoint)
        next_kpoint = np.dot(Hk, qpoints_scaled[k+1])
        if(np.allclose(next_kpoint,[0,0,0])):
            next_kpoint = [0,0,0]
        else:
            next_kpoint = next_kpoint/np.linalg.norm(next_kpoint)
#        print(k,qpoints_scaled[k], np.round(next_kpoint,2))

        this_eigvecs = eigvecs[k].T/np.sqrt(masses)*10
        next_eigvecs = eigvecs[k+1].T/np.sqrt(masses)*10
        next_eigvecs = next_eigvecs/np.linalg.norm(next_eigvecs, axis=0)

#        print(np.round(next_eigvecs[0::],2))

        temp = new_indexes#np.arange(num_branches)
        for j,l in zip(range(num_branches), new_indexes):
            eig = this_eigvecs[l,:]
            eig = eig/np.linalg.norm(eig)
#            print(l,np.round(eig,2), freqs[l,k])
            dot_prod = np.abs(np.dot(next_eigvecs,eig))
#            print(np.round(dot_prod,2))


            new_index = np.argwhere([dot_prod.max()-0.0000000000001 <= dd <= dot_prod.max() for dd in dot_prod])
            degenerate = len(new_index)
#            print(new_index)
            if (len(new_index) > 1):
#                print('two are degenerate')
#                next_eigvecs_deg = next_eigvecs[new_index,:]
#                dot_nexteigvecs_nextk = np.dot(next_eigvecs_deg.reshape(degenerate*2,3), next_kpoint)
#                dot_nexteigvecs_nextk = np.abs(dot_nexteigvecs_nextk.reshape(degenerate,2))
#                dot_nexteigvecs_nextk = dot_nexteigvecs_nextk/np.linalg.norm(dot_nexteigvecs_nextk)
#                dot_thiseig_nextk = np.abs(np.dot(eig.reshape(1*2,3), next_kpoint))
#                dot_thiseig_nextk = dot_thiseig_nextk/np.linalg.norm(dot_thiseig_nextk)
#                diff = np.abs(dot_thiseig_nextk - dot_nexteigvecs_nextk)
#                diff_sum = np.sum(diff, axis=1)
#                print(np.round(dot_nexteigvecs_nextk,2))
#                print(np.round(dot_thiseig_nextk,2))
#                print('diffsum', np.round(diff_sum,2))
                a=0
                if(a==10):#(np.isclose(dot_nexteigvecs_nextk, 1,  rtol=0.2, atol=0.2).any()):
                    #you have a longitudinal branch
                    print('theres a longitudinal')
#                    isclose = np.isclose(dot_nexteigvecs_nextk, dot_thiseig_nextk, rtol=0.2, atol=.2)
#                    true_long = np.all(isclose, axis=1)
#                    arg_long = np.argwhere(true_long)
#                    new_index = new_index[arg_long]
#                    print(new_index)
#                    
                else:
#                    c = np.argwhere(diff_sum==diff_sum.min())
                    new_index = l#new_index[c]
                    print(new_index)

                
                
            if (new_index in temp[0:j]): #it happens at Gamma where TA modes are degenerate
#                print('aaaa')
                new_index = l

            temp[j] = new_index
#            print()
        new_indexes = temp.astype(int)
#        print(new_indexes)
#        print()



        indexes = np.vstack((indexes,new_indexes))
        
    indexes = indexes.astype(int)
#    print(indexes)
    freqs_sorted = []
    for j in range(num_ks):
        freqs_sorted.append(freqs[indexes[j],j])   
        
    return indexes, np.array(freqs_sorted).T


def plot4_old(kk, frequencies, frequencies_disp, qpoints, x_labels, ZQS):
    """
    old plot 4, with mathematical interpolation
    """
    pgf_with_latex = {                      # setup matplotlib to use latex for output

    "pgf.texsystem": "pdflatex",        # change this if using xetex or lautex

    "text.usetex": True,                # use LaTeX to write all text

    "font.family": "serif",

    "font.serif": [],                   # blank entries should cause plots to inherit fonts from the document

    "font.sans-serif": [],

    "font.monospace": [],

    "axes.labelsize": 16,                # LaTeX default is 10pt font.     "text.fontsize": 10,

    "legend.fontsize": 'x-small',               # Make the legend/label fonts a little smaller

    "xtick.labelsize": 16,

    "ytick.labelsize": 16,

    "figure.figsize": figsize(1.4),       # default fig size of 0.9 textwidth

    "pgf.preamble": [

        r"\usepackage[utf8x]{inputenc}",    # use utf8 fonts becasue your computer can handle it :)

        r"\usepackage[T1]{fontenc}",        # plots will be generated using this preamble

        ]

    }

#    mpl.rcParams.update(pgf_with_latex)
    freq = ZQS[:,0] 
    fig = plt.figure()
    gs = gridspec.GridSpec(1,5, wspace=0)
    ax = fig.add_subplot(gs[0, 0:4])
    plt.xticks(kk, x_labels)
    ax2 = fig.add_subplot(gs[0, 4], sharey=ax)
    n_branches = len(frequencies[0,:,0])
    
    
    
    gamma_pos = []
    for c in range(len(qpoints)):
        qpoint = qpoints[c]
        if(np.allclose(qpoint,[0,0,0])):
            gamma_pos.append(c)
    if(gamma_pos[0] != 0):
        gamma_pos.insert(0,0)
    if(gamma_pos[-1] != len(kk)):
        gamma_pos.insert(len(kk),len(kk))
    
    
    gaussians = np.zeros(len(freq)) 
    gaussians_ft = np.zeros(len(freq))
    for j in range(3):
#        ax.scatter(kk,frequencies_disp[0,j,:], marker='x', color='black', label='0K dispersion')
#        ax.scatter(kk,frequencies[0,j,:], marker='x', color='red')
        for d in range(len(gamma_pos)-1):
            this_gamma = gamma_pos[d]
            next_gamma = gamma_pos[d+1]+1
            kk_div = kk[this_gamma:next_gamma]
            f = interpolate.interp1d(kk_div, frequencies[0,j,this_gamma:next_gamma], kind=3)
            f_disp = interpolate.interp1d(kk_div, frequencies_disp[0,j,this_gamma:next_gamma], kind=3)
            x = np.arange(kk_div.min(), kk_div.max(), 0.01)
            ax.plot(x, f(x), color='red')
            ax.plot(x, f_disp(x), color='black')
            f_gamma = interpolate.interp1d(kk_div, frequencies[1,j,this_gamma:next_gamma], kind=1)
            y1, y2 = f(x)+f_gamma(x)/2, f(x)-f_gamma(x)/2
            ax.fill_between(x, y1, y2, color='red', alpha=0.3)
            for g in range(len(x)):
                mi_disp = f_disp(x)[g]
                mi_ft = f(x)[g]
                
                if(np.isclose(mi_disp,0, rtol=0.1, atol=0.1) or np.isclose(mi_ft,0,rtol=0.1, atol=0.1)):
                    continue

                gauss = util.norm_gaussian(freq, mi_disp, .1)
                gauss_ft = util.norm_gaussian(freq,mi_ft, .1)
                gaussians = gaussians + gauss
                gaussians_ft = gaussians_ft + gauss_ft
    
    for j in range(3,n_branches):
        f = interpolate.interp1d(kk, frequencies[0,j,:], kind=3)
        f_disp = interpolate.interp1d(kk, frequencies_disp[0,j,:], kind=3)
        x = np.arange(kk.min(), kk_div.max(), 0.01)
        graph_ft, = ax.plot(x, f(x), color='red', label='finite T dispersion')
        graph_disp, = ax.plot(x, f_disp(x), color='black', label='0K dispersion')
        f_gamma = interpolate.interp1d(kk, frequencies[1,j,:], kind=1)
        y1, y2 = f(x)+f_gamma(x)/2, f(x)-f_gamma(x)/2
        ax.fill_between(x, y1, y2, color='red', alpha=0.3)
#        graph_disp = ax.scatter(kk,frequencies_disp[0,j,:], marker='x', color='black', label='0K dispersion')
#        graph_ft = ax.scatter(kk,frequencies[0,j,:], marker='x', color='red', label='finite T dispersion')
        
        for g in range(len(x)):
            mi_disp = f_disp(x)[g]
            mi_ft = f(x)[g]
            gauss = util.norm_gaussian(freq, mi_disp, 0.1)
            gauss_ft = util.norm_gaussian(freq,mi_ft, 0.1)
            gaussians = gaussians + gauss
            gaussians_ft = gaussians_ft + gauss_ft
        
    tot_DOS = np.trapz(gaussians, freq)
    tot_DOS_ft = np.trapz(gaussians_ft, freq)
    
    ax.set_ylabel('Frequency [Thz]')
    ax.tick_params(axis='both', which='major', labelsize=15, width=2 , length=6, direction='in', top=True, right=True)
    ax.axhline(0, linestyle='--', color='b')
    
#    print(np.trapz(gaussians/tot_DOS/2,freq))
#    print(np.trapz(np.sum(ZQS[:,1:], axis=1), freq))
    DOS_ft, = ax2.plot(np.sum(ZQS[:,1:], axis=1), freq, c='red', label='finite T DOS')
#    DOS_ft, = ax2.plot(gaussians_ft/tot_DOS_ft/2, freq, c='red', label='finite T DOS')
#    DOS_0K,= ax2.plot(gaussians/tot_DOS/2,freq, c='black', label = '0K DOS')
    ax2.set_xticks([])
    ax2.tick_params(axis='y', which='major', labelsize=0.001, width=2 , length=6, direction='in', top=True, right=True)
    ax2.legend()
    
    plt.rcParams['axes.linewidth'] = 2
    ax.set_xticks(kk, x_labels)
    ax.legend(handles=[graph_disp, graph_ft])
#    ax2.legend()
#    plt.show()
    fig.savefig('plot4.pdf')
    return

def plot_k2_old(f, data, data_projected, indexes,freqs, max_Z, branches, ks_path, title=''):
    pgf_with_latex = {                      # setup matplotlib to use latex for output

    "pgf.texsystem": "pdflatex",        # change this if using xetex or lautex

    "text.usetex": True,                # use LaTeX to write all text

    "font.family": "serif",

    "font.serif": [],                   # blank entries should cause plots to inherit fonts from the document

    "font.sans-serif": [],

    "font.monospace": [],

    "axes.labelsize": 16,                # LaTeX default is 10pt font.     "text.fontsize": 10,

    "legend.fontsize": 12,               # Make the legend/label fonts a little smaller

    "xtick.labelsize": 16,

    "ytick.labelsize": 16,

    "figure.figsize": figsize(1.4),       # default fig size of 0.9 textwidth

    "pgf.preamble": [

        r"\usepackage[utf8x]{inputenc}",    # use utf8 fonts becasue your computer can handle it :)

        r"\usepackage[T1]{fontenc}",        # plots will be generated using this preamble

        ]

    }

    mpl.rcParams.update(pgf_with_latex)
    num_ks = len(data_projected[0,0,:])
    tot_branches = int(len(freqs[0][0,:]))
    plt.ion()
    kk = np.linspace(0,1,num_ks)
    X, Y = np.meshgrid(kk,f)
    
    fig, ax = plt.subplots()
    
    
#    if(len(branches) == tot_branches): #plot whole spectrum
#        if(max_Z > np.max(data) or max_Z < 0.0):
#            max_Z = np.max(data)
#        print('Drawing the whole spectrum...')
#        ax.contourf(X,Y,data,100, vmax=max_Z)
#        print('finished')

    if(max_Z > np.max(data_projected) or max_Z < 0.0):
        max_Z = np.max(data_projected)
    print('Drawing branches ', branches)
    ax.contourf(X,Y,np.sum(data_projected, axis=1),100, vmax=max_Z)
    print('finished')
        
    num_Gammas, indexes_Gammas, indexes_Gammas_withboundaries = util.find_Gammas(ks_path)
    
    
    
    ax2 = plt.twinx()
    ax2.set_ylabel('[Thz]')
    num_dispersions = len(freqs)
    colours = ['black', 'red']
    graphs = [0,0]
    num_ks_commensurate = len(freqs[0][:,0])
    kk_commensurate = np.linspace(0,1,num_ks_commensurate)
    acou_branches = [b for b in branches if b in [0,1,2]]
    optic_branches = [b for b in branches if b not in [0,1,2]]
    for l in range(1):#(num_dispersions):
        for j in acou_branches:
           for m in range(len(indexes_Gammas)):
                this_G = indexes_Gammas_withboundaries[m]
                next_G = indexes_Gammas_withboundaries[m+1]+1
                kk_i = kk_commensurate[this_G:next_G]
                f_i = freqs[l][this_G:next_G,j]
                interp = interp1d(kk_i, f_i, 'cubic')
                x_i = np.arange(kk_i[0], kk_i[-1], 0.001)
                graphs[l] = ax2.plot(x_i,interp(x_i),  c=colours[l], label=title[l])
#           ax2.scatter(kk_commensurate, freqs[l][:,j], c='red')
        for j in optic_branches:
            kk_i = kk_commensurate
            f_i = freqs[l][:,j]
            interp = interp1d(kk_i, f_i, 'cubic')
            x_i = np.arange(kk_i[0], kk_i[-1], 0.001)
            graphs[l] = ax2.plot(x_i,interp(x_i),  c=colours[l], label=title[l])
#            ax2.scatter(kk_commensurate, freqs[l][:,j], c='red')
            

           
    ax2.get_shared_y_axes().join(ax, ax2)
    plt.ylim([f[0], f[-1]])
    plt.xlim([kk[0], kk[-1]])
    
    plt.xticks(kk_commensurate,indexes)
    plt.legend(handles=(graphs[0][0],))#graphs[1][0]
    ax.tick_params(axis='both', which='major', labelsize=15, width=2 , length=6, direction='in', top=True, left=True, bottom=True)
    ax2.tick_params(axis='y', which='major', labelsize=15, width=2 , length=6, direction='in')
    plt.rcParams['axes.linewidth'] = 2
#    plt.show()
    plt.suptitle('Spectrum branches '+str(branches))
    fig.savefig('plot5_'+str(branches)+'.pdf', backend='pgf')
    return 


def interpol_spectrum_old(ks_path, freq, freqs_from_spectrum, eigvecs, modes, ZQS, new_ks_in_between):
    num_ks = len(ks_path)
    num_modes = len(freqs_from_spectrum[0,:])
    num_freqs = len(ZQS[:,0,0])
    kk = np.linspace(0,1,num_ks)
    num_Gammas, indexes_Gammas, indexes_Gammas_withboundaries = find_Gammas(ks_path)
    df = freq[1] - freq[0]
    X, Y = np.meshgrid(kk,freq)
    
#    get_Force_Constants(eigvecs, freqs_from_spectrum.T)
    interp_freq = []
    INTERP = []
    for j in range(len(modes)):
        interp_freq_interm = np.array([])
        for m in range(len(indexes_Gammas)):
            this_G = indexes_Gammas_withboundaries[m]
            next_G = indexes_Gammas_withboundaries[m+1]+1
            kk_i = kk[this_G:next_G]
            f_i = freqs_from_spectrum[this_G:next_G,j]
            interp = interp1d(kk_i, f_i, 'cubic')
#            x_i = np.arange(kk_i[0], kk_i[-1], 0.001)
            INTERP.append(interp)
#            interp_freq_interm = np.concatenate((interp_freq_interm, interp(x_i)))
#        interp_freq_interm = np.array(interp_freq_interm)
#        interp_freq.append(interp_freq_interm)
#    interp_freq = np.array(interp_freq)

    ZQS_interp = np.zeros((num_freqs,num_modes, new_ks_in_between*(num_ks-1)+num_ks))
    
    
    ktot = 0
    for k in range(num_ks-1):
        sector = 0
        for l in indexes_Gammas_withboundaries[1::]:
            if(k >= l):
                sector = sector + 1
        count_k_in_between = 0
        for j in range(num_modes):  
            this_gaussian = ZQS[:,j,k]
            next_gaussian = ZQS[:,j,k+1]
            
#            import matplotlib.pyplot as plt
#            fig,ax = plt.subplots()
#            #to comment
#            popt_this, pcov_this = curve_fit(gaussian, freq, this_gaussian)
#            popt_next, pcov_next = curve_fit(gaussian, freq, next_gaussian)
            
            this_max = freqs_from_spectrum[k,j]
            next_max = freqs_from_spectrum[k+1,j]
            diff_maxima = next_max - this_max
            
            if(diff_maxima >= 0):
                this_gaussian_interp = interp1d(freq, this_gaussian, bounds_error=False, fill_value=0)
                next_gaussian_interp = interp1d(freq, next_gaussian, bounds_error=False, fill_value=0)
                this_gaussian_fit = this_gaussian_interp(freq-diff_maxima)
                next_gaussian_fit = next_gaussian_interp(freq)
                shift_interp = -next_max
            else:
                this_gaussian_interp = interp1d(freq, this_gaussian, bounds_error=False, fill_value=0)
                next_gaussian_interp = interp1d(freq, next_gaussian, bounds_error=False, fill_value=0)
                this_gaussian_fit = this_gaussian_interp(freq)
                next_gaussian_fit = next_gaussian_interp(freq+diff_maxima)
                shift_interp = -this_max
            
#            area_this_gaussian = np.trapz(this_gaussian_fit, freq)
#            area_next_gaussian = np.trapz(next_gaussian_fit, freq)

            this_k = kk[k]
            next_k = kk[k+1]
            interm_k = np.linspace(this_k, next_k, new_ks_in_between+2)[0:-1]

            interp = INTERP[sector+j*num_Gammas]
            intermediate_maxima = interp(interm_k)
            
            count_k_in_between = 0
            for m in range(new_ks_in_between+1):
                mi = intermediate_maxima[m]
                x = (interm_k[m] - interm_k[0])/(next_k-interm_k[0])
#                area_factor = area_this_gaussian+(area_next_gaussian-area_this_gaussian)*x
                interp_gaussian = this_gaussian_fit+(next_gaussian_fit-this_gaussian_fit)*x
                interp_gaussian_interp = interp1d(freq, interp_gaussian,bounds_error=False, fill_value=0)
                interp_gaussian_fit = interp_gaussian_interp(freq-(shift_interp+mi))
                ZQS_interp[:,j,ktot+count_k_in_between] = interp_gaussian_fit
                count_k_in_between = count_k_in_between + 1
                

#                popt = popt_this + (popt_next-popt_this)*x
#                interp_gaussian_fit = gaussian(freq, *popt)#1/(sig*np.sqrt(2*np.pi)) * np.exp(-.5*((freq-mi)/sig)**2) *area_factor

#                ax.plot(freq, interp_gaussian_fit, label='interp')
#            ax.plot(freq, this_gaussian, label='real this')
#            ax.plot(freq,next_gaussian, label='real next')
##            ax.plot(freq, this_gaussian_fit, label='real this fit')
##            ax.plot(freq,next_gaussian_fit, label='real next fit')
#            ax.legend()
            
        ktot = ktot + count_k_in_between
    ZQS_interp[:,:,-1] = ZQS[:,:,-1]
    return ZQS_interp

def get_nac_wrong(kpoint,Vuc, BORN, eps_inf, masses):
    const = 1.18*1e+07
    num = np.outer(np.dot(kpoint,BORN.T) , np.dot(BORN,kpoint))
    den = np.dot(kpoint.T,np.dot(eps_inf,kpoint))
    Cna_k = 4*np.pi/Vuc * num/den #* const
    
#                    thisq_eigvec = eigvecs_phonopy[j]
#                    M = masses_for_animation[0]*masses_for_animation[3]/(masses_for_animation[0]+masses_for_animation[3])
#                    omega_l = np.sqrt(freqs_from_disp[0][5]**2 + 4*np.pi*BORN[0,0]/(M*eps_inf[0,0]*Vuc))   
#                    nac_q = np.zeros((tot_atoms_uc, tot_atoms_uc, 3, 3), dtype='double', order='C')
#                    born = BORN.reshape((2,3,3))
#                    A = np.dot(kpoint, born)
#                    CC = np.zeros((6,6))
#                    for i in range(tot_atoms_uc):
#                        for j in range(tot_atoms_uc):
#                            nac_q[i, j] = np.outer(A[i], A[j])
#                            CC[i*3:(i+1)*3, j*3:(j+1)*3] = 4*np.pi/Vuc *nac_q[i,j] /den
##                            print(i,j, 4*np.pi/Vuc *nac_q[i,j])
#                    AB = CC
#                    eigvna, eigvecna = np.linalg.eigh(AB)
#                    print(np.sqrt(eigvna))              
#                    lamdas = np.diag(freqs_from_disp[0]**2)
#                    Dq = np.dot(thisq_eigvec, np.dot(lamdas, np.linalg.inv(thisq_eigvec)))
    M1, M2 = np.meshgrid(np.sqrt(masses), np.sqrt(masses))
    Mij = np.multiply(M1,M2)
    D = 1/Mij*Cna_k*const/1000 #+Dq
    eigvals, eigvecs = np.linalg.eigh(D)
    omegas_nac = np.sqrt(eigvals)
    return omegas_nac, D



#def get_real_branches(freqs):
#    num_ks = len(freqs[0,:])
#    num_branches = len(freqs[:,0])
#    indexes0 = np.arange(num_branches)
#    freqs_until_now = freqs[:,0:2]
#    
#    
#    for k in range(1,8):
#        deriv = np.diff(freqs[:,k-1:k+2], axis=1)
#        next_freqs = freqs[:,k+1]
#        this_deriv = deriv[:,1]
#        prev_deriv = deriv[:,0]
#        actual_diff = this_deriv-prev_deriv
#        print(this_deriv[2])
#        print(prev_deriv[2])
#        
#        sopra, sotto = np.ones(num_branches)*100, np.ones(num_branches)*100
#        two_sopra, two_sotto = np.ones(num_branches)*100, np.ones(num_branches)*100
#        
#        for j in range(num_branches-1):
#            down_freq = freqs[j-1,k+1]
#            up_freq = freqs[j+1,k+1]
#            diff_down = down_freq - freqs[j,k] 
#            diff_up = up_freq - freqs[j,k] 
#            sopra[j] = diff_up
#            sotto[j+1] = diff_down
#            
#        for j,l in zip(range(num_branches-2),range(2,num_branches)):
#            two_down_freq = freqs[l-2,k+1]
#            two_up_freq = freqs[j+2,k+1]
#            two_diff_down = two_down_freq - freqs[j,k] 
#            two_diff_up = two_up_freq - freqs[j,k] 
#            two_sopra[j] = two_diff_up
#            two_sotto[j+1] = two_diff_down
#
#        sopra, sotto = np.array(sopra), np.array(sotto)
#        diff_deriv_up = sopra - prev_deriv
#        diff_deriv_down = sotto - prev_deriv
#        gain_up = np.abs(diff_deriv_up)-np.abs(actual_diff)
#        gain_down = np.abs(diff_deriv_down)-np.abs(actual_diff)
#        
#        two_sopra, two_sotto = np.array(two_sopra), np.array(two_sotto)
#        two_diff_deriv_up = two_sopra - prev_deriv
#        two_diff_deriv_down = two_sotto - prev_deriv
#        two_gain_up = np.abs(two_diff_deriv_up)-np.abs(actual_diff)
#        two_gain_down = np.abs(two_diff_deriv_down)-np.abs(actual_diff)
#        
#        print(k)
#        print(np.shape(next_freqs))
#        print(np.round(np.hstack((freqs_until_now[:,-2::],next_freqs.reshape(6,1))),4))
#        print(np.round(next_freqs,4))
##        print()
##        print(np.round(diff_deriv_down,2))
#        print('gaindown',np.round(gain_down,2))
#        print('gainup',np.round(gain_up,2))
#        print('actualdiff', np.round(actual_diff,2))
#        print()
#        for j in range(num_branches-1):
#
#            if(gain_down[j+1] <0 and gain_up[j] <0):
#                print('aaa',j)
#                temp = next_freqs[j]
#                next_freqs[j] = next_freqs[j+1]
#                next_freqs[j+1] = temp
#               
##            elif(two_gain_up[j]<0 and two_gain_down[j+2]<0 and np.abs(next_freqs[j]-next_freqs[j+1])<0.05):
##                print('aaa2',j)
##                temp = next_freqs[j]
##                next_freqs[j] = next_freqs[j+2]
##                next_freqs[j+2] = temp
#        print(next_freqs)
#        freqs_sorted = np.hstack((freqs_until_now,next_freqs.reshape(num_branches,1)))
#        freqs_until_now = freqs_sorted
#        
#        print()
#    return freqs_sorted

def interpol_spectrum_old(ks_path, freq, freqs_from_spectrum, eigvecs, modes, ZQS, new_ks_in_between):
    num_ks = len(ks_path)
    num_modes = len(freqs_from_spectrum[0,:])
    num_freqs = len(ZQS[:,0,0])
    kk = np.linspace(0,1,num_ks)
    num_Gammas, indexes_Gammas, indexes_Gammas_withboundaries = find_Gammas(ks_path)
    df = freq[1] - freq[0]
    X, Y = np.meshgrid(kk,freq)
    
#    get_Force_Constants(eigvecs, freqs_from_spectrum.T)
    interp_freq = []
    INTERP = []
    for j in range(len(modes)):
        interp_freq_interm = np.array([])
        for m in range(len(indexes_Gammas)):
            this_G = indexes_Gammas_withboundaries[m]
            next_G = indexes_Gammas_withboundaries[m+1]+1
            kk_i = kk[this_G:next_G]
            f_i = freqs_from_spectrum[this_G:next_G,j]
            interp = interp1d(kk_i, f_i, 'cubic')
#            x_i = np.arange(kk_i[0], kk_i[-1], 0.001)
            INTERP.append(interp)
#            interp_freq_interm = np.concatenate((interp_freq_interm, interp(x_i)))
#        interp_freq_interm = np.array(interp_freq_interm)
#        interp_freq.append(interp_freq_interm)
#    interp_freq = np.array(interp_freq)

    ZQS_interp = np.zeros((num_freqs,num_modes, new_ks_in_between*(num_ks-1)+num_ks))
    
    
    ktot = 0
    for k in range(num_ks-1):
        sector = 0
        for l in indexes_Gammas_withboundaries[1::]:
            if(k >= l):
                sector = sector + 1
        count_k_in_between = 0
        for j in range(num_modes):  
            this_gaussian = ZQS[:,j,k]
            next_gaussian = ZQS[:,j,k+1]
            
#            import matplotlib.pyplot as plt
#            fig,ax = plt.subplots()
#            #to comment
#            popt_this, pcov_this = curve_fit(gaussian, freq, this_gaussian)
#            popt_next, pcov_next = curve_fit(gaussian, freq, next_gaussian)
            
            this_max = freqs_from_spectrum[k,j]
            next_max = freqs_from_spectrum[k+1,j]
            diff_maxima = next_max - this_max
            
            if(diff_maxima >= 0):
                this_gaussian_interp = interp1d(freq, this_gaussian, bounds_error=False, fill_value=0)
                next_gaussian_interp = interp1d(freq, next_gaussian, bounds_error=False, fill_value=0)
                this_gaussian_fit = this_gaussian_interp(freq-diff_maxima)
                next_gaussian_fit = next_gaussian_interp(freq)
                shift_interp = -next_max
            else:
                this_gaussian_interp = interp1d(freq, this_gaussian, bounds_error=False, fill_value=0)
                next_gaussian_interp = interp1d(freq, next_gaussian, bounds_error=False, fill_value=0)
                this_gaussian_fit = this_gaussian_interp(freq)
                next_gaussian_fit = next_gaussian_interp(freq+diff_maxima)
                shift_interp = -this_max
            
#            area_this_gaussian = np.trapz(this_gaussian_fit, freq)
#            area_next_gaussian = np.trapz(next_gaussian_fit, freq)

            this_k = kk[k]
            next_k = kk[k+1]
            interm_k = np.linspace(this_k, next_k, new_ks_in_between+2)[0:-1]

            interp = INTERP[sector+j*num_Gammas]
            intermediate_maxima = interp(interm_k)
            
            count_k_in_between = 0
            for m in range(new_ks_in_between+1):
                mi = intermediate_maxima[m]
                x = (interm_k[m] - interm_k[0])/(next_k-interm_k[0])
#                area_factor = area_this_gaussian+(area_next_gaussian-area_this_gaussian)*x
                interp_gaussian = this_gaussian_fit+(next_gaussian_fit-this_gaussian_fit)*x
                interp_gaussian_interp = interp1d(freq, interp_gaussian,bounds_error=False, fill_value=0)
                interp_gaussian_fit = interp_gaussian_interp(freq-(shift_interp+mi))
                ZQS_interp[:,j,ktot+count_k_in_between] = interp_gaussian_fit
                count_k_in_between = count_k_in_between + 1
                

#                popt = popt_this + (popt_next-popt_this)*x
#                interp_gaussian_fit = gaussian(freq, *popt)#1/(sig*np.sqrt(2*np.pi)) * np.exp(-.5*((freq-mi)/sig)**2) *area_factor

#                ax.plot(freq, interp_gaussian_fit, label='interp')
#            ax.plot(freq, this_gaussian, label='real this')
#            ax.plot(freq,next_gaussian, label='real next')
##            ax.plot(freq, this_gaussian_fit, label='real this fit')
##            ax.plot(freq,next_gaussian_fit, label='real next fit')
#            ax.legend()
            
        ktot = ktot + count_k_in_between
    ZQS_interp[:,:,-1] = ZQS[:,:,-1]
    return ZQS_interp


def plot6_old(x,y,ytot, k,eigvec,freq,n,Ruc,eigname,masses, max_Z):
    mpl.rcParams.update(pgf_with_latex)
    
    fig,ax = plt.subplots()
#    graph2, = ax.plot(x,ytot,'--',label='qpoint DOS', color='orangered')
    graph1, = ax.plot(x,y,label='mode-projected DOS', color='blue')
    ax.set_xlim(left=-1,right=30)
    ax.set_xlabel('Frequency [Thz]')
    plt.title('Spectrum of mode n. '+str(n)+' kpoint '+str(np.round(k,2)))
    
#    ax1 = ax.twiny()
#    ax1.set_xlabel('Frequency [cm$^{-1}$]')
#    ax1.plot(x*33.35641,-np.ones(len(x)),c='white',linewidth=0,label='')
#    ax1.set_xlim(-1*33.35641,30*33.35641)

    graph3, = ax.plot(np.repeat(freq,100),np.linspace(0,y.max(),100),':' ,c='r', label='freq from dispersion')
    plt.legend(handles=[graph1,  graph3], loc=2)
    
    
    ax2 = fig.add_axes([0.5, .5, .4, .4],projection='3d')
#    ax2.set_title(str(eigname)+'\nfrequency: '+str(freq))
    ax2.set_xlabel('x'), ax2.set_ylabel('y'), ax2.set_zlabel('z')
    ampl = 10
    eigvec = eigvec/np.sqrt(masses)*ampl

    print('# =============================================================================')
    print('Kpoint '+str(np.round(k,2))+' Mode '+str(n)+'; frequency: ', freq, '\n')
    print('Eigenvector components:')
    print(np.round(np.reshape(np.real(eigvec),np.shape(Ruc)),2))
    print()
    print('Imaginary part:')
    print(np.round(np.reshape(np.imag(eigvec),np.shape(Ruc)),2))
    print()
    ani = plot_eigvec_noani(Ruc, 1,k,eigvec,freq,ax2,fig, masses)
    
    if(max_Z > np.max(ytot.max()) or max_Z < 0.0):
        a=1
    else:
        ax.set_ylim(bottom=-max_Z/10,top=max_Z)
        
    plt.show()
    plt.tight_layout()
    fig.savefig('plot6_'+str(np.round(k))+'_mode_'+str(n)+'.pdf')
    return ani


def read_path(kinput_scaled, Nqpoints, labels, Hk):
    Nq_input = len(kinput_scaled)
    ks = []
    x_labels = []
    distances = []
    previous_k = np.dot(Hk, kinput_scaled[0])
    distance = 0.0
    for i in range(Nq_input-1):
        this_k_input = kinput_scaled[i]
        next_k_input = kinput_scaled[i+1]
        ks.append(this_k_input)
        x_labels.append(labels[i])
        direction_input = (next_k_input - this_k_input)/np.linalg.norm(next_k_input - this_k_input)
        accepted_kinputs = []
        for j in range(Nqpoints):
            to_skip = (4)*j
            this_k = np.genfromtxt('quasiparticles',skip_header=to_skip+0, max_rows=1)
            print(this_k)
            direction = (this_k - this_k_input)/np.linalg.norm(this_k - this_k_input)
            print(direction,direction_input)
            if(np.allclose(direction, direction_input) and not np.allclose(this_k, next_k_input)):
                print('aaa')
                ks.append(this_k)
                distance = distance + np.linalg.norm(np.dot(Hk,this_k) - previous_k)
                distances.append(distance)
                previous_k = np.dot(Hk,this_k)
                x_labels.append(' ')
            elif(np.allclose(this_k, this_k_input) and not this_k.tolist() in accepted_kinputs):
                accepted_kinputs.append(this_k_input.tolist())
                this_q = np.dot(Hk, this_k_input)
                distance = distance + np.linalg.norm(this_q - previous_k)
                distances.append(distance)  
                previous_k = this_q
    
    ks.append(kinput_scaled[-1])
    x_labels.append(labels[-1])
    distance = distance + np.linalg.norm(np.dot(Hk,kinput_scaled[-1])-previous_k)
    distances.append(distance)
    distances = np.array(distances)
    return ks, x_labels, distances


def plot(x,y,title):
    fig,ax = plt.subplots()
    ax.plot(x,y)
    ax.set_xlabel('Frequency [Thz]')
    ax.set_title(title)
    plt.show()
    return


def from_band(ks):
    Points = {'$\Gamma$':[0,0,0],'X':[0.5,0,0],'M':[0.5,0.5,0],'R':[0.5,0.5,0.5],'boh':[0,0.5,0], 'Z':[0,0,0.5]}
    x_labels = []
    for kpoint in ks:
        a = 0
        for element in Points.items():
            a = a + 1
            if (np.array_equal(kpoint , element[1])):
                x_labels.append(element[0])
                break
            if (a==len(Points.items())):
                x_labels.append(' ')
    return x_labels


def plot_k(f, data, data_projected, indexes,freqs, max_Z, branches,  freq_res, title=''):
    """
    Plotting the dispersion from MD and from phonon theory.
    
    Variables:
        f = array of the frequencies [Thz] 
        data = matrix with spectra from all k points: shape = (timesteps,N)
        indexes = list of all kpoints
        freqs = frequencies from phonopy
    """
    
    pgf_with_latex = {                      # setup matplotlib to use latex for output

    "pgf.texsystem": "pdflatex",        # change this if using xetex or lautex

    "text.usetex": True,                # use LaTeX to write all text

    "font.family": "serif",

    "font.serif": [],                   # blank entries should cause plots to inherit fonts from the document

    "font.sans-serif": [],

    "font.monospace": [],

    "axes.labelsize": 16,                # LaTeX default is 10pt font.     "text.fontsize": 10,

    "legend.fontsize": 12,               # Make the legend/label fonts a little smaller

    "xtick.labelsize": 16,

    "ytick.labelsize": 16,

    "figure.figsize": figsize(1.4),       # default fig size of 0.9 textwidth

    "pgf.preamble": [

        r"\usepackage[utf8x]{inputenc}",    # use utf8 fonts becasue your computer can handle it :)

        r"\usepackage[T1]{fontenc}",        # plots will be generated using this preamble

        ]

    }

    mpl.rcParams.update(pgf_with_latex)

    
    fig,ax = plt.subplots()
    plt.suptitle('Spectrum via MD and phonon theory')
    #ax.set_title(title)
    ax.set_ylabel('[Thz]')
    N = len(data[0,:])
    offset = np.zeros(N) + f[0]
    df = f[1]-f[0]
    molt = int(freq_res/df)
    tot_branches = int(len(freqs[0][0,:]))
    
    kk = np.linspace(0,1,N)
    dk = kk[1] - kk[0]
    
    

#    indexes = from_band(ks)
    
    #norm = [plt.cm.colors.Normalize(vmax=abs(data[0::1,l]).max(), vmin=-abs(data[0::1,l]).min()) for l in range(len(data[0,:]))]
    if(len(branches) == tot_branches): #plot whole spectrum
        print('Drawing the whole spectrum...')
        if(max_Z > np.max(data) or max_Z < 0.0):
            max_Z = np.max(data[::molt,:])
        norm = plt.cm.colors.Normalize(vmax=max_Z, vmin=0)
        for j in range(0,len(data[:,0]),molt):  
            # this is the whole spectrum
            ax.bar(kk, np.repeat(df*molt,N), bottom=offset-df/2,  color=plt.cm.Blues(norm(data[j,:])), tick_label=indexes, align='center', width=dk, alpha=None)
            offset = offset + df*molt
            
    else:   #print only those branches 
        if(max_Z > np.max(data_projected) or max_Z < 0.0):
             max_Z = np.max(data_projected)
        norm = plt.cm.colors.Normalize(vmax=max_Z, vmin=0)
        cmps = [plt.cm.Purples, plt.cm.Reds, plt.cm.Greens, plt.cm.Greys, plt.cm.Oranges]
        print('Drawing spectrum branches ', branches)
        for j in range(0,len(data[0::1,0])):
            for mm in range(len(data_projected[0,:,0])):
                if(np.max(data_projected[j,mm,:]) == np.max(data_projected[:,mm,:])): #this is just for the legend
                    ax.bar(kk, np.repeat(df,N), bottom=offset-df/2,  color=cmps[mm]((data_projected[j,mm,:])), tick_label=indexes, align='center', width=dk, alpha=.5)
                    kpoint_of_max = np.argwhere(data_projected[j,mm,:] == np.max(data_projected[j,mm,:]))[0,0]
                    bar = ax.bar(kk[kpoint_of_max], df, bottom=offset[0]-df/2,  color=cmps[mm]((data_projected[j,mm,kpoint_of_max])),  align='center', width=dk, alpha=.5, label='mode '+str(branches[0]+mm))
                else:
#                    print(j, (data_projected[j,mm,:]))
                    ax.bar(kk, np.repeat(df,N), bottom=offset-df/2,  color=cmps[mm]((data_projected[j,mm,:])), tick_label=indexes, align='center', width=dk, alpha=.5)

            offset = offset + df
   
    
    ax2 = plt.twinx()
    ax2.set_ylabel('[Thz]')
    num_dispersions = len(freqs)
    colours = ['black', 'red']
    for l in range(num_dispersions):
        for j in range(tot_branches):
            ax2.scatter(kk,freqs[l][:,j], marker='x', c=colours[l])
        ax2.scatter(kk,freqs[l][:,tot_branches-1],  marker='x',  c=colours[l], label=title[l])
    ax2.get_shared_y_axes().join(ax, ax2)
    
    
    handles, labels = ax.get_legend_handles_labels()

    plt.ylim([f[0], f[-1]])
    plt.legend(handles=handles, labels=labels)
    ax.tick_params(axis='both', which='major', labelsize=15, width=2 , length=6, direction='in', top=True, left=True, bottom=True)
    ax2.tick_params(axis='y', which='major', labelsize=15, width=2 , length=6, direction='in')
#    plt.show()
    fig.savefig('spectrum_branches_'+str(branches)+'.pdf')
    fig.savefig('spectrum_branches_'+str(branches)+'.png')
    return

def plot_k2_old(f, data, data_projected, indexes,freqs, max_Z, branches, ks_path, title=''):
    pgf_with_latex = {                      # setup matplotlib to use latex for output

    "pgf.texsystem": "pdflatex",        # change this if using xetex or lautex

    "text.usetex": True,                # use LaTeX to write all text

    "font.family": "serif",

    "font.serif": [],                   # blank entries should cause plots to inherit fonts from the document

    "font.sans-serif": [],

    "font.monospace": [],

    "axes.labelsize": 16,                # LaTeX default is 10pt font.     "text.fontsize": 10,

    "legend.fontsize": 12,               # Make the legend/label fonts a little smaller

    "xtick.labelsize": 16,

    "ytick.labelsize": 16,

    "figure.figsize": figsize(1.4),       # default fig size of 0.9 textwidth

    "pgf.preamble": [

        r"\usepackage[utf8x]{inputenc}",    # use utf8 fonts becasue your computer can handle it :)

        r"\usepackage[T1]{fontenc}",        # plots will be generated using this preamble

        ]

    }

    mpl.rcParams.update(pgf_with_latex)
    num_ks = len(data_projected[0,0,:])
    tot_branches = int(len(freqs[0][0,:]))
    plt.ion()
    kk = np.linspace(0,1,num_ks)
    X, Y = np.meshgrid(kk,f)
    
    fig, ax = plt.subplots()
    
    
#    if(len(branches) == tot_branches): #plot whole spectrum
#        if(max_Z > np.max(data) or max_Z < 0.0):
#            max_Z = np.max(data)
#        print('Drawing the whole spectrum...')
#        ax.contourf(X,Y,data,100, vmax=max_Z)
#        print('finished')

    if(max_Z > np.max(data_projected) or max_Z < 0.0):
        max_Z = np.max(data_projected)
    print('Drawing branches ', branches)
    ax.contourf(X,Y,np.sum(data_projected, axis=1),100, vmax=max_Z)
    print('finished')
        
    num_Gammas, indexes_Gammas, indexes_Gammas_withboundaries = util.find_Gammas(ks_path)
    
    
    
#     ax2 = plt.twinx()
#     ax2.set_ylabel('[Thz]')
#     num_dispersions = len(freqs)
#     colours = ['black', 'red']
#     graphs = [0,0]
#     num_ks_commensurate = len(freqs[0][:,0])
#     kk_commensurate = np.linspace(0,1,num_ks_commensurate)
#     acou_branches = [b for b in branches if b in [0,1,2]]
#     optic_branches = [b for b in branches if b not in [0,1,2]]
#     for l in range(1):#(num_dispersions):
#         for j in acou_branches:
#            for m in range(len(indexes_Gammas)):
#                 this_G = indexes_Gammas_withboundaries[m]
#                 next_G = indexes_Gammas_withboundaries[m+1]+1
#                 kk_i = kk_commensurate[this_G:next_G]
#                 f_i = freqs[l][this_G:next_G,j]
#                 interp = interp1d(kk_i, f_i, 'cubic')
#                 x_i = np.arange(kk_i[0], kk_i[-1], 0.001)
#                 graphs[l] = ax2.plot(x_i,interp(x_i),  c=colours[l], label=title[l])
# #           ax2.scatter(kk_commensurate, freqs[l][:,j], c='red')
#         for j in optic_branches:
#             kk_i = kk_commensurate
#             f_i = freqs[l][:,j]
#             interp = interp1d(kk_i, f_i, 'cubic')
#             x_i = np.arange(kk_i[0], kk_i[-1], 0.001)
#             graphs[l] = ax2.plot(x_i,interp(x_i),  c=colours[l], label=title[l])
# #            ax2.scatter(kk_commensurate, freqs[l][:,j], c='red')
            

           
#     ax2.get_shared_y_axes().join(ax, ax2)
    plt.ylim([f[0], f[-1]])
    plt.xlim([kk[0], kk[-1]])
    
    # plt.xticks(kk_commensurate,indexes)
    # plt.legend(handles=(graphs[0][0],))#graphs[1][0]
    ax.tick_params(axis='both', which='major', labelsize=15, width=2 , length=6, direction='in', top=True, left=True, bottom=True)
    ax2.tick_params(axis='y', which='major', labelsize=15, width=2 , length=6, direction='in')
    plt.rcParams['axes.linewidth'] = 2
#    plt.show()
    plt.suptitle('Spectrum branches '+str(branches))
    fig.savefig('plot5_'+str(branches)+'.pdf', backend='pgf')
    return 