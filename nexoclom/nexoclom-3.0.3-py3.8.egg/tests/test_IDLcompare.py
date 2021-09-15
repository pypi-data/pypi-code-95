import os.path
import astropy.units as u
import numpy as np
from scipy.io import readsav
import pandas as pd
import pickle
import subprocess
from astropy.visualization import PercentileInterval
try:
    from ..Input import Input
    from ..Output import Output
except:
    from nexoclom import Input, Output
from MESSENGERuvvs import MESSENGERdata
from bokeh.layouts import column
import bokeh.plotting as bkp


inputfiles = ['Ca.isotropic.maxwellian.50000.input',    # Good
              'Ca.spot.maxwellian.input',               # Good
              'Na.Gaussian.4_2.south.input',            # Good
              'Na.Sputtering.input',                    # Good
              'Ca.Gaussian.4_2.south.input',            # Good
              'Ca.spot.gaussian.input',                 # Good
              'Na.Gaussian.3_1.input',                  # Good
              'Na.Gaussian.3_1.no_accom.input',         # Good
              'Na.maxwellian.1200.accom.input',         # fixed
              'Na.Gaussian.3_1.accom.input',
              'Na.Gaussian.3_1.fullaccom.input']

idloverwrite = False
pyoverwrite = False

def load_idl_files(filename):
    X0 = {'x0':[], 'y0':[], 'z0':[], 'vx0':[], 'vy0':[], 'vz0':[]}
    X = {'x':[], 'y':[], 'z':[], 'vx':[], 'vy':[], 'vz':[], 'frac':[]}
    idlout = readsav(filename)
    
    for line in idlout['outputfile']:
        out = readsav(line.strip())
        out = out['output']
        t0 = out['time'][0] == max(out['time'][0])
        for key in X0.keys():
            X0[key].extend(out[key][0][t0])
        for key in X.keys():
            X[key].extend(out[key][0])
            
    result = pd.DataFrame(X0)
    result2 = pd.DataFrame(X)
    
    return (result, result2, idlout['im'], idlout['col'], idlout['radiance'],
            idlout['packets'])

