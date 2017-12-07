'''
Author: Dean
'''
from math import radians, cos, sin, asin, sqrt
import numpy as np
import datetime
import stats
from scipy.stats import mode


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


def DataExtract(fin):
    '''
    extract latitude,longtitude,date,time
    Example:
    DataExtract("000")
    Output:000_cleaned
    '''
    file_out = fin + "_cleaned"
    f = open(fin)
    fout = open(file_out, 'w')
    for index, line in enumerate(f):
        line_list = line.strip().split(',')
        if len(line_list) != 7:
            continue
        latitude = line_list[0]
        longtitude = line_list[1]
        date = line_list[5]
        time = line_list[6]
        # print(latitude + "\t" + longtitude + "\t" + date + "\t" + time)
        fout.write(fin + "\t" + latitude + "\t" + longtitude +
                   "\t" + date + "\t" + time + '\n')
        print("{} is finished!".format(index))


def DataExtractForBJ(fin):
    '''
    extract data for beijing
    Example:
    DataExtractForBJ("000_cleaned")
    Output:000_cleaned_BJ
    '''
    file_BJ = fin + "_BJ"
    # file_SH = fin + "_SH"
    # fout_BJ = open(file_BJ, "w")
    fout_BJ_inner = open(fin + "_BJ_inner", "w")
    # fout_SH = open(file_SH, "w")
    for index, line in enumerate(open(fin)):
        line_list = line.strip().split('\t')
        # print(line_list)
        latitude = float(line_list[1])
        longitude = float(line_list[2])
        # if (115.7 <= longitude <= 117.4) and (39.4 <= latitude <= 41.6):
        #     fout_BJ.write(line)
        if (116.2 <= longitude <= 116.6) and (39.7 <= latitude <= 40.1):
            fout_BJ_inner.write(line)
        print("{} finished!".format(index))


def DataSplitForWeekday(fin):
    '''
    split data for weekday and weekend
    Example:
    DataSplitForWeekday("000_cleaned_BJ_grided")
    Output:000_cleaned_BJ_grided_weekday
    '''
    f_full = open(fin + "_full", "w")
    f_weekday = open(fin + "_weekday", "w")
    f_weekend = open(fin + "_weekend", "w")
    f_saturday = open(fin + "_saturday", "w")
    f_sunday = open(fin + "_sunday", "w")
    for line in open(fin):
        line_list = line.strip().split('\t')
        d = line_list[3] + " " + line_list[4]
        f_full.write('\t'.join(line_list[:3]) +
                     '\t' + d + '\t' + line_list[5] + '\n')
        dt = datetime.datetime.strptime(d, "%Y-%m-%d %H:%M:%S")
        dw = dt.weekday()
        is_weekday = 1 if dw < 5 else 0
        if is_weekday:
            f_weekday.write('\t'.join(line_list[:3]) +
                            '\t' + d + '\t' + line_list[5] + '\n')
        else:
            f_weekend.write('\t'.join(line_list[:3]) +
                            '\t' + d + '\t' + line_list[5] + '\n')
        if dw == 5:
            f_saturday.write('\t'.join(line_list[:3]) +
                             '\t' + d + '\t' + line_list[5] + '\n')
        elif dw == 6:
            f_sunday.write('\t'.join(line_list[:3]) +
                           '\t' + d + '\t' + line_list[5] + '\n')


def convertToTrajectory(fin, timeVal=120, disVal=500):
    '''
    convert data to Trajectory,trajectory id begin from 0
    timeVal is maximum time interval
    disVal is maximum distance interval
    Example: convertToTrajectory("000_cleaned_BJ_grided_weekday",120,500)
    Output: 000_trajectry
    '''
    f_out = open(fin[:3] + "_trajectory", "w")
    lines = open(fin).readlines()
    lastDt = ''
    lastLatitude = ''
    lastLongitude = ''
    traj_id = 0
    for index, val in enumerate(lines):
        line_list = val.strip().split('\t')
        if index == 0:
            lastT = line_list[3]
            lastDt = datetime.datetime.strptime(lastT, "%Y-%m-%d %H:%M:%S")
            lastLatitude = line_list[1]
            lastLongitude = line_list[2]
            continue
        curT = line_list[3]
        curDt = datetime.datetime.strptime(curT, "%Y-%m-%d %H:%M:%S")
        T_interval = (curDt - lastDt).total_seconds()
        lastDt = curDt
        curLatitude = line_list[1]
        curLongitude = line_list[2]
        D_interval = haversine(float(lastLongitude), float(lastLatitude),
                               float(curLongitude), float(curLatitude))
        if (T_interval <= 120 * 60 and D_interval <= 500):
            if T_interval <= 30:
                speed = D_interval * 1.0 / T_interval
                f_out.write('\t'.join(line_list) + '\t' + str(traj_id) +
                            '\t' + str(T_interval) + '\t' + str(D_interval) +
                            '\t' + str(speed) + '\n')
            else:
                f_out.write('\t'.join(line_list) + '\t' + str(traj_id) +
                            '\t' + str(T_interval) + '\t' + str(D_interval) +
                            '\t' + '-1' + '\n')
        else:
            traj_id += 1
            f_out.write('\t'.join(line_list) + '\t' + str(traj_id) +
                        '\t' + str(T_interval) + '\t' + str(D_interval) +
                        '\t' + str(-1) + '\n')

        lastLatitude = curLatitude
        lastLongitude = curLongitude
        # print(T_interval, D_interval)


