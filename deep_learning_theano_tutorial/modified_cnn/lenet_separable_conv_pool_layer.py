# -*- coding: utf-8 -*-
"""
Created on Fri Oct 31 00:19:05 2014

@author: vivianapetrescu
"""

"""This tutorial introduces the LeNet5 neural network architecture
using Theano.  LeNet5 is a convolutional neural network, good for
classifying images. This tutorial shows how to build the architecture,
and comes with all the hyper-parameters you need to reproduce the
paper's MNIST results.


This implementation simplifies the model in the following ways:

 - LeNetConvPool doesn't implement location-specific gain and bias parameters
 - LeNetConvPool doesn't implement pooling by average, it implements pooling
   by max.
 - Digit classification is implemented with a logistic regression rather than
   an RBF network
 - LeNet5 was not fully-connected convolutions at second layer

References:
 - Y. LeCun, L. Bottou, Y. Bengio and P. Haffner:
   Gradient-Based Learning Applied to Document
   Recognition, Proceedings of the IEEE, 86(11):2278-2324, November 1998.
   http://yann.lecun.com/exdb/publis/pdf/lecun-98.pdf

"""
import scipy.io
import numpy as np
import time

import theano
import theano.tensor as T
from theano.tensor.signal import downsample
from theano.tensor.nnet import conv


class LeNetSeparableConvPoolLayer(object):
    """Pool Layer of a convolutional network """

    def __init__(self, rng, input, filter_shape, image_shape, poolsize=(2, 2),  Pstruct = None, b= None):
        """
        Allocate a LeNetConvPoolLayer with shared variable internal parameters.

        :type rng: numpy.random.RandomState
        :param rng: a random number generator used to initialize weights

        :type input: theano.tensor.dtensor4
        :param input: symbolic image tensor, of shape image_shape

        :type filter_shape: tuple or list of length 4
        :param filter_shape: (number of filters, num input feature maps,
                              filter height,filter width)

        :type image_shape: tuple or list of length 4
        :param image_shape: (batch size, num input feature maps,
                             image height, image width)

        :type poolsize: tuple or list of length 2
        :param poolsize: the downsampling (pooling) factor (#rows,#cols)
        """

        assert image_shape[1] == filter_shape[1]
        self.input = input

        # the bias is a 1D tensor -- one bias per output feature map

        # convolve input feature maps with filters

#(number of filters, num input feature maps,
#                              filter height,filter width)
#   10filters, 1, 20, h 1,
#   10filtrs, 1,20 , 1 ,w

#        pWeights = scipy.io.loadmat('file./experiments/setup_theano_tutorial/cnn_separable_model.mat')        
#        val = pWeights['P']
#        av = val[0,0]
#        sep_filters = av[1][2];
#        conv_out = conv.conv2d(input=input, filters=sep_filters,
#                filter_shape=(10,1,5,5), image_shape=image_shape)
        
        ## P is of size  U0, U1, U2
        ## rank*nbr_filters, rank*w_filter,rank*w_filter
        
        ## Pstruct is contains an array of PU,lambda for every channel!
        ## We look at the composition for the first channel in the beginning        
        fwidth = Pstruct[0].U[1].size/ Pstruct[0].rank
        fheight = Pstruct[0].U[2].size/ Pstruct[0].rank
        rank = Pstruct[0].rank
        nbr_filters = Pstruct[0].U[0].size / rank
        
        print 'width, height, rank ', fwidth, fheight, rank
     #   rank 4, w,h 3x3, nbr filter 7
        num_input_feature_maps = filter_shape[1]
        horizontal_filter_shape = (rank, num_input_feature_maps, fwidth, 1)
        horizontal_filters = np.ndarray(horizontal_filter_shape)
        print horizontal_filter_shape
        for chanel in range(num_input_feature_maps):
            print chanel
            print horizontal_filters[:, chanel,:, 0].shape
            horizontal_filters[:, chanel,:, 0] = Pstruct[chanel].U[1].reshape(rank,fwidth);
        horizontal_conv_out = conv.conv2d(input = input, filters = horizontal_filters,
                               filter_shape = horizontal_filter_shape, image_shape = image_shape)
                
        
        vertical_filter_shape = (rank, num_input_feature_maps, 1, fheight)
        vertical_filters = np.ndarray(vertical_filter_shape)        
        for chanel in range(num_input_feature_maps):
            vertical_filters[:, chanel,0, :] = Pstruct[chanel].U[2].reshape(rank, fheight);
    #    number of filters, num input feature maps,
        conv_out = conv.conv2d(input = horizontal_conv_out, filters = vertical_filters,
                               filter_shape = vertical_filter_shape, image_shape = image_shape)

        ## numberof images, number of filters, image width, image height
        input4D = np.zeros((image_shape[0], nbr_filters, image_shape[2], image_shape[3]))
        for f in range(nbr_filters):            
            temp = np.zeros((image_shape[0], image_shape[2], image_shape[3]))
            for chanel in range(num_input_feature_maps):
                 alphas = Pstruct[chanel].U[0].reshape(nbr_filters, rank)
                 for r in range(rank):
                     temp = temp + conv_out[:,r, :,:]* alphas[f, r];    
            input4D[:,f,:,:]  = temp
             
        # downsample each feature map individually, using maxpooling
        start = time.time()
        pooled_out = downsample.max_pool_2d(input=input4D,
                                            ds=poolsize, ignore_border=True)
        end = time.time()
        self.downsample_time = (end - start)*1000/ image_shape[0]
        
        # add the bias term. Since the bias is a vector (1D array), we first
        # reshape it to a tensor of shape (1,n_filters,1,1). Each bias will
        # thus be broadcasted across mini-batches and feature map
        # width & height
        self.output = T.tanh(pooled_out + theano.shared(b).dimshuffle('x', 0, 'x', 'x'))

        print 'pooled out shape ', pooled_out.shape
        # store parameters of this layer

