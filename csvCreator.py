import subprocess
import pandas as pd
import numpy as np
import operator

from re import split
import re
from fluffUtil import get_sensor_name, get_lines_to_read, get_values, match_unix_stamp


def insert_line(df, dict):
    df = df.append({'time': dict.get('time'),
                    'accX': dict.get('accX'), 'accX_std': dict.get('accX_std'),
                    'accY': dict.get('accY'), 'accY_std': dict.get('accY_std'),
                    'accZ': dict.get('accZ'), 'accZ_std': dict.get('accZ_std'),

                    'gyrX': dict.get('gyrX'), 'gyrX_std': dict.get('gyrX_std'),
                    'gyrY': dict.get('gyrY'), 'gyrY_std': dict.get('gyrY_std'),
                    'gyrZ': dict.get('gyrZ'), 'gyrZ_std': dict.get('gyrZ_std'),

                    'heartR': dict.get('heartR'), 'heartR_std': dict.get('heartR_std'),

                    'SmoothedAirPressure': dict.get('SmoothedAirPressure'), 'SAP_std': dict.get('SAP_std'),
                    'UncalibratedBarometerAltitude': dict.get('UncalibratedBarometerAltitude'),
                    'UBA_std': dict.get('UBA_std'),
                    'AirTemperature': dict.get('AirTemperature'), 'AT_std': dict.get('AT_std'),
                    'AirPressure': dict.get('AirPressure'), 'AP_std': dict.get('AP_std'),

                    'PlethysmogramGreen': dict.get('PlethysmogramGreen'), 'ple_std': dict.get('ple_std'),

                    'steps': dict.get('steps'), 'steps_std': dict.get('steps_std'),
                    'WalkingSteps': dict.get('WalkingSteps'), 'W_St_std': dict.get('W_St_std'),
                    'RunningSteps': dict.get('RunningSteps'), 'RS_std': dict.get('RS_std'),
                    'CaloriesBurned': dict.get('CaloriesBurned'), 'CB_std': dict.get('CB_std'),

                    'Latitude': dict.get('Latitude'),
                    'Longitude': dict.get('Longitude'),
                    }, ignore_index=True)

    return df


def get_next_earliest(df_collection):
    # get earliest data frame
    temp_dict = {}
    for key in df_collection:
        if len(df_collection[key]) != 0:
            temp_dict[key] = df_collection[key]['time'].iloc[0]
    if len(temp_dict) != 0:
        earliest_key = min(temp_dict, key=temp_dict.get)
    else:
        return 0, 'none'
    earliest_time = df_collection[earliest_key]['time'].iloc[0]
    return earliest_time, earliest_key


def get_latest(df_collection):
    temp_dict = {}
    for key in df_collection:
        if len(df_collection[key]) != 0:
            temp_dict[key] = df_collection[key]['time'].iloc[-1]
    if len(temp_dict) != 0:
        latest_key = max(temp_dict, key=temp_dict.get)
    else:
        return 0, 'none'
    latest_time = df_collection[latest_key]['time'].iloc[0]
    return latest_time, latest_key


def df_collection_is_not_empty(df_collection):
    for key in df_collection:
        if len(df_collection[key]) != 0:
            return True
        else:
            continue
    return False


