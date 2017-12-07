# -*- coding: utf-8 -*-

###################################
##  Written by Shane Grigsby     ##
##  Email: refuge@rocktalus.com  ##
##  Date:  May 2013              ##
###################################


## Imports ##

import sys
import scipy
import pickle
import numpy as np
from sklearn.neighbors import BallTree

from sklearn.datasets.samples_generator import make_blobs
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt


## Main Class ##


class setOfObjects():

    """Build balltree data structure with processing index from given data in preparation for OPTICS Algorithm

    Parameters
    ----------
    data_points: array [n_samples, n_features]"""

    def __init__(self, data_points, metric="euclidean"):
        self.data = data_points
        self._balltree = BallTree(data_points, metric=metric)
        self._n = len(self.data)
        # Start all points as 'unprocessed' ##
        self._processed = scipy.zeros((self._n, 1), dtype=bool)
        self._reachability = scipy.ones(self._n) * scipy.inf  # Important! ##
        self._core_dist = scipy.ones(self._n) * scipy.nan
        # Might be faster to use a list? ##
        self._index = scipy.array(range(self._n))
        self._nneighbors = scipy.ones(self._n, dtype=int)
        # Start all points as noise ##
        self._cluster_id = -scipy.ones(self._n, dtype=int)
        self._is_core = scipy.ones(self._n, dtype=bool)
        self._ordered_list = []  # DO NOT switch this to a hash table, ordering is important ###

    ## Used in prep step ##
    def _set_neighborhood(self, point, epsilon):
        self._nneighbors[point] = self._balltree.query_radius(
            np.array(self.data[point]).reshape(1, -1), epsilon, count_only=1)[0]

    ## Used in prep step ##
    def _set_core_dist(self, point, MinPts):
        self._core_dist[point] = self._balltree.query(
            np.array(self.data[point]).reshape(1, -1), MinPts)[0][0][-1]

## Prep Method ##

### Paralizeable! ###


def prep_optics(SetofObjects, epsilon, MinPts):
    """Prep data set for main OPTICS loop

    Parameters
    ----------
    SetofObjects: Instantiated instance of 'setOfObjects' class
    epsilon: float or int
        Determines maximum object size that can be extracted. Smaller epsilons reduce run time
    MinPts: int
        The minimum number of samples in a neighborhood to be considered a core point

    Returns
    -------
    Modified setOfObjects tree structure"""

    for i in SetofObjects._index:
        SetofObjects._set_neighborhood(i, epsilon)
    for j in SetofObjects._index:
        if SetofObjects._nneighbors[j] >= MinPts:
            SetofObjects._set_core_dist(j, MinPts)
    print('Core distances and neighborhoods prepped for ' +
          str(SetofObjects._n) + ' points.')

## Main OPTICS loop ##


def build_optics(SetOfObjects, epsilon, MinPts, Output_file_name):
    """Builds OPTICS ordered list of clustering structure

    Parameters
    ----------
    SetofObjects: Instantiated and prepped instance of 'setOfObjects' class
    epsilon: float or int
        Determines maximum object size that can be extracted. Smaller epsilons reduce run time. This should be equal to epsilon in 'prep_optics'
    MinPts: int
        The minimum number of samples in a neighborhood to be considered a core point. Must be equal to MinPts used in 'prep_optics'
    Output_file_name: string
        Valid path where write access is available. Stores cluster structure"""

    for point in SetOfObjects._index:
        if SetOfObjects._processed[point] == False:
            expandClusterOrder(SetOfObjects, point, epsilon,
                               MinPts, Output_file_name)

## OPTICS helper functions; these should not be public ##

### NOT Paralizeable! The order that entries are written to the '_ordered_list' is important! ###


def expandClusterOrder(SetOfObjects, point, epsilon, MinPts, Output_file_name):
    if SetOfObjects._core_dist[point] <= epsilon:
        while not SetOfObjects._processed[point]:
            SetOfObjects._processed[point] = True
            SetOfObjects._ordered_list.append(point)
            ## Comment following two lines to not write to a text file ##
            with open(Output_file_name, 'a') as file:
                # file.write(
                #     (str(point) + ', ' + str(SetOfObjects._reachability[point]) + '\n'))
                ## Keep following line! ##
                point = set_reach_dist(SetOfObjects, point, epsilon)
        print('Object Found!')
    else:
        SetOfObjects._processed[point] = True    # Probably not needed... #


