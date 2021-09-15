import matplotlib
#matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.animation as animation

import numpy as np
from nexoclom import Input, Output
from MESSENGERuvvs import MESSENGERdata
import pickle
from mathMB import minmaxmean
import time

def test_compareversions():
    # old version
    old = pickle.load(open('data/oldmodel.pkl', 'rb'))
    old0 = pickle.load(open('data/oldmodel0.pkl', 'rb'))

    # new version
    npack = 1e5
    orbit = 36
    overwrite = True

    inputsfile = 'inputfiles/Na.Gaussian.3_1.input'
#    inputsfile = 'inputfiles/Na.v3.radial.input'
    inputs = Input(inputsfile)
    inputs.run(npack, overwrite=overwrite)

    # imformat = 'MercuryEmission.format'
    # image = inputs.produce_image(imformat)
    # image.display(savefile=inputsfile.replace('.input', '_radiance.png'),
    #               show=False)
    #
    # colformat = 'MercuryColumn.format'
    # column = inputs.produce_image(colformat)
    # column.display(savefile=inputsfile.replace('.input', '_column.png'),
    #                show=False)
    
    savefile, _, _ = inputs.search()
    output = Output.restore(savefile[0])
    X = output.X
    X0 = output.X0
    
    # xbin = np.linspace(-1, 1, 25)
    # h, _ = np.histogram(X0.x, bins=xbin)
    # h0, _ = np.histogram(old0.x, bins=xbin)
    # plt.plot(xbin[0:-1], h)
    # plt.plot(xbin[0:-1], h0)
    # plt.show()
    #
    # h, _ = np.histogram(X0.y, bins=xbin)
    # h0, _ = np.histogram(old0.y, bins=xbin)
    # plt.plot(xbin[0:-1], h)
    # plt.plot(xbin[0:-1], h0)
    # plt.show()
    #
    # h, _ = np.histogram(X0.z, bins=xbin)
    # h0, _ = np.histogram(old0.z, bins=xbin)
    # plt.plot(xbin[0:-1], h)
    # plt.plot(xbin[0:-1], h0)
    # plt.show()
    #
    # xbin = np.linspace(-6, 6, 100)
    # h, _ = np.histogram(X0.vx*2440, bins=xbin)
    # h0, _ = np.histogram(old0.vx*2440, bins=xbin)
    # plt.plot(xbin[0:-1], h)
    # plt.plot(xbin[0:-1], h0)
    # plt.show()
    #
    # h, _ = np.histogram(X0.vy*2440, bins=xbin)
    # h0, _ = np.histogram(old0.vy*2440, bins=xbin)
    # plt.plot(xbin[0:-1], h)
    # plt.plot(xbin[0:-1], h0)
    # plt.show()
    #
    # h, _ = np.histogram(X0.vz*2440, bins=xbin)
    # h0, _ = np.histogram(old0.vz*2440, bins=xbin)
    # plt.plot(xbin[0:-1], h)
    # plt.plot(xbin[0:-1], h0)
    # plt.show()
    # assert 0

    # Set up formatting for the movie files
    
    animate(X, 'newmodel.mp4')
#    animate(old, 'oldmodel.mp4')



def animate(data, filename):
    Writer = animation.writers['ffmpeg']
    writer = Writer(fps=15, metadata=dict(artist='Me'), bitrate=1800)
    
    def xyscatter(t=0):
        while t <= len(times):
            t += 1
            x = data.x[data.time == times[t-1]].values
            y = data.y[data.time == times[t-1]].values
            # f = data.frac[data.time == times[t-1]].values
            yield x, y
            
    def init():
        ax.set_xlim(-10,10)
        ax.set_ylim(-10,10)
        ax.set_aspect('equal')
        ax.plot(np.cos(np.linspace(0, 2*np.pi, 361)),
                np.sin(np.linspace(0, 2*np.pi, 361)))
                
        line.set_data(xdata, ydata)
        
        return line,
        
    def run(data):
        xdata, ydata = data
        line.set_data(xdata, ydata)

    times = data.time.unique()
    t = times[0]
    xdata, ydata = data.x[data.time == t], data.y[data.time == t]

    fig, ax = plt.subplots(1, 1)
    line, = ax.plot(xdata, ydata, marker='.', linestyle=' ')
    
    ani = animation.FuncAnimation(fig, run, xyscatter, interval=10,
                                  init_func=init)
    ani.save(filename, writer=writer)
    plt.close()


if __name__ == '__main__':
    test_compareversions()