def merge(df_collection):
    complete_df = pd.DataFrame(columns=['time',
                                        # acc
                                        'accX', 'accX_std',
                                        'accY', 'accY_std',
                                        'accZ', 'accZ_std',

                                        'gyrX', 'gyrX_std',
                                        'gyrY', 'gyrY_std',
                                        'gyrZ', 'gyrZ_std',

                                        'heartR', 'heartR_std',

                                        'SmoothedAirPressure', 'SAP_std',
                                        'UncalibratedBarometerAltitude', 'UBA_std',
                                        'AirTemperature', 'AT_std',
                                        'AirPressure', 'AP_std',

                                        'PlethysmogramGreen', 'ple_std',

                                        'steps', 'steps_std',
                                        'WalkingSteps', 'W_St_std',
                                        'RunningSteps', 'RS_std',
                                        'CaloriesBurned', 'CB_std',

                                        'Latitude',
                                        'Longitude'])

    # start two minutes aggregating
    earliest_time, key = get_next_earliest(df_collection)
    # latest_time, l_key = get_latest(df_collection)
    while df_collection_is_not_empty(df_collection):
        merging_keys = []
        limit = earliest_time + 61
        for key in df_collection:
            if len(df_collection[key]) != 0:
                if df_collection[key]['time'].iloc[0] <= limit:
                    merging_keys.append(key)
        # combine new row
        temp_dict = {'time': earliest_time}
        for key in merging_keys:
            if key == 'sg2_bar':
                if len(df_collection[key].index) != 0:
                    temp_dict['SmoothedAirPressure'] = df_collection[key]['SmoothedAirPressure'].iloc[0]
                    temp_dict['UncalibratedBarometerAltitude'] = \
                    df_collection[key]['UncalibratedBarometerAltitude'].iloc[0]
                    temp_dict['AirTemperature'] = df_collection[key]['AirTemperature'].iloc[0]
                    temp_dict['AirPressure'] = df_collection[key]['AirPressure'].iloc[0]
                    temp_dict['SAP_std'] = df_collection[key]['SAP_std'].iloc[0]
                    temp_dict['UBA_std'] = df_collection[key]['UBA_std'].iloc[0]
                    temp_dict['AT_std'] = df_collection[key]['AT_std'].iloc[0]
                    temp_dict['AP_std'] = df_collection[key]['AP_std'].iloc[0]
                    # drop this row
                    df_collection[key] = df_collection[key].iloc[1:]
                else:
                    del df_collection[key]
            if key == 'sg2_gps':
                if len(df_collection[key].index) != 0:
                    temp_dict['Latitude'] = df_collection[key]['Latitude'].iloc[0]
                    temp_dict['Longitude'] = df_collection[key]['Longitude'].iloc[0]
                    # drop this row
                    df_collection[key] = df_collection[key].iloc[1:]
                else:
                    del df_collection[key]
            if key == 'sg2_acc':
                if len(df_collection[key].index) != 0:
                    temp_dict['accX'] = df_collection[key]['X'].iloc[0]
                    temp_dict['accY'] = df_collection[key]['Y'].iloc[0]
                    temp_dict['accZ'] = df_collection[key]['Z'].iloc[0]
                    temp_dict['accX_std'] = df_collection[key]['x_std'].iloc[0]
                    temp_dict['accY_std'] = df_collection[key]['y_std'].iloc[0]
                    temp_dict['accZ_std'] = df_collection[key]['y_std'].iloc[0]
                    # drop this row
                    df_collection[key] = df_collection[key].iloc[1:]
                else:
                    del df_collection[key]
            if key == 'sg2_ple':
                if len(df_collection[key].index) != 0:
                    temp_dict['PlethysmogramGreen'] = df_collection[key]['PlethysmogramGreen'].iloc[0]
                    temp_dict['ple_std'] = df_collection[key]['ple_std'].iloc[0]
                    # drop this row
                    df_collection[key] = df_collection[key].iloc[1:]
                else:
                    del df_collection[key]
            if key == 'sg2_ped':
                if len(df_collection[key].index) != 0:
                    temp_dict['steps'] = df_collection[key]['steps'].iloc[0]
                    temp_dict['WalkingSteps'] = df_collection[key]['WalkingSteps'].iloc[0]
                    temp_dict['RunningSteps'] = df_collection[key]['RunningSteps'].iloc[0]
                    temp_dict['CaloriesBurned'] = df_collection[key]['CaloriesBurned'].iloc[0]
                    temp_dict['steps_std'] = df_collection[key]['steps_std'].iloc[0]
                    temp_dict['W_St_std'] = df_collection[key]['W_St_std'].iloc[0]
                    temp_dict['RS_std'] = df_collection[key]['RS_std'].iloc[0]
                    temp_dict['CB_std'] = df_collection[key]['CB_std'].iloc[0]
                    df_collection[key] = df_collection[key].iloc[1:]
                else:
                    del df_collection[key]
            if key == 'sg2_hrt':
                if len(df_collection[key].index) != 0:
                    temp_dict['heartR'] = df_collection[key]['heartR'].iloc[0]
                    temp_dict['heartR_std'] = df_collection[key]['heartR_std'].iloc[0]
                    df_collection[key] = df_collection[key].iloc[1:]
                else:
                    del df_collection[key]
            if key == 'sg2_gyr':
                if len(df_collection[key].index) != 0:
                    temp_dict['gyrX'] = df_collection[key]['X'].iloc[0]
                    temp_dict['gyrY'] = df_collection[key]['Y'].iloc[0]
                    temp_dict['gyrZ'] = df_collection[key]['Z'].iloc[0]
                    temp_dict['gyrX_std'] = df_collection[key]['x_std'].iloc[0]
                    temp_dict['gyrY_std'] = df_collection[key]['y_std'].iloc[0]
                    temp_dict['gyrZ_std'] = df_collection[key]['z_std'].iloc[0]
                    df_collection[key] = df_collection[key].iloc[1:]
                else:
                    del df_collection[key]
        # earliest_time = df_collection[earliest_key]['time'].iloc[0]
        earliest_time, key = get_next_earliest(df_collection)
        if not complete_df.empty:
            if earliest_time == complete_df['time'].iloc[-1]:
                print('Duplicated entry. ERROR ERROR ERROR ERROR ERROR ERROR ERROR ERROR')
                continue
        print(str(earliest_time) + ' from ' + key)
        # if match_unix_stamp(earliest_time):
        complete_df = insert_line(complete_df, temp_dict)
        # else:
        #     print(str(earliest_time) + ' from ' + key)
        #     print('Time stamp does not match unix time pattern. stopping here')
        #     return complete_df
        # raise ValueError('Time stamp does not match unix time pattern.')
    # print('latest' + str(latest_time) + 'from ' + key)
    return complete_df


