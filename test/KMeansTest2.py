# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt, numpy as np
from scipy.cluster.vq import vq, kmeans, whiten

features  = np.array([[ 1.9 ],
                   [ 1.5 ],
                   [ 0.8 ],
                   [ 0.4 ],
                   [ 0.1 ],
                   [ 0.2 ],
                   [ 2.0 ],
                   [ 0.3 ],
                   [ 1.0 ]])

whitened = whiten(features)

# Find 2 clusters in the data
codebook, distortion = kmeans(whitened, 2)
# Plot whitened data and cluster centers in red
y = whitened[ :, 0]
plt.scatter( [0]*len(y), y )
y = codebook[ :, 0]
plt.scatter( [0]*len(y), y, c='r')
plt.show()