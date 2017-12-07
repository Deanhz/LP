import matplotlib.pyplot as plt
import numpy as np


def loadData(filename, step=1):
    latitude = []
    longitude = []
    i = 0
    j = 0
    for index, line in enumerate(open(filename)):
        j += 1
        i += 1
        if i % step == 0:
            list_line = line.strip().split('\t')
            latitude.append(float(list_line[0]))
            longitude.append(float(list_line[1]))
            i = 0
        print("{} finished!".format(index))
        if j > 908:
            break
    print('load finished!')
    return np.array([latitude, longitude])


def plotScatter(data):
    latitude = data[0]
    longitude = data[1]
    print("plot begin!")
    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    ax1.set_title('user GPS trajectory')
    plt.xlabel('longitude')
    plt.ylabel('latitude')
    ax1.scatter(longitude, latitude, s=0.8, c='r', marker='.')
    plt.show()


def display(filename, step=1):
    data = loadData(filename, step)
    plotScatter(data)


if __name__ == "__main__":
    display("../cleaned_data/000", step=1)
