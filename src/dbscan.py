import numpy as np
import matplotlib.pyplot as plt
import math
import time
import pprint as pp
from sklearn.cluster import DBSCAN
from math import radians, cos, sin, asin, sqrt

UNCLASSIFIED = False
NOISE = 0


def haversine(lon1, lat1, lon2, lat2):  # 经度1，纬度1，经度2，纬度2 （十进制度数）
    """ 
    Calculate the great circle distance between two points  
    on the earth (specified in decimal degrees) 
    """
    # 将十进制度数转化为弧度
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine公式
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * asin(sqrt(a))
    r = 6371  # 地球平均半径，单位为公里
    return c * r * 1000


def Is_neighbor(A, B, eps):
    '''
    input: point A,B;radius;
    return: True,False
    '''
    lat1 = A[0]
    lon1 = A[1]
    lat2 = B[0]
    lon2 = B[1]

    return haversine(lon1, lat1, lon2, lat2) <= eps


def regionQuery(data, p_Id, eps):
    '''
    input: dataset,id of p,radius
    return: all points id within eps-neighborhood(include p)
    '''
    nPoints = np.shape(data)[0]
    seeds = []
    for i in range(nPoints):
        if Is_neighbor(data[i, :], data[p_Id, :], eps):
            seeds.append(i)
    return seeds


def expandCluster(data, clusterResult, pointId, clusterId, eps, minPts):
    '''
    input: 数据集,聚类结果，待分类的点,当前簇id,半径，最小点个数
    return:是否成功分类(若该点是核心点，则成功)
    '''
    seeds = regionQuery(data, pointId, eps)
    if len(seeds) < minPts:  # 不是核心点，暂时设为噪声(不一定真是噪声)
        clusterResult[pointId] = NOISE
        return False  # 返回
    # 否则该点是核心点
    # 把该点，以及该点的邻域内的点划分到clusterId
    clusterResult[pointId] = clusterId
    for seed in seeds:
        clusterResult[seed] = clusterId
    # 持续扩张
    while len(seeds) > 0:
        currentPoint = seeds[0]
        queryResults = regionQuery(data, currentPoint, eps)
        if len(queryResults) >= minPts:
            # 如果该点是核心点，则处理该核心点邻域内的点
            for i in range(len(queryResults)):
                resultPoint = queryResults[i]
                # 如果该点未被分类，则加入到当前簇，扩张
                if clusterResult[resultPoint] == UNCLASSIFIED:
                    clusterResult[resultPoint] = clusterId
                    seeds.append(resultPoint)
                # 如果该点是噪声，则加入到当前簇，由于它不是核心点，没必要扩张
                elif clusterResult[resultPoint] == NOISE:
                    clusterResult[resultPoint] = clusterId
        seeds = seeds[1:]
    return True


def dbscan(data, eps, minPts):
    '''
    DBSCAN,簇0是噪声
    input:数据集，半径，最小点个数
    return:聚类结果，聚类的数目
    '''
    clusterId = 1
    nPoints = np.shape(data)[0]
    clusterResult = [UNCLASSIFIED] * nPoints
    for pointId in range(nPoints):
        if clusterResult[pointId] == UNCLASSIFIED:
            if expandCluster(data, clusterResult, pointId, clusterId, eps, minPts):
                print("cluster {} is finished!".format(str(clusterId)))
                clusterId += 1
    print("clustering is finished!total {} clusters".format(str(clusterId - 1)))
    return clusterResult, clusterId - 1


def plotFeature(data, clusters, clusterNum):
    # print(data)
    # print(clusters)
    matClusters = np.mat(clusters)
    fig = plt.figure()
    ax = fig.add_subplot(111)
    colors = ['blue', 'green', 'yellow', 'brown',
              'red', 'purple', 'orange', 'grey']

    noise_data = data[np.nonzero(matClusters == 0)[1], :]  # 噪声点
    # noise_data = data[np.argwhere(matClusters <= 0)[:, 1], :]  # 噪声点
    ax.scatter(noise_data[:, 1], noise_data[:, 0],
               c="black", s=3, marker='v', label='noise')  # 画噪声点，颜色为黑色
    for i in range(1, clusterNum + 1):  # 画其他簇
        colorStyle = colors[i % len(colors)]
        subCluster = data[np.nonzero(matClusters == i)[1], :]
        ax.scatter(subCluster[:, 1], subCluster[:, 0],
                   c=colorStyle, s=2)
    plt.legend(loc='best')
    plt.show()