for infile_ in inputfiles:
    infile = os.path.join(os.path.dirname(__file__),
                          'inputfiles', infile_)
    
    idlsavefile = os.path.join(os.path.dirname(__file__), 'outputs',
                               infile_.replace('.input', '.IDL.pkl'))
    idlfile = f"'{infile.replace('.input', '.IDL.input')}'"
    idlfile_ = infile.replace('.input', '.IDL.input')
    idloutputfile = os.path.join(os.path.dirname(__file__), 'idloutputs',
                                 os.path.basename(idlfile_)+'.sav')
    if not(os.path.exists(idlsavefile)) or idloverwrite:
        # Run the IDL version
        if not(idloutputfile) or idloverwrite:
            print('Running IDL version')
            ow = 1 if idloverwrite else 0
            command = (f'/Applications/exelis/idl85/bin/idl '
                       f'-e "run_idl_version, {idlfile}, overwrite={ow}"')
            print(command)
            idlcmd = subprocess.run(command, shell=True, capture_output=True)
            assert 'Completed Successfully' in str(idlcmd.stdout), idlcmd
        else:
            pass

        # Load the IDL results
        print(f'Loading from {idloutputfile}')
        idl0, idl, idlim, idlcol, idlrad, idlpack = load_idl_files(idloutputfile)
        idlim = idlim.transpose()
        idlcol = idlcol.transpose()

        with open(idlsavefile, 'wb') as f:
            pickle.dump((idl0, idl, idlim, idlcol, idlrad, idlpack), f)
    else:
        print('Found IDL results')
        with open(idlsavefile, 'rb') as f:
            idl0, idl, idlim, idlcol, idlrad, idlpack = pickle.load(f)
    
    # Run the python version
    inputs = Input(infile)
    sp = inputs.options.species
    orbit = 1489 if sp == 'Ca' else 1541
    data = MESSENGERdata(sp, f'orbit = {orbit}')
    inputs.geometry.taa = data.taa * u.rad
    data.model(inputs, 1e5, overwrite=pyoverwrite)
    pyim = inputs.produce_image('inputfiles/MercuryEmission.format')
    pycol = inputs.produce_image('inputfiles/MercuryColumn.format')

    # Load the python results
    outfiles, _, _ = inputs.search()
    output = Output.restore(outfiles[0])
    py0 = output.X0
    py = output.X

    # Convert velocities to km/s
    py0.vx = py0.vx * output.inputs.geometry.planet.radius
    py0.vy = py0.vy * output.inputs.geometry.planet.radius
    py0.vz = py0.vz * output.inputs.geometry.planet.radius
    py.vx = py.vx * output.inputs.geometry.planet.radius
    py.vy = py.vy * output.inputs.geometry.planet.radius
    py.vz = py.vz * output.inputs.geometry.planet.radius

    idl0.vx0 = idl0.vx0 * output.inputs.geometry.planet.radius
    idl0.vy0 = idl0.vy0 * output.inputs.geometry.planet.radius
    idl0.vz0 = idl0.vz0 * output.inputs.geometry.planet.radius
    idl.vx = idl.vx * output.inputs.geometry.planet.radius
    idl.vy = idl.vy * output.inputs.geometry.planet.radius
    idl.vz = idl.vz * output.inputs.geometry.planet.radius

    # Compare initial spatial distribution
    xbins = np.linspace(-1, 1, 21)
    xpy0, _ = np.histogram(py0.x, bins=xbins)
    ypy0, _ = np.histogram(py0.y, bins=xbins)
    zpy0, _ = np.histogram(py0.z, bins=xbins)

    xidl0, _ = np.histogram(idl0.x0, bins=xbins)
    yidl0, _ = np.histogram(idl0.y0, bins=xbins)
    zidl0, _ = np.histogram(idl0.z0, bins=xbins)

    p1 = bkp.figure(plot_width=1000, plot_height=600,
                    title=f'{infile_}: Initial x Distribution')
    #p1.legend.click_policy = 'hide'
    p1.line(xbins[0:-1], xpy0/max(xpy0), color='red', legend_label='Python')
    p1.line(xbins[0:-1], xidl0/max(xidl0), color='blue', legend_label='IDL')

    p2 = bkp.figure(plot_width=1000, plot_height=600,
                    title = f'{infile_}: Initial y Distribution')
    p2.line(xbins[0:-1], ypy0/max(ypy0), color='red', legend_label='Python')
    p2.line(xbins[0:-1], yidl0/max(yidl0), color='blue', legend_label='IDL')

    p3 = bkp.figure(plot_width=1000, plot_height=600,
                    title = f'{infile_}: Initial z Distribution')
    p3.line(xbins[0:-1], zpy0/max(zpy0), color='red', legend_label='Python')
    p3.line(xbins[0:-1], zidl0/max(zidl0), color='blue', legend_label='IDL')
    
    # compare initial velocity distribution
    vbins = np.linspace(np.min(py0.vx), np.max(py0.vx), 21)
    vxpy0, _ = np.histogram(py0.vx, bins=vbins)
    vypy0, _ = np.histogram(py0.vy, bins=vbins)
    vzpy0, _ = np.histogram(py0.vz, bins=vbins)

    vxidl0, _ = np.histogram(idl0.vx0, bins=vbins)
    vyidl0, _ = np.histogram(idl0.vy0, bins=vbins)
    vzidl0, _ = np.histogram(idl0.vz0, bins=vbins)

    p4 = bkp.figure(plot_width=1000, plot_height=600,
                    title=f'{infile_}: Initial vx Distribution')
    p4.line(xbins[0:-1], vxpy0/max(vxpy0), color='red', legend_label='Python')
    p4.line(xbins[0:-1], vxidl0/max(vxidl0), color='blue', legend_label='IDL')

    p5 = bkp.figure(plot_width=1000, plot_height=600,
                    title = f'{infile_}: Initial vy Distribution')
    p5.line(xbins[0:-1], vypy0/max(vypy0), color='red', legend_label='Python')
    p5.line(xbins[0:-1], vyidl0/max(vyidl0), color='blue', legend_label='IDL')

    p6 = bkp.figure(plot_width=1000, plot_height=600,
                    title = f'{infile_}: Initial vz Distribution')
    p6.line(xbins[0:-1], vzpy0/max(vzpy0), color='red', legend_label='Python')
    p6.line(xbins[0:-1], vzidl0/max(vzidl0), color='blue', legend_label='IDL')

    # Compare final spatial distribution
    xbins = np.linspace(-10, 10, 201)
    xpy, _ = np.histogram(py.x, bins=xbins)
    ypy, _ = np.histogram(py.y, bins=xbins)
    zpy, _ = np.histogram(py.z, bins=xbins)

    xidl, _ = np.histogram(idl.x, bins=xbins)
    yidl, _ = np.histogram(idl.y, bins=xbins)
    zidl, _ = np.histogram(idl.z, bins=xbins)

    p7 = bkp.figure(plot_width=1000, plot_height=600,
                    title=f'{infile_}: Final x Distribution')
    p7.line(xbins[0:-1], xpy/max(xpy), color='red', legend_label='Python')
    p7.line(xbins[0:-1], xidl/max(xidl), color='blue', legend_label='IDL')

    p8 = bkp.figure(plot_width=1000, plot_height=600,
                    title=f'{infile_}: Final y Distribution')
    p8.line(xbins[0:-1], ypy/max(ypy), color='red', legend_label='Python')
    p8.line(xbins[0:-1], yidl/max(yidl), color='blue', legend_label='IDL')

    p9 = bkp.figure(plot_width=1000, plot_height=600,
                    title=f'{infile_}: Final z Distribution')
    p9.line(xbins[0:-1], zpy/max(zpy), color='red', legend_label='Python')
    p9.line(xbins[0:-1], zidl/max(zidl), color='blue', legend_label='IDL')

    # Compare final velocity distribution
    vbins = np.linspace(np.min(py.vx), np.max(py.vx), 201)
    vxpy, _ = np.histogram(py.vx, bins=vbins, weights=py.frac)
    vypy, _ = np.histogram(py.vy, bins=vbins, weights=py.frac)
    vzpy, _ = np.histogram(py.vz, bins=vbins, weights=py.frac)

    vxidl, _ = np.histogram(idl.vx, bins=vbins, weights=idl.frac)
    vyidl, _ = np.histogram(idl.vy, bins=vbins, weights=idl.frac)
    vzidl, _ = np.histogram(idl.vz, bins=vbins, weights=idl.frac)

    p10 = bkp.figure(plot_width=1000, plot_height=600,
                    title=f'{infile_}: Final vx Distribution')
    p10.line(vbins[0:-1], vxpy/max(vxpy), color='red', legend_label='Python')
    p10.line(vbins[0:-1], vxidl/max(vxidl), color='blue', legend_label='IDL')

    p11 = bkp.figure(plot_width=1000, plot_height=600,
                    title=f'{infile_}: Final vy Distribution')
    p11.line(vbins[0:-1], vypy/max(vypy), color='red', legend_label='Python')
    p11.line(vbins[0:-1], vyidl/max(vyidl), color='blue', legend_label='IDL')

    p12 = bkp.figure(plot_width=1000, plot_height=600,
                    title=f'{infile_}: Final vz Distribution')
    p12.line(vbins[0:-1], vzpy/max(vzpy), color='red', legend_label='Python')
    p12.line(vbins[0:-1], vzidl/max(vzidl), color='blue', legend_label='IDL')

    ###############################################

    q0 = np.sum(pyim.image[:,200:250], axis=1)
    q1 = np.sum(pyim.image[:,250:300], axis=1)
    q2 = np.sum(pyim.image[200:250,:], axis=0)
    q3 = np.sum(pyim.image[250:300,:], axis=0)
    i0 = np.sum(idlim[:,200:250], axis=1)
    i1 = np.sum(idlim[:,250:300], axis=1)
    i2 = np.sum(idlim[200:250,:], axis=0)
    i3 = np.sum(idlim[250:300,:], axis=0)
    
    p13 = bkp.figure(plot_width=1000, plot_height=600,
                    title=f'{infile_}: Radiance')
    p13.line(pyim.xaxis, q0, legend_label='py0', color='red')
    p13.line(pyim.xaxis, i0, legend_label='idl0', color='blue')
    p13.line(pyim.xaxis, q1, legend_label='py1', color='red')
    p13.line(pyim.xaxis, i1, legend_label='idl1', color='blue')

    p14 = bkp.figure(plot_width=1000, plot_height=600,
                    title=f'{infile_}: Radiance')
    p14.line(pyim.xaxis, q2, legend_label='py2', color='red')
    p14.line(pyim.xaxis, i2, legend_label='idl2', color='blue')
    p14.line(pyim.xaxis, q3, legend_label='py3', color='red')
    p14.line(pyim.xaxis, i3, legend_label='idl3', color='blue')
    
    q0 = np.sum(pycol.image[:, 200:250], axis=1)
    q1 = np.sum(pycol.image[:, 250:300], axis=1)
    q2 = np.sum(pycol.image[200:250, :], axis=0)
    q3 = np.sum(pycol.image[250:300, :], axis=0)
    i0 = np.sum(idlcol[:, 200:250], axis=1)
    i1 = np.sum(idlcol[:, 250:300], axis=1)
    i2 = np.sum(idlcol[200:250, :], axis=0)
    i3 = np.sum(idlcol[250:300, :], axis=0)

    p15 = bkp.figure(plot_width=1000, plot_height=600,
                    title=f'{infile_}: Column')
    p15.line(pycol.xaxis, q0, legend_label='py0', color='red')
    p15.line(pycol.xaxis, i0, legend_label='idl0', color='blue')
    p15.line(pycol.xaxis, q1, legend_label='py1', color = 'red')
    p15.line(pycol.xaxis, i1, legend_label='idl1', color='blue')

    p16 = bkp.figure(plot_width=1000, plot_height=600,
                    title=f'{infile_}: Column')
    p16.line(pycol.xaxis, q2, legend_label='py2', color = 'red')
    p16.line(pycol.xaxis, i2, legend_label='idl2', color='blue')
    p16.line(pycol.xaxis, q3, legend_label='py3', color = 'red')
    p16.line(pycol.xaxis, i3, legend_label='idl3', color='blue')

    # Estimate model strength (source rate) by mean of middle 50%
    interval = PercentileInterval(50)
    lim = interval.get_limits(data.data.radiance)
    mask = ((data.data.radiance >= lim[0]) &
            (data.data.radiance <= lim[1]))
    m_data = np.mean(data.data.radiance[mask])
    m_idl = np.mean(idlrad[mask])
    str = m_data/m_idl

    p17 = bkp.figure(plot_width=1000, plot_height=600,
                     title=f'{infile_}: Orbit compare radiance')
    p17.circle(data.data['utc'], data.data['radiance'], color='black',
             legend_label='Data')
    p17.line(data.data['utc'], data.data['model0'], color='red',
             legend_label='Python')
    p17.line(data.data['utc'], idlrad*str, color='blue', legend_label='IDL')
    
    p18 = bkp.figure(plot_width=1000, plot_height=600,
                     title=f'{infile_}: Orbit compare packets')
    p18.line(data.data['utc'], data.data['packets0'], color='red',
             legend_label='Python')
    p18.line(data.data['utc'],
             idlpack*np.max(data.data['packets0'])/np.max(idlpack),
             color='blue', legend_label='IDL')

    savefile = os.path.join(os.path.dirname(__file__), 'figures',
                            infile_.replace('.input', '.html'))
    bkp.output_file(savefile)
    bkp.save(column(p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11,
                    p12, p13, p14, p15, p16, p17, p18))
 