def to_csv(files, prefix, file_path=''):
    df_collection = {}
    for file_name in files:

        # get sensor name
        sensor_name = get_sensor_name(file_name)
        lines_to_read = get_lines_to_read(sensor_name)

        with open(file_path + '/' + file_name, 'rt') as file:
            fileLines = int(
                subprocess.check_output(["wc", "-l", file_path + '/' + file_name]).decode("utf8").split()[0])
            # as every component got its std dev
            lines_per_iteration = lines_to_read
            window = 0
            timeAll = []

            all_1 = []
            all_1_std = []

            all_2 = []
            all_2_std = []

            all_3 = []
            all_3_std = []

            all_4 = []
            all_4_std = []

            print(file_name)
            while window < fileLines:
                file_lines = []
                for i in range(lines_per_iteration):
                    file_lines.append(get_values(file.readline()))

                timeAll.extend(file_lines[0])
                all_1.extend(file_lines[1])
                all_1_std.extend((file_lines[2]))
                # special case
                if sensor_name == 'sg2_gps':
                    all_2.extend(file_lines[2])
                    all_3.extend(file_lines[3])
                    window += lines_per_iteration
                    continue

                if sensor_name in ['sg2_gyr', 'sg2_bar', 'sg2_acc', 'sg2_ped']:
                    all_2.extend(file_lines[3])
                    all_2_std.extend(file_lines[4])
                    all_3.extend(file_lines[5])
                    all_3_std.extend(file_lines[6])
                if sensor_name in ['sg2_bar', 'sg2_ped', 'sg2_bar']:
                    all_4.extend(file_lines[7])
                    all_4_std.extend(file_lines[8])

                # print(window)
                window += lines_per_iteration

            if sensor_name == 'sg2_acc' or sensor_name == 'sg2_gyr':
                df = pd.DataFrame(np.column_stack([timeAll,
                                                   all_1, all_1_std,
                                                   all_2, all_2_std,
                                                   all_3, all_3_std]),
                                  columns=['time',
                                           'X', 'x_std',
                                           'Y', 'y_std',
                                           'Z', 'z_std'])

            elif sensor_name == 'sg2_hrt':
                df = pd.DataFrame(np.column_stack([timeAll,
                                                   all_1, all_1_std]),
                                  columns=['time',
                                           'heartR', 'heartR_std'])
                indexNames = df[(df['heartR'] < 50) & df['heartR'] > 120].index
                df.drop(indexNames, inplace=True)
            elif sensor_name == 'sg2_bar':
                df = pd.DataFrame(np.column_stack([timeAll,
                                           all_1, all_1_std,
                                           all_2, all_2_std,
                                           all_3, all_3_std,
                                           all_4, all_4_std]),
                                  columns=['time',
                                           'SmoothedAirPressure', 'SAP_std',
                                           'UncalibratedBarometerAltitude', 'UBA_std',
                                           'AirTemperature', 'AT_std',
                                           'AirPressure', 'AP_std'])
            elif sensor_name == 'sg2_ped':
                df = pd.DataFrame(np.column_stack([timeAll,
                                           all_1, all_1_std,
                                           all_2, all_2_std,
                                           all_3, all_3_std,
                                           all_4, all_4_std]),
                                  columns=['time',
                                           'steps', 'steps_std',
                                           'WalkingSteps', 'W_St_std',
                                           'RunningSteps', 'RS_std',
                                           'CaloriesBurned', 'CB_std'])
            elif sensor_name == 'sg2_gps':
                df = pd.DataFrame(np.column_stack([timeAll, all_1, all_2]),
                                  columns=['time',
                                           'Latitude', 'Longitude'])
                df = df[df['Latitude'] != 0]
            # when sg2_ple
            else:
                df = pd.DataFrame(np.column_stack([timeAll,
                                                   all_1, all_1_std]),
                                  columns=['time',
                                           'PlethysmogramGreen', 'ple_std'])

            df.sort_values('time', inplace=True)
            df_collection[sensor_name] = df
            # index += 1
            file.close()
    # merge data frames:
    all_df = merge(df_collection)
    for key in df_collection:
        print(key + ': ')
        print(len(df_collection[key]))

    all_df.to_csv(prefix + '.csv', index=False)
    print("here")