### As above, NOT paralizable! Paralizing would allow items in 'unprocessed' list to switch to 'processed' ###
def set_reach_dist(SetOfObjects, point_index, epsilon):

    ###  Assumes that the query returns ordered (smallest distance first) entries     ###
    ###  This is the case for the balltree query...                                   ###
    ###  ...switching to a query structure that does not do this will break things!   ###
    ###  And break in a non-obvious way: For cases where multiple entries are tied in ###
    ###  reachablitly distance, it will cause the next point to be processed in       ###
    ###  random order, instead of the closest point. This may manefest in edge cases  ###
    ###  where different runs of OPTICS will give different ordered lists and hence   ###
    ###  different clustering structure...removing reproducability.                   ###

    distances, indices = SetOfObjects._balltree.query(np.array(SetOfObjects.data[point_index]).reshape(1, -1),
                                                      SetOfObjects._nneighbors[point_index])

    ## Checks to see if there more than one member in the neighborhood ##
    if scipy.iterable(distances):

        ## Masking processed values ##
        unprocessed = indices[(SetOfObjects._processed[indices] < 1)[0].T]
        rdistances = scipy.maximum(distances[(SetOfObjects._processed[indices] < 1)[
                                   0].T], SetOfObjects._core_dist[point_index])
        SetOfObjects._reachability[unprocessed] = scipy.minimum(
            SetOfObjects._reachability[unprocessed], rdistances)

        ### Checks to see if everything is already processed; if so, return control to main loop ##
        if unprocessed.size > 0:
            ### Define return order based on reachability distance ###
            return sorted(zip(SetOfObjects._reachability[unprocessed], unprocessed), key=lambda reachability: reachability[0])[0][1]
        else:
            return point_index
    else:  # Not sure if this else statement is actaully needed... ##
        return point_index

## Extract DBSCAN Equivalent cluster structure ##

# Important: Epsilon prime should be less than epsilon used in OPTICS #


def ExtractDBSCAN(SetOfObjects, epsilon_prime):
    """Performs DBSCAN equivalent extraction for arbitrary epsilon. Can be run multiple times.

    Parameters
    ----------
    SetOfObjects: Prepped and build instance of setOfObjects
    epsilon_prime: float or int
        Must be less than or equal to what was used for prep and build steps

    Returns
    -------
    Modified setOfObjects with cluster_id and is_core attributes."""

    # Start Cluster_id at zero, incremented to '1' for first cluster
    cluster_id = 0
    for entry in SetOfObjects._ordered_list:
        if SetOfObjects._reachability[entry] > epsilon_prime:
            if SetOfObjects._core_dist[entry] <= epsilon_prime:
                cluster_id += 1
                SetOfObjects._cluster_id[entry] = cluster_id
                # Two gives first member of the cluster; not meaningful, as first cluster members do not correspond to centroids #
                ## SetOfObjects._is_core[entry] = 2     ## Breaks boolean array :-( ##
            else:
                # This is only needed for compatibility for repeated scans. -1 is Noise points #
                SetOfObjects._cluster_id[entry] = -1
        else:
            SetOfObjects._cluster_id[entry] = cluster_id
            if SetOfObjects._core_dist[entry] <= epsilon_prime:
                # One (i.e., 'True') for core points #
                SetOfObjects._is_core[entry] = 1
            else:
                # Zero (i.e., 'False') for non-core, non-noise points #
                SetOfObjects._is_core[entry] = 0

##### End Algorithm #####


def plotFeatureOPTICS(data, clusters, clusterNum):
    matClusters = np.mat(clusters)
    fig = plt.figure()
    ax = fig.add_subplot(111)
    colors = ['blue', 'green', 'yellow', 'brown',
              'red', 'purple', 'orange', 'grey']

    noise_data = data[np.nonzero(matClusters == -1)[1], :]  # 噪声点
    # noise_data = data[np.argwhere(matClusters <= 0)[:, 1], :]  # 噪声点
    ax.scatter(noise_data[:, 1], noise_data[:, 0],
               c="black", s=3, marker='v', label='noise')  # 画噪声点，颜色为黑色
    for i in range(0, clusterNum + 1):  # 画其他簇
        colorStyle = colors[i % len(colors)]
        subCluster = data[np.nonzero(matClusters == i)[1], :]
        ax.scatter(subCluster[:, 1], subCluster[:, 0],
                   c=colorStyle, s=2)
    plt.legend(loc='best')
    plt.show()


def test():
    centers = [[1, 1], [-1, -1], [1, -1]]
    X, labels_true = make_blobs(n_samples=750, centers=centers, cluster_std=0.4,
                                random_state=0)
    X1 = StandardScaler().fit_transform(X)
    # plotFeature(X, labels_true, len(set(labels_true)))
    # Load the data into the classifier object
    testtree = setOfObjects(X1)
    prep_optics(testtree, 30, 10)
    build_optics(testtree, 30, 10, './testing_may6.txt')
    ExtractDBSCAN(testtree, 0.2)
    core_samples = testtree._index[testtree._is_core[:] > 0]
    labels = testtree._cluster_id[:]
    n_clusters_ = max(testtree._cluster_id)
    print(labels)
    # print(labels_true)

    # import pylab as pl

    # # Black removed and is used for noise instead.
    # unique_labels = set(testtree._cluster_id[:])  # modifed from orginal #
    # colors = pl.cm.Spectral(np.linspace(0, 1, len(unique_labels)))
    # for k, col in zip(unique_labels, colors):
    #     if k == -1:
    #         # Black used for noise.
    #         col = 'k'
    #         markersize = 6
    #     class_members = [index[0] for index in np.argwhere(labels == k)]
    #     for index in class_members:
    #         x = X[index]
    #         if index in core_samples and k != -1:
    #             markersize = 14
    #         else:
    #             markersize = 6
    #         pl.plot(x[0], x[1], 'o', markerfacecolor=col,
    #                 markeredgecolor='k', markersize=markersize)

    # pl.title('Estimated number of clusters: %d' % n_clusters_)
    # pl.show()


if __name__ == "__main__":
    test()
