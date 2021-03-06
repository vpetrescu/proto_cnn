#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 21 16:19:55 2014

@author: vivianapetrescu
"""

import argparse
import sys
import src.core

from mnist_train_cnn  import CNNTrainTPmnist
from mnist_retrain_cnn import CNNRetrainTPmnist
from mnist_test_cnn import CNNTestTPmnist

def main():
    print 'Number of arguments:', len(sys.argv)
    print 'Arguments list:', str(sys.argv)

    parser = argparse.ArgumentParser()
    parser.add_argument('-p','--proto_file', help="path to proto file", dest='prototxt_file', required=True)
    parser.add_argument('-w','--cached_weights_file', help="path to weights file", dest='cached_weights_file', required=True)
    parser.add_argument('-r','--run_mode', help="mode 0 for train\n 1 for test, 2 for train and test", dest='mode', type = int, required=True)
    results = parser.parse_args()

    print 'prototxt file is ', results.prototxt_file
    print 'weights file is', results.cached_weights_file
    print 'run mode', results.mode

    if results.mode == 0 or results.mode == 2:
    	cnn = CNNTrainTPmnist(results.prototxt_file, results.cached_weights_file)
    	cnn.build_model()
    	cnn.train_model()
    if results.mode == 1 or results.mode == 2:
    	cnn = CNNTestTPmnist(results.prototxt_file, results.cached_weights_file)
    	cnn.test_model()
    if results.mode == 3:
	cnn = CNNRetrainTPmnist(results.prototxt_file, results.cached_weights_file)
        cnn.build_model()
        cnn.retrain_model()

if __name__ == '__main__':
    main()




