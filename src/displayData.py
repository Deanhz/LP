'''
Author: Dean
Date: 2017.9.7
'''

FILE_IN = '000_cleaned_BJ_grided'
latitudes = []
longitudes = []
indexes = []


def display():
    '''
    show min,max latitude and longitude
    show min,max index
    '''
    for line in open(FILE_IN):
        list_line = line.strip().split('\t')
        latitudes.append(float(list_line[1]))
        longitudes.append(float(list_line[2]))
        indexes.append(int(list_line[5]))
    print("min latitude:{}, max latitude:{}".format(
        str(min(latitudes)), str(max(latitudes))))
    print("min longitude:{}, max longtitude:{}".format(
        str(min(longitudes)), str(max(longitudes))))
    print("min index:{}, max index:{}".format(
        str(min(indexes)), str(max(indexes))))


if __name__ == "__main__":
    display()
