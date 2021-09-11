import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from scipy import stats
import scipy.integrate as integrate

def read_data(file_name):
    f = open(file_name, 'r')
    line1 = f.readline()
    names1 = line1.replace('#', ' ').split()
    data_read = pd.read_csv(f, sep="\s+", names=line1.replace('#', ' ').split(), skiprows=0)
    return data_read

def draw_histo(data, field_name, title):
    fig, ax0 = plt.subplots(ncols=1, nrows=1)
    x_v1, bins_v1, p_v1 = ax0.hist(data[field_name], bins = 50, density=True, label='Histogram')
    mu_v1, sigma_v1 = stats.norm.fit(data[field_name])
    best_fit_line_v1 = stats.norm.pdf(bins_v1, mu_v1, sigma_v1)
    ax0.plot(bins_v1, best_fit_line_v1, label='$\mu$ = {0:6.3f}\n$\sigma$ = {1:6.3f}'.format(mu_v1, sigma_v1))
    ax0.legend()
    plt.title(title)
    plt.show()
    print("mu = {0}, sigma = {1}".format(mu_v1, sigma_v1))
    return ax0

def draw_histo_multi(data_items, field_name, titles, title):
    fig, ax0 = plt.subplots(ncols=1, nrows=1)
    idx = 0
    for data in data_items:
        x_v1, bins_v1, p_v1 = ax0.hist(data[field_name], bins = 50, density=True)
        mu_v1, sigma_v1 = stats.norm.fit(data[field_name])
        best_fit_line_v1 = stats.norm.pdf(bins_v1, mu_v1, sigma_v1)
        ax0.plot(bins_v1, best_fit_line_v1, label=titles[idx])
        idx=idx+1
        ax0.legend()
    plt.title(title)
    plt.show()

def draw_histo_center(data, field_name, title):
    fig, ax0 = plt.subplots(ncols=1, nrows=1)
    values, bins, p = ax0.hist(data[field_name], bins = 100, density=True, label='Histogram')
    mu, sigma = stats.norm.fit(data[field_name])
    bin_centers = 0.5*(bins[1:] + bins[:-1])
    pdf = stats.norm.pdf(x = bin_centers, loc=mu, scale=sigma)
    ax0.plot(bin_centers, pdf, label="PDF")
    ax0.legend()
    plt.title(title)
    plt.show()
    print("mu = {0}, sigma = {1}".format(mu, sigma))
    return ax0

def draw_histo_center_multi(data_items, field_name, titles, title):
    fig, ax0 = plt.subplots(ncols=1, nrows=1)
    idx = 0
    for data in data_items:
        values, bins, p = ax0.hist(data[field_name], bins = 100, density=True)
        mu, sigma = stats.norm.fit(data[field_name])
        bin_centers = 0.5*(bins[1:] + bins[:-1])
        pdf = stats.norm.pdf(x = bin_centers, loc=mu, scale=sigma)
        ax0.plot(bin_centers, pdf, label=titles[idx])
        ax0.legend()
        idx += 1
    plt.title(title)
    plt.show()

def get_histo_bins(data, bin_number, field_name):
    fig = matplotlib.figure.Figure()
    ax = matplotlib.axes.Axes(fig, (0,0,0,0))
    values, bins, p = ax.hist(data[field_name], bins = bin_number, density = True)
    del ax, fig
    return values, bins, p
def get_histo_bins_bin(data, given_bins, field_name):
    fig = matplotlib.figure.Figure()
    ax = matplotlib.axes.Axes(fig, (0,0,0,0))
    #print('given_bins = {0}'.format(len(given_bins)))
    values, bins, p = ax.hist(data[field_name], bins = given_bins, density = True)
    #print('bins = {0}'.format(len(bins)))
    del ax, fig
    return values, bins, p

def integrate_histo(data, bin_number, field_name):
    values, bins, p = get_histo_bins(data, bin_number, field_name)
    bin_centers = 0.5*(bins[1:]+bins[:-1])
    int_value = integrate.simpson(values, bin_centers)
    return int_value

