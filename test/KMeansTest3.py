# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt, numpy as np
from scipy.cluster.vq import vq, kmeans, whiten

#features  = np.array( [[1], [2], [3], [4]] )

features = np.array( [ 1, 2, 3, 4 ] )
features = features.reshape( (-1, 1) )
#features = features.reshape( (len(features), 1) )

whitened = whiten(features)

print( 'std = ', np.std( features) )
print( whitened )
print( np.std(features)*whitened )

# Find 2 clusters in the data
codebook, distortion = kmeans(whitened, 2)
print( 'codebook = ', codebook )

# Plot whitened data and cluster centers in red
y = whitened[ :, 0]
plt.scatter( [0]*len(y), y )
y = codebook[ :, 0]
plt.scatter( [0]*len(y), y, c='r')
plt.show()