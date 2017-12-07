'''
Author: Dean
Date: 2017.9.6
'''
import numpy as np

FILE_IN = '000_cleaned_BJ'
FILE_OUT = FILE_IN + "_grided"
fout = open(FILE_OUT, "w")


class GeoObject(object):
    def __init__(self, user, lati, longi, d, t):
        self.user = user
        self.lati = float(lati)
        self.longi = float(longi)
        self.d = d
        self.t = t

    def setTag(self, tag):  # Cell number
        self.tag = tag


class GridUser(object):
    def __init__(self, m, n, filename):
        self.m = m  # numbers of Y
        self.n = n  # numbers of X
        self.objList = []
        self.gpsList = []
        i = 0
        for line in open(filename):
            i = i + 1
            list_line = line.strip().split('\t')
            obj = GeoObject(list_line[0], list_line[1],
                            list_line[2], list_line[3], list_line[4])
            self.objList.append(obj)
            self.gpsList.append([float(list_line[1]), float(list_line[2])])

    def grid_map(self):
        min_lati, min_longi = np.min(self.gpsList, axis=0)
        max_lati, max_longi = np.max(self.gpsList, axis=0)
        self.min_latitude = min_lati - 0.001
        self.min_longitude = min_longi - 0.001
        self.max_latitude = max_lati + 0.001
        self.max_longitude = max_longi + 0.001
        print(str(self.min_latitude) + " " + str(self.max_latitude))
        print(str(self.min_longitude) + " " + str(self.max_longitude))
        self.sizeY = (self.max_latitude - self.min_latitude) * 100000 / self.m
        self.sizeX = (self.max_longitude - self.min_longitude) * \
            100000 / self.n
        print("size X: {}".format(str(self.sizeX)))
        print("size Y: {}".format(str(self.sizeY)))
        self.indexCell = []
        for i in range(0, self.m * self.n):
            self.indexCell.append([])
        # IndexList = []value, ..., sep, end, file, flush
        total_obj = len(self.objList)
        j = 0
        for obj in self.objList:
            j = j + 1
            print("total:{},current:{}...".format(total_obj, j))
            Xcell = np.floor((obj.longi - self.min_longitude)
                             * 100000 / self.sizeX)
            Ycell = np.floor((obj.lati - self.min_latitude)
                             * 100000 / self.sizeY)
            Index = int(self.n * Ycell + Xcell + 1)
            # IndexList.append(Index)
            self.indexCell[Index].append(obj)
            obj.setTag(Index)
            fout.write(str(obj.user) + "\t" + str(obj.lati) +
                       "\t" + str(obj.longi) + "\t" + obj.d +
                       "\t" + obj.t + "\t" + str(obj.tag) + '\n')
        # print(sorted(IndexList)[:100])

    def displayObj(self):
        for obj in self.objList:
            print(str(obj.user) + "\t" + str(obj.lati) +
                  "\t" + str(obj.longi) + "\t" + str(obj.tag))

    def display_min_max(self):
        print("min latitude:{},max latitude:{}".format(
            str(self.min_latitude), str(self.max_latitude)))
        print("min longitude:{},max longtitude:{}".format(
            str(self.min_longitude), str(self.max_longitude)))
        print("size X: {}".format(str(self.sizeX)))
        print("size Y: {}".format(str(self.sizeY)))


if __name__ == '__main__':
    grid = GridUser(200, 400, FILE_IN)
    grid.grid_map()
    grid.display_min_max()