def find_bins(small_size, small_bins, big_size, big_bins):
    start_idx = np.floor((big_bins[0]-small_bins[0])/small_size)
    bin_edge = small_bins[0] + start_idx * small_size
    idx = 0
    offset_idx = start_idx
    big_bin_number = big_bins.size
    new_bins = []
    new_bins.append(bin_edge)
    while new_bins[idx] < big_bins[big_bin_number -1]:
        idx += 1
        new_bins.append(new_bins[idx-1] + small_size)
    return new_bins

def merge_bins(bins1, values1, bins2, values2, bin_size):
    bins1_number = len(bins1)
    bins2_number = len(bins2)
    #print('bins1_number = {0}, values1 size = {1}'.format(bins1_number, len(values1)))
    #print('bins2_number = {0}, values2 size = {1}'.format(bins2_number, len(values2)))
    bins1_start = bins1[0]
    bins1_end = bins1[bins1_number -1]
    bins2_start = bins2[0]
    bins2_end = bins2[bins2_number -1]
    bin_start = min(bins1_start, bins2_start)
    bin_end = max(bins1_end, bins2_end)
    merged_bins = []
    merged_values1 = []
    merged_values2 = []
    bin_edge = bin_start
    bins1_idx = 0
    bins2_idx = 0
    while bin_edge < bin_end:
        merged_bins.append(bin_edge)
        if bin_edge < bins1_start or bin_edge >= bins1_end:
            merged_values1.append(0)
        elif bin_edge < bins1_end and bins1_idx < bins1_number -1:
            merged_values1.append(values1[bins1_idx])
            bins1_idx += 1
        if bin_edge < bins2_start or bin_edge >= bins2_end:
            merged_values2.append(0)
        elif bin_edge < bins2_end and bins2_idx < bins2_number - 1:
            merged_values2.append(values2[bins2_idx])
            bins2_idx += 1
        bin_edge += bin_size
    return merged_bins, merged_values1, merged_values2

def integrate_diff_histo(data1, data2, bin_number, field_name):
    #print(data1)
    #print(data2)
    values1, bins1, p1 = get_histo_bins(data1, bin_number, field_name)
    values2, bins2, p2 = get_histo_bins(data2, bin_number, field_name)
    #print('bins1 = {0}'.format(bins1))
    #print('bins2 = {0}'.format(bins2))
    bin_size1 = bins1[1] - bins1[0]
    bin_size2 = bins2[1] - bins2[0]
    bin_size = bin_size1
    #print('size 1 = {0}'.format(bin_size1))
    #print('size 2 = {0}'.format(bin_size2))
    if bin_size1 < bin_size2: # recalculate for data2
        new_bins2 = find_bins(bin_size1, bins1, bin_size2, bins2)
        values2, bins2, p2 = get_histo_bins_bin(data2, new_bins2, field_name)
        #print('new_bins2 size = {0}'.format(new_bins2[1]-new_bins2[0]))
        #print('new_bins2 number = {0}, old = {1}'.format(len(new_bins2), len(bins2)))
    elif bin_size1 > bin_size2: # recalculate for data1
        bin_size = bin_size2
        new_bins1 = find_bins(bin_size2, bins2, bin_size1, bins1)
        values1, bins1, p1 = get_histo_bins_bin(data1, new_bins1, field_name)
        #print('new_bins1 size = {0}'.format(new_bins1[1]-new_bins1[0]))
        #print('new_bins1 number = {0}, old = {1}'.format(len(new_bins1), len(bins1)))
    merged_bins, merged_values1, merged_values2 = merge_bins(bins1, values1, bins2, values2, bin_size)
    #print('merged_bins size = {0}'.format(len(merged_bins)))
    #print('merged_values1 size = {0}'.format(len(merged_values1)))
    #print('merged_values2 size = {0}'.format(len(merged_values2)))
    # zero appends 
    if len(merged_values1) < len(merged_bins):
        for idx in range(len(merged_bins)-len(merged_values1)):
            merged_values1.append(0)
    if len(merged_values2) < len(merged_bins):
        for idx in range(len(merged_bins)-len(merged_values2)):
            merged_values2.append(0)
    min_values = []
    for idx in range(len(merged_bins)):
        min_values.append(min(merged_values1[idx], merged_values2[idx]))
    #print('min_values size = {0}'.format(len(min_values)))
    confusion = integrate.simpson(min_values, merged_bins)
    #print('confusion = {0}'.format(confusion))
    return confusion