def denoise(fin):
    '''
    denoising through speed
    Example: denoise('000_trajectory')
    Output: "000_trajectory_denoised"
    '''
    fout = open(fin + "_denoised", "w")
    speeds = []
    indexes = []
    noise_indexes = []
    total_noise = 0
    lines = open(fin).readlines()
    length = len(lines)
    sum_speed_is_0 = 0
    for index, line in enumerate(lines):
        line_list = line.strip().split('\t')
        speed = line_list[8]
        if float(speed) == 0.0:
            sum_speed_is_0 += 1
        timeInterval = line_list[6]
        if float(timeInterval) <= 30 and float(speed) > 0:
            speeds.append(float(speed))
            indexes.append(int(index))
        else:
            if float(speed) != 0:
                noise_indexes.append(index)
                total_noise += 1
            if len(speeds) == 0:
                continue
            if len(speeds) == 1:
                noise_indexes.append(indexes[0])
                total_noise += 1
                speeds = []
                indexes = []
                continue
            Q1 = stats.quantile(speeds, p=0.25)
            Q3 = stats.quantile(speeds, p=0.75)
            IQR = Q3 - Q1
            upbound = Q3 + 1.5 * IQR
            downbound = Q1 - 1.5 * IQR
            # print(downbound, upbound)
            for ind, sp in enumerate(speeds):
                if (sp <= downbound or sp >= upbound):
                    noise_indexes.append(indexes[ind])
                    total_noise += 1
            print("total data: {},have finded noise : {}".format(
                length, total_noise))
            speeds = []
            indexes = []
    noise_indexes = sorted(noise_indexes)
    print(noise_indexes)
    print("total speed is 0:{}".format(sum_speed_is_0))
    print("total noise:{}".format(total_noise))
    print("writing denoised data....")
    for index, line in enumerate(lines):
        if index in noise_indexes:
            continue
        fout.write(line)
    print("Finished!")


def feature_dispose(fin):
    '''
    yield feature:
    user_id week_id time_id grid_id traj_id speed
    Example:
    feature_dispose("000_trajectory_denoised")
    Output:
    000_trajectory_denoised_feature
    '''
    fout = open(fin + "_feature", "w")
    i = 0
    for line in open(fin):
        i += 1
        line_list = line.strip().split('\t')
        user = line_list[0]
        dt = datetime.datetime.strptime(line_list[3], "%Y-%m-%d %H:%M:%S")
        st = datetime.datetime.combine(dt, datetime.time.min)
        diff_minutes = int((dt - st).total_seconds() / 60.0)
        week = dt.weekday()
        week_id = 0
        if week == 5:
            week_id = 1
        elif week == 6:
            week_id = 2
        time_id = diff_minutes
        grid_id = line_list[4]
        traj_id = line_list[5]
        speed = line_list[8]
        fout.write(user + "\t" + str(week_id) + '\t' + str(time_id) +
                   '\t' + grid_id + '\t' + traj_id + '\t' + speed + '\n')
        print("line {} finished!".format(str(i)))


def timeId_aggregate(fin):
    '''
    aggregate data for time_Id
    week_id,grid_id is mode value
    speed is mean value
    Example:timeId_aggregate("000_trajectory_denoised_feature")
    Output:
    000_trajectory_denoised_feature_timeAggregate
    '''
    fout = open(fin + "_timeAggregate", "w")
    i = 0
    speeds = []
    weeks = []
    grids = []
    lasttime = ''
    lastline = ''
    for line in open(fin):
        i += 1
        userId, week_id, time_id, grid_id, traj_id, speed = line.strip().split('\t')
        if i == 1:
            lasttime = time_id
            lastline = line
            speeds.append(float(speed))
            weeks.append(int(week_id))
            grids.append(int(grid_id))
            continue
        if time_id == lasttime:
            speeds.append(float(speed))
            weeks.append(int(week_id))
            grids.append(int(grid_id))
        else:
            avg_speed = sum(speeds) / len(speeds)
            mode_week = mode(weeks)[0][0]
            mode_grid = mode(grids)[0][0]
            last = lastline.strip().split('\t')
            fout.write(last[0] + '\t' + str(mode_week) + '\t' +
                       last[2] + '\t' + str(mode_grid) + '\t' +
                       last[4] + '\t' + str(avg_speed) + '\n')
            lasttime = time_id
            speeds = [float(speed), ]
            weeks = [int(week_id), ]
            grids = [int(grid_id), ]
        lastline = line
        print("line {} finished!".format(str(i)))


def calNextTimeId(speed):
    alpha = 30
    beta = 2
    return int(alpha / (np.log10(speed + 10)) ** beta)


def calculate_sampling_By_speed(fin):
    fout = open(fin + "_sampling", "w")
    i = 0
    for line in open(fin):
        i += 1
        l_list = line.strip().split('\t')
        timeId = l_list[2]
        speed = l_list[5]
        nextTimeId = int(timeId) + calNextTimeId(float(speed))
        fout.write('\t'.join(l_list) + '\t' + str(nextTimeId) + '\n')
        print("line {} finished!".format(str(i)))


if __name__ == "__main__":
    calculate_sampling_By_speed('000_trajectory_denoised_feature_timeAggregate')
