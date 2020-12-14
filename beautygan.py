# -*- coding: utf-8 -*-

import tensorflow as tf
import numpy as np
import os
import glob
from imageio import imread, imsave
import cv2
import argparse


class BeautyGAN:
    
    def __init__(self):
        self.img_size = 256
        self.makeups = glob.glob(os.path.join('imgs', 'makeup', '*.*'))
        
        tf.reset_default_graph()
        self.sess = tf.Session()
        self.sess.run(tf.global_variables_initializer())

        self.saver = tf.train.import_meta_graph(os.path.join('model', 'model.meta'))
        self.saver.restore(self.sess, tf.train.latest_checkpoint('model'))

        self.graph = tf.get_default_graph()
        self.X = self.graph.get_tensor_by_name('X:0')
        self.Y = self.graph.get_tensor_by_name('Y:0')
        self.Xs = self.graph.get_tensor_by_name('generator/xs:0')


    def preprocess(self, img):
        return (img / 255. - 0.5) * 2

    def deprocess(self, img):
        return (img + 1) / 2


    def run(self, img):
        size = self.img_size
        no_makeup = cv2.resize(imread(img), (size, size))
        X_img = np.expand_dims(self.preprocess(no_makeup), 0)

        # result = np.ones((2*size, (len(self.makeups) + 1) * size, 3))
        # result[size: 2 *  size, :size] = no_makeup / 255.

        
        paths = []
        guideline = []
        for i in range(len(self.makeups)):
            result = np.ones((size, size,3))
            makeup = cv2.resize(imread(self.makeups[i]), (self.img_size, self.img_size))
            Y_img = np.expand_dims(self.preprocess(makeup), 0)
            Xs_ = self.sess.run(self.Xs, feed_dict={self.X: X_img, self.Y: Y_img})
            Xs_ = self.deprocess(Xs_)
            result = Xs_[0]
            #result[:size, (i + 1) * size: (i + 2) * size] = makeup / 255.
            #result[size: 2 * size, (i + 1) * size: (i + 2) * size] = Xs_[0]
            guideline.append(result)
            path = 'tmp/' + str(i) + '.png'
            imsave(path, result)
            paths.append(path)
            

        # imsave(path, result)
        return paths


#bg = BeautyGAN()

#bg.run('imgs/no_makeup/vSYYZ306.png')