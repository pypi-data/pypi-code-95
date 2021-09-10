#!/usr/bin/env python3
# -*- coding: utf-8 -*-
​
from __future__ import print_function, division, absolute_import
​
#::: plotting settings
import seaborn as sns

sns.set(context='paper', style='ticks', palette='deep', font='sans-serif', font_scale=1.5, color_codes=True)
sns.set_style({"xtick.direction": "in", "ytick.direction": "in"})
sns.set_context(rc={'lines.markeredgewidth': 1})
​
#::: modules
import numpy as np
import matplotlib.pyplot as plt
import os, sys
# import scipy.ndimage
from scipy.interpolate import griddata
import matplotlib.ticker as mtick
​
​
​
###############################################################################
#::: plotting settings
###############################################################################
eps = 1e-12
font_scale = 1.5
SMALL_SIZE = 8 * font_scale
MEDIUM_SIZE = 10 * font_scale
BIGGER_SIZE = 12 * font_scale


def change_font(ax):
    ax.set_xlabel(ax.get_xlabel(), fontsize=BIGGER_SIZE)
    ax.set_ylabel(ax.get_ylabel(), fontsize=BIGGER_SIZE)
    ax.set_xticklabels(ax.get_xticks(), {'fontsize': MEDIUM_SIZE})
    ax.set_yticklabels(np.around(ax.get_yticks(), decimals=1), {'fontsize': MEDIUM_SIZE})


###############################################################################
#::: run
###############################################################################
period, rplanet, found = np.genfromtxt('tls_table/tls_table.csv', delimiter=',', unpack=True)
​
​
​
###############################################################################
#::: scatter plot
###############################################################################
plt.figure(figsize=(5, 5))
plt.scatter(period, rplanet, c=found)
​
​
​
​
###############################################################################
#::: histogram (normed)
###############################################################################
# bins=[np.arange(1,19+eps,1), np.arange(0.8,4.0+eps,0.20)]
# bins=[np.arange(1,19+eps,2), np.arange(0.8,4.0+eps,0.5)]
bins = [np.histogram_bin_edges(period, bins='auto'), np.histogram_bin_edges(rplanet, bins='auto')]
​
h1, x, y = np.histogram2d(period[found == 1], rplanet[found == 1], bins=bins)
h2, x, y = np.histogram2d(period[found == 0], rplanet[found == 0], bins=bins)
normed_hist = (100. * h1 / (h1 + h2))
​
fig, ax = plt.subplots(figsize=(6.5, 5))
im = plt.imshow(normed_hist.T, origin='lower', extent=(x[0], x[-1], y[0], y[-1]), interpolation='none', aspect='auto',
                cmap='viridis', vmin=0, vmax=100, rasterized=True)
# plt.plot(4.7,1.11,'o',color="firebrick",markersize=5,markeredgecolor='black',markeredgewidth=0.5)
# plt.plot(18.6,1.58,'o',color="firebrick",markersize=7,markeredgecolor='black',markeredgewidth=0.5)
# plt.vlines(x=4.7, ymin=1.04, ymax=1.18,linestyle='-', linewidth=2,color="black")
# plt.vlines(x=18.6, ymin=1.32, ymax=1.83,linestyle='-', linewidth=2,color="black")
plt.colorbar(im, label='Recovery rate (%)')
plt.yticks([0.5, 1.0, 1.5, 2.0])
plt.xticks([1, 2, 3, 4, 5])
plt.xlabel('Injected period (days)')
plt.ylabel(r'Injected radius (R$_\oplus$)')
change_font(ax)
​
plt.savefig('injection-recovery-test_new.png', bbox_inches='tight')
​
​
​
​
###############################################################################
#::: pyplot histograms (total counts)
###############################################################################
# fig, ax = plt.subplots(figsize=(6.5,5))
# h1,x,y,im = plt.hist2d(period[found==1], rplanet[found==1], bins=bins, cmap='Blues_r')
# plt.colorbar(im, label='Recovery rate (%)')
# plt.xlabel('Injected period (days)')
# plt.ylabel(r'Injected radius (R$_\oplus$)')
# change_font(ax)
​
​
# fig, ax = plt.subplots(figsize=(6.5,5))
# h2,x,y,im = plt.hist2d(period[found==0], rplanet[found==0], bins=bins, cmap='Blues_r')
# plt.colorbar(im, label='Recovery rate (%)')
# plt.xlabel('Injected period (days)')
# plt.ylabel(r'Injected radius (R$_\oplus$)')
# change_font(ax)
​
​
​
​
###############################################################################
#::: kdeplots
###############################################################################
fig, ax = plt.subplots(figsize=(6.5, 5))
ax = sns.kdeplot(period[found == 1], rplanet[found == 1], shade=True, cmap='Blues_r', cbar=True)
# ax.set(xlim=[1,20], ylim=[0.75,3.0])
plt.xlabel('Injected period (days)')
plt.ylabel(r'Injected radius (R$_\oplus$)')
change_font(ax)
​
​
# fig, ax = plt.subplots(figsize=(6.5,5))
# ax = sns.kdeplot(period[found==0], rplanet[found==0], shade=True, cmap='Blues', cbar=True)
# ax.set(xlim=[15,85], ylim=[0.8,2.0])
# plt.xlabel('Injected period (days)')
# plt.ylabel(r'Injected radius (R$_\oplus$)')
# change_font(ax)
​
​
​
​
###############################################################################
#::: others
###############################################################################
# plt.figure(figsize=(5,5))
# z = found.reshape(len(np.unique(period)), len(np.unique(rplanet)))
# plt.imshow(z.T, extent=(np.amin(period), np.amax(period), np.amin(rplanet), np.amax(rplanet)), aspect='auto', interpolation='gaussian', cmap='Blues')
# plt.xlabel('Period (days)')
# plt.ylabel(r'Radius (R$_\oplus$)')
​
# fig, ax = plt.subplots(figsize=(6.5,5))
# plt.tricontourf(period, rplanet, found, cmap='Blues_r')
# plt.xlabel('Injected period (days)')
# plt.ylabel(r'Injected radius (R$_\oplus$)')
​
​
# grid_x, grid_y = np.mgrid[np.amin(period):np.amax(period):100j, np.amin(rplanet):np.amax(rplanet):100j]
# grid_z = griddata((period, rplanet), found*100, (grid_x, grid_y), method='linear')
# fig, ax = plt.subplots(figsize=(6.5,5))
# im = plt.imshow(grid_z.T, origin='lower', extent=(np.amin(period), np.amax(period), np.amin(rplanet), np.amax(rplanet)), interpolation='none', aspect='auto', cmap='Blues_r', rasterized=True, vmin=0, vmax=100)
# plt.colorbar(im, label='Recovery rate (%)')
# plt.xlabel('Injected period (days)')
# plt.ylabel(r'Injected radius (R$_\oplus$)')
# change_font(ax)
#
# plt.savefig('injected_transit_search.pdf', bbox_inches='tight')
