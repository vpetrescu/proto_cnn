# -*- coding: utf-8 -*-
"""
Created on Mon Nov 24 14:39:22 2014

@author: vivianapetrescu
"""

import convolutional_neural_network_settings_pb2 as pb_cnn
import numpy as np
import logging
import datetime
import os
import time
import theano.tensor as T
import theano
import misc
import patches

from google.protobuf import text_format

from test_voc_cnn import CNNTestVOC
from lenet_conv_pool_layer import LeNetConvPoolLayer
from lenet_layer_conv_pool_non_symbolic import LeNetLayerConvPoolNonSymbolic
from lenet_layer_conv_pool_separable_non_symbolic import LeNetLayerConvPoolSeparableNonSymbolic
from logistic_sgd import LogisticRegression
from mlp import HiddenLayer

class CNNTestVOCMitocondria(CNNTestVOC):
	def __init__(self, protofile, cached_weights_file, frame = None):
		self.frame = frame
		super(CNNTestVOCMitocondria, self).__init__(protofile, cached_weights_file)

	def load_samples(self):
	     path_to_data = '../data/' 
             if self.frame != None:
    	 	Vtest = (misc.tiffread(path_to_data + 'Volume_test.tif')/255.0)
    		Gtest = (misc.tiffread(path_to_data + 'Ground_truth_test.tif'))
    	 	Gtest[Gtest==255] = 1
         	areasize = 51
         	gap = (areasize -1)/2

        	# Extract all 51x51 patches from testing data
       	 	centers = patches.grid_patches_centers(Vtest[self.frame,:,:].shape, (areasize,areasize))
         	test_set_x = patches.get_many_patches(Vtest[self.frame,:,:], (areasize,areasize), centers, flat=True)
         	test_set_y = Gtest[self.frame][centers[:,0], centers[:,1]]
         	print 'Test set shape ', test_set_x.shape
	     else:
     	 	test_set_x = np.load(path_to_data +'test_set_x_fr1_51.npy')
     	 	test_set_y = np.load(path_to_data +'test_set_y_fr1_51.npy')
     	     
             test_set_x, test_set_y = self.shared_dataset((test_set_x, test_set_y))
	     return test_set_x, test_set_y