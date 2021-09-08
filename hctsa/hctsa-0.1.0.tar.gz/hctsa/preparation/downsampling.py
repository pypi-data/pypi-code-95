#!/usr/bin/env python3

# Source: https://skemman.is/bitstream/1946/15343/3/SS_MSthesis.pdf

# Largest-Triangle-One-Bucket
'''
Algorithm 4.1 Largest-Triangle-One-Bucket
Require: data . The original data
Require: threshold . Number of data points to be returned
1: Rank every point in regard to its effective area
2: Split the data into the same number of buckets as the threshold
3: for each bucket do
4: Select the point with the highest rank within the bucket
5: end for
6: Finally make sure that the first and last data points in the original data are also
the first and last data points in the downsampled data.
'''
def ltob(raw_timeseries_data, threshold=False):
  if treshold:
    ...

  else:
    ...

  return _timeseries_data

# Largest-Triangle-Three-Buckets
'''
Algorithm 4.2 Largest-Triangle-Three-Buckets
Require: data . The original data
Require: threshold . Number of data points to be returned
1: Split the data into equal number of buckets as the threshold but have the first
bucket only containing the first data point and the last bucket containing only
the last data point
2: Select the point in the first bucket
3: for each bucket except the first and last do
4: Rank every point in the bucket by calculating the area of a triangle it forms
with the selected point in the last bucket and the average point in the next
bucket
5: Select the point with the highest rank within the bucket
6: end for
7: Select the point in the last bucket . There is only one
'''
def lttb(raw_timeseries_data, threshold=False):
  if treshold:
    ...
    
  else:
    ...

  return _timeseries_data

# Largest-Triangle-Dynamic
'''
Algorithm 4.3 Largest-Triangle-Dynamic
Require: data . The original data
Require: threshold . Number of data points to be returned
1: Split the data into equal number of buckets as the threshold but have the first
bucket only containing the first data point and the last bucket containing only
the last data point . First and last buckets are then excluded in the bucket
resizing
2: Calculate the SSE for the buckets accordingly . With one point in adjacent
buckets overlapping
3: while halting condition is not met do . For example, using formula 4.2
4: Find the bucket F with the highest SSE
5: Find the pair of adjacent buckets A and B with the lowest SSE sum . The
pair should not contain F
6: Split bucket F into roughly two equal buckets . If bucket F contains an odd
number of points then one bucket will contain one more point than the other
7: Merge the buckets A and B
8: Calculate the SSE of the newly split up and merged buckets
9: end while.
10: Use the Largest-Triangle-Three-Buckets algorithm on the resulting bucket configuration to select one point per buckets
'''
def ltd(raw_timeseries_data, threshold=False):
  if treshold:
    ...
    
  else:
    ...

  return _timeseries_data