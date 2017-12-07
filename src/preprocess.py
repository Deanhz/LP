'''
Dean
2017.11.21
'''
import numpy as np
import time
import os
from dbscan import *
from OPTICS import *
from scatterPlot import *
import datetime
from math import radians, cos, sin, asin, sqrt

INDIR = '../Data'
OUTDIR = r'../cleaned_data'


def alluser(func):
    userList = sorted(os.listdir(INDIR))
    for user in userList:
        func(user)


def userClean(user):
    '''
    function:
    1.extract latitude,longtitude,date,time
    2.add trajectory number
    3.extract data for Beijing
    Example:
    userClean('../Data')
    '''
    dataDir = INDIR + "/" + user + "/Trajectory"
    trajectories = sorted(os.listdir(dataDir))
    fout = open(OUTDIR + "/" + user, "w")
    for trajIndex, traj in enumerate(trajectories):
        trajfile = dataDir + "/" + traj
        f = open(trajfile)
        for lineIndex, line in enumerate(f):
            if lineIndex < 6:
                continue
            line_list = line.strip().split(',')
            latitude = float(line_list[0])
            longitude = float(line_list[1])
            if (116.2 <= longitude <= 116.6) and (39.7 <= latitude <= 40.1):
                date = line_list[5]
                time = line_list[6]
                trajNum = trajIndex
                print(str(latitude) + "\t" + str(longitude) + "\t" +
                      date + "\t" + time + "\t" + str(trajNum))
                fout.write(str(latitude) + "\t" + str(longitude) +
                           "\t" + date + "\t" + time + "\t" +
                           str(trajNum) + "\t" + str(user) + "\n")


def clusteringDBSCAN(user, e, m):
    '''
    DBSCAN,簇0是噪声
    input:userdata，半径，最小点个数
    return:聚类结果，聚类的数目
    '''
    filename = OUTDIR + "/" + user
    fin = open(filename)
    data = []  # all trajectory
    curTrajSet = []  # one trajectory
    i = 0
    j = 0
    for line in fin:
        i += 1
        line_list = line.strip().split("\t")
        latitude = float(line_list[0])
        longitude = float(line_list[1])
        trajNum = int(line_list[4])

        if trajNum == j:
            # print(j)
            curTrajSet.append([latitude, longitude])
        else:
            data.append(np.array(curTrajSet))
            j += 1
            curTrajSet = []
            curTrajSet.append([latitude, longitude])
        # if i >= 1152:
        #     break
    if len(curTrajSet) > 10:
        data.append(np.array(curTrajSet))
    # pp.pprint(data)
    # print("j: {}".format(str(j)))
    # print("lens: {}".format(str(len(data))))
    print("load data finished! clustering begin...")
    for trajIndex in range(0, j + 1):
        fout = open("clusterResultDBSCAN" + str(trajIndex), "w")
        print(trajIndex)
        result, numbers = dbscan(data[trajIndex], e, m)
        ind = 0
        for cluster in result:
            fout.write(str(data[trajIndex][ind][0]) + "\t" +
                       str(data[trajIndex][ind][1]) + "\t" + str(cluster) + "\n")
            ind += 1

    # plotFeature(data, result, numbers)


def plotCluster(filename, t="OPTICS"):
    print("plot data begin...")
    fin = open(filename)
    plotdata = []
    clusters = []
    for line in fin:
        line_list = line.strip().split("\t")
        latitude = float(line_list[0])
        longitude = float(line_list[1])
        cluster = int(line_list[2])
        plotdata.append([latitude, longitude])
        clusters.append(cluster)
    plotdata = np.array(plotdata)
    numbers = len(set(clusters))
    if t == "OPTICS":
        print("plot OPTICS...")
        plotFeatureOPTICS(plotdata, clusters, numbers)
    elif t == "DBSCAN":
        print("plot DBSCAN...")
        plotFeature(plotdata, clusters, numbers)


def loadTrajsRaw(filename):
    fin = open(filename)
    data = []
    curTrajSet = []
    i = -1
    is_firstLine = True
    j = 0
    for line in fin:
        i += 1
        line_list = line.strip().split("\t")
        latitude = float(line_list[0])
        longitude = float(line_list[1])
        d = line_list[2] + " " + line_list[3]
        dt = datetime.datetime.strptime(d, "%Y-%m-%d %H:%M:%S")
        trajNum = int(line_list[4])
        userId = str(line_list[5])
        if is_firstLine:
            j = trajNum
            is_firstLine = False

        if trajNum == j:
            curTrajSet.append([latitude, longitude, dt, i, trajNum, userId])
        else:
            data.append(np.array(curTrajSet))
            curTrajSet = []
            curTrajSet.append([latitude, longitude, dt, i, trajNum, userId])
            j = trajNum
    if len(curTrajSet) > 10:
        data.append(np.array(curTrajSet))
    return data


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
    r = 6369  # 地球平均半径，单位为公里
    return c * r * 1000


def extractStayPoint(traj, Time, Distance, fout):
    '''
    traj: point of list
    Time: second
    Distance: meter
    '''
    # print(traj)
    trajNum = traj[0][4]
    userId = traj[0][5]
    # fout = open("../st_data/" + userId + "_st", "a+")
    length = len(traj)
    result = []
    i = 0
    flag = False
    while(i < length):
        for j in range(i + 1, length):
            dist = haversine(traj[i][1], traj[i][0], traj[j][1], traj[j][0])
            if dist >= Distance:
                tmp_data = traj[j:j + 10, :]
                avg_latitude = np.mean(tmp_data[:, 0])
                avg_longitude = np.mean(tmp_data[:, 1])
                avg_dist = haversine(
                    traj[i][1], traj[i][0], avg_longitude, avg_latitude)
                if avg_dist <= Distance:
                    continue
                if (traj[j][2] - traj[i][2]).total_seconds() >= Time:
                    # print("**********start*********************************")
                    # print(i, j)
                    # print(dist, (traj[j - 1][2] - traj[i][2]).total_seconds())
                    # print("*******************end***************************")
                    result.append(traj[i:j])
                    flag = True
                    break
                else:
                    break
            if j == length - 1:
                if (traj[j - 1][2] - traj[i][2]).total_seconds() >= Time:
                    result.append(traj[i:])

        if flag:
            for point in traj[i:j]:
                fout.write(str(point[0]) + "\t" + str(point[1]) +
                           "\t" + str(point[2]) + "\t" +
                           str(point[3]) + "\t" + str(trajNum) +
                           "\t" + userId + "\t" + "1" + "\n")
            i = j
            flag = False
        else:
            fout.write(str(traj[i][0]) + "\t" + str(traj[i][1]) +
                       "\t" + str(traj[i][2]) + "\t" +
                       str(traj[i][3]) + "\t" + str(trajNum) +
                       "\t" + userId + "\t" + "0" + "\n")
            i = i + 1

    return result


def plotStayPoint(dataRaw, data_stay):
    number = len(data_stay)
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.scatter(dataRaw[:, 1], dataRaw[:, 0], s=2, c='black')
    colors = ['blue', 'green', 'yellow', 'brown',
              'red', 'purple', 'orange', 'grey']
    for i in range(number):
        print(i)
        colorStyle = colors[i % len(colors)]
        ax.scatter(data_stay[i][:, 1], data_stay[i][:, 0], s=3, c=colorStyle)
    plt.show()


def extractST_forUser(data, userId, Time, Distance):
    fout = open("../st_data/" + userId + "_st", "w")
    len_traj = len(data)
    resultAll = []
    st_index = []
    for i in range(len_traj):
        result = extractStayPoint(data[i], Time, Distance, fout)
        resultAll.append(result)
        for st in result:
            st_index.extend(st[:, 3])
    return resultAll, st_index


def plotST_forUser(data, resultAll):
    len_traj = len(data)
    fig = plt.figure()
    ax = fig.add_subplot(111)
    for i in range(len_traj):
        st_data = resultAll[i]
        n_st = len(st_data)
        colors = ['blue', 'green', 'yellow', 'brown',
                  'red', 'purple', 'orange', 'grey']
        st_index = []
        for j in range(n_st):
            colorStyle = colors[j % len(colors)]
            ax.scatter(st_data[j][:, 1], st_data[j][:, 0],
                       s=3, c=colorStyle, marker='o')
            st_index.extend(st_data[j][:, 3])
        non_st_data = []
        for d in data[i]:
            if d[3] not in st_index:
                non_st_data.append(d)
        non_st_data = np.array(non_st_data)
        ax.scatter(non_st_data[:, 1], non_st_data[:, 0],
                   s=0.3, c='black', marker='.')
    plt.show


# def write_result_forUser(userid, data, resultAll, st_index):
#     fout = open("../st_data/" +
#                 userid + "_st", "w")
#     print("write stay point for user {}....".format(str(userid)))
#     len_traj = len(data)
#     for i in range(len_traj):
#         for point in data[i]:
#             if point[3] in st_index:
#                 fout.write(str(point[0]) + '\t' + str(point[1]) + '\t' +
#                            str(point[2]) + "\t" + str(point[3]) + "\t" +
#                            str(point[4]) + "\t" + str(point[5]) + "\t" +
#                            "1" + "\n")
#             else:
#                 fout.write(str(point[0]) + '\t' + str(point[1]) + '\t' +
#                            str(point[2]) + "\t" + str(point[3]) + "\t" +
#                            str(point[4]) + "\t" + str(point[5]) + "\t" +
#                            "0" + "\n")
#     fout.close()
#     print("user {} write finished!".format(str(userid)))


def loadSTdata(filename):
    fin = open(filename)
    data = []
    ind = 0
    n_StayArea = 0
    flag = False
    for line in fin:
        ind += 1
        line_list = line.strip().split("\t")
        latitude = float(line_list[0])
        longitude = float(line_list[1])
        # dt = datetime.datetime.strptime(line_list[2], "%Y-%m-%d %H:%M:%S")
        # index = int(line_list[3])
        # trajNum = int(line_list[4])
        # userId = line_list[5]
        isST = int(line_list[6])
        if isST == 1:
            if flag is False:
                n_StayArea += 1
                flag = True
            data.append([latitude, longitude])
        else:
            flag = False
    print("total {} GPS point! ".format(str(ind)))
    print("total {} stay area! ".format(str(n_StayArea)))
    data = np.array(data)
    dataForOptics = data * np.pi / 180
    return data, dataForOptics


def ST_Optics(data, dataRaw):
    fout = open("ST_Optics", "w")
    tree = setOfObjects(data, metric='haversine')
    prep_optics(tree, 2.5e-5, 30)
    build_optics(tree, 2.5e-5, 30, './test_st_optics.txt')
    tmp_coredist = []
    for i in tree._core_dist:
        if not math.isnan(i):
            tmp_coredist.append(i)
    print(np.mean(tmp_coredist))
    print(np.median(tmp_coredist))
    ExtractDBSCAN(tree, 0.94e-5)
    labels = tree._cluster_id[:]
    ind = 0
    for cluster in labels:
        fout.write(str(dataRaw[ind][0]) + "\t" +
                   str(dataRaw[ind][1]) + "\t" + str(cluster) + "\n")
        # print("write {} finished!".format(str(ind)))
        ind += 1
    print("total {} clusters!".format(str(len(set(labels)) - 1)))
    return labels


def plot_ST_Optics(filename, dataRaw):
    fin = open(filename)
    data = []
    for line in fin:
        line_list = line.strip().split("\t")
        latitude = float(line_list[0])
        longitude = float(line_list[1])
        cluster = int(line_list[2])
        data.append([latitude, longitude, cluster])
    data = np.array(data)
    n_cluster = len(set(data[:, 2])) - 1
    print("total {} clusters! ".format(str(n_cluster)))
    plotFeatureOPTICS(data, data[:, 2], n_cluster)


def loadUserData(user):
    fin = open("../cleaned_data/" + user)
    data = []
    for line in fin:
        line_list = line.strip().split("\t")
        latitude = float(line_list[0])
        longitude = float(line_list[1])
        data.append([latitude, longitude])
    data = np.array(data)
    return data


def loadAllUser(step=1):
    data = []
    for i in range(0, 182):
        j = 0
        fin = open("../cleaned_data/" + '{:03d}'.format(i))
        for line in fin:
            j += 1
            if j % step == 0:
                line_list = line.strip().split("\t")
                latitude = float(line_list[0])
                longitude = float(line_list[1])
                data.append([latitude, longitude])
                j = 0
        print("user {} finished!".format(str(i)))
    data = np.array(data)
    return data


def plotData(data):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.scatter(data[:, 1], data[:, 0], s=0.3, c="red", marker=".")
    plt.show()


def ExtractST_AllUser(dir):
    userList = ["{:03d}".format(i) for i in range(0, 182)]
    for index, user in enumerate(userList):
        if index <= 35:
            continue
        data = loadTrajsRaw(dir + user)
        resultAll, st_index = extractST_forUser(data, user, 300, 60)
        print("user {} extract finished!".format(str(user)))


if __name__ == '__main__':
    time_start = time.time()
    # Data clean:
    # userClean('000')
    # alluser(userClean)

    # Clustering
    # clusteringDBSCAN('000_tmp', 40, 40)
    # plotCluster("clusterResultOPTICS0", "OPTICS")

    # Extract Stay Point
    # one trajectory
    # data = loadTrajsRaw("../cleaned_data/000_tmp")
    # result = extractStayPoint(data[1], 300, 60)
    # print(result)
    # plotStayPoint(data[1], result)
    # all trajectory for one user
    # data = loadTrajsRaw("../cleaned_data/000_tmp")
    # resultAll, st_index = extractST_forUser(data, 300, 60)
    # plotST_forUser(data, resultAll)
    # write_result_forUser("000", data, resultAll, st_index)

    # Stay Point Clustering
    # data, dataForOptics = loadSTdata("../cleaned_data/000_st")
    # labels = ST_Optics(dataForOptics, data)
    # plot_ST_Optics("ST_Optics", data)

    # plot user data
    # user000 = loadAllUser("000")
    # data = loadAllUser(50)
    # print(len(user000))
    # plotData(data)
    # print(haversine(116.299307, 39.983304, 116.298663, 39.984019))

    ExtractST_AllUser('../cleaned_data/')

    time_end = time.time()
    print("total time: {}s".format(str(time_end - time_start)))
