#!/usr/local/bin/python2.7

import argparse as ap
import cv2
import imutils
import numpy as np
import sys
import os
from sklearn import svm, grid_search
from sklearn.svm import LinearSVC, SVC
from sklearn.externals import joblib
from scipy.cluster.vq import *
from sklearn.preprocessing import StandardScaler

# test
#parameters = {'kernel':('linear', 'rbf'), 'C':[1, 10, 100, 1000]}
#svr=SVC()
#clf = grid_search.GridSearchCV(svr, parameters)
#test

# Get the path of the training set
parser = ap.ArgumentParser()
parser.add_argument("-t", "--trainingSet", help="Path to Training Set", required="True")
args = vars(parser.parse_args())

"""
# Get the training classes names and store them in a list
#train_path = args["trainingSet"]
#training_names = os.listdir(train_path)

# Get all the path to the images and save them in a list
# image_paths and the corresponding label in image_paths
image_paths = []
image_classes = []
class_id = 0
for training_name in training_names:
    dir = os.path.join(train_path, training_name)
    class_path = imutils.imlist(dir)
    image_paths+=class_path
    image_classes+=[class_id]*len(class_path)
    class_id+=1
"""

# Get the labels and paths from a caffe imagelist file
# Things needed are image_paths and image_classes
image_paths = []
image_classes = []
with open('train') as f:
    lines = f.readlines()
for line in lines:
    tmp = line.split()
    image_paths.append(tmp[0])
    image_classes.append(int(tmp[1]))
sys.stdout.flush()
print image_paths[0]
sys.stdout.flush()
print image_classes[0]
sys.stdout.flush()
print len(image_paths)
sys.stdout.flush()
print len(image_classes)
sys.stdout.flush()

# Create feature extraction and keypoint detector objects
fea_det = cv2.FeatureDetector_create("SIFT")
des_ext = cv2.DescriptorExtractor_create("SIFT")

# List where all the descriptors are stored
des_list = []

# Very memory consuming for large datasets
count = 0
for image_path in image_paths:
    im = cv2.imread(image_path)
    im = cv2.resize(im, (128, 128))

    kpts = fea_det.detect(im)
    kpts, des = des_ext.compute(im, kpts)
    #print sys.getsizeof(des)/1000000.0
    des_list.append((image_path, des))

    if count % 100 == 0:
	sys.stdout.flush()
        print  count
	sys.stdout.flush()
    count += 1

# Stack all the descriptors vertically in a numpy array
descriptors = des_list[0][1]
count = 0
for image_path, descriptor in des_list[1:]:
    descriptors = np.vstack((descriptors, descriptor))
    if count % 1000 == 0:
	sys.stdout.flush()
        print  count
	sys.stdout.flush()
    count += 1
sys.stdout.flush()
print type(descriptors)
sys.stdout.flush()
print len(descriptors)
sys.stdout.flush()
print descriptors.shape
sys.stdout.flush()
print descriptors[0]
sys.stdout.flush()

# Perform k-means clustering
k = 100
voc, variance = kmeans(descriptors, k, 1)

# Calculate the histogram of features
im_features = np.zeros((len(image_paths), k), "float32")
for i in xrange(len(image_paths)):
    words, distance = vq(des_list[i][1],voc)
    for w in words:
        im_features[i][w] += 1

# Perform Tf-Idf vectorization
nbr_occurences = np.sum( (im_features > 0) * 1, axis = 0)
idf = np.array(np.log((1.0*len(image_paths)+1) / (1.0*nbr_occurences + 1)), 'float32')

# Scaling the words
stdSlr = StandardScaler().fit(im_features)
im_features = stdSlr.transform(im_features)

# Train the Linear SVM
#clf = LinearSVC()
#clf = SVC()
parameters = {'kernel':('linear', 'rbf'), 'C':[1, 10, 100, 1000]}
svr=SVC()
clf = grid_search.GridSearchCV(svr, parameters)
clf.fit(im_features, np.array(image_classes))

# Save the SVM
#joblib.dump((clf, training_names, stdSlr, k, voc), "bof.pkl", compress=3)
joblib.dump((clf, image_classes, stdSlr, k, voc), "bof_newdataset_svc.pkl", compress=3)

