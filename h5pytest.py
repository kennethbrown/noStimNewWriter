import h5py
import numpy as np

f = h5py.File('test.hdf5', 'w')
dataSet = f.create_dataset('test', (10000,))
dataSet[0:1000] = np.zeros(1000)
f.close()
