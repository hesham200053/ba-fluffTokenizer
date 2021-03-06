import json
import re
from os import listdir
from os.path import isfile, join

pattern = re.compile("15[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]")


def get_lines_to_read(s_type):
    # structure is unix timeStamp + time offsets + (sensor components * 2) cause we add std-dev for each component
    switcher = {
        'sg2_acc': 7,
        'sg2_hrt': 3,
        'sg2_gyr': 7,
        'sg2_ple': 3,
        'sg2_ped': 9,
        'sg2_bar': 9,
        # exception: just the sensor components
        'sg2_gps': 12
    }
    return switcher.get(s_type, -1)


def get_values(argument, ints=False):
    temp = argument.split(':')
    if len(temp) == 2:
        if temp[0].strip() == 'time_series':
            ints = True
        values = temp[1].strip(' []\n,')
        if len(values) > 1:
            if ints:
                return [int(x) for x in values.split(',')]
            else:
                return [float(x) for x in values.split(',')]
        else:
            return []
    else:
        return []


def get_lines(in_file, components):
    lines = []

    for i in range(components):
        # parsing unix time stamp
        new_line = in_file.readline()
        if len(new_line) != 0:
            if i == 0:
                lines.append(int(new_line))
                continue
            # parsing time offsets
            if i == 1:
                lines.append(get_values(new_line, ints=True))
                continue
            # parsing normal sensor values
            lines.append(get_values(new_line))
    return lines


def get_components(s_type):
    # structure is unix timeStamp + time offsets + sensor components
    switcher = {
        'sg2_acc': 5,
        'sg2_hrt': 6,
        'sg2_gyr': 5,
        'sg2_ple': 3,
        'sg2_ped': 10,
        'sg2_bar': 6,
        # exception: just the sensor components
        'sg2_gps': 12

    }
    return switcher.get(s_type, -1)


def match_unix_stamp(unix_stamp):
    match = pattern.match(str(unix_stamp))
    if match is not None:
        return True
    else:
        return False


def writeListToFile(argument, file, name):
    # argument = map(str, argument)
    argument = str(argument).strip('[]')
    file.write(name)
    file.writelines(argument)
    file.write('\n')


def get_sensor_name(file_name):
    sensor_name_length = len('sg2_xxx')
    start_index = file_name.find('sg2')
    end_index = start_index + sensor_name_length
    return file_name[start_index:end_index]


# correct json schemas for phq protocols
def correct_phq_schemas():
    path = '/Users/Hesham/dev/steadyusecase/src/main/resources/Patientendaten/ST-1233329802/phq'

    files = [f for f in listdir(path) if isfile(join(path, f))
             & ('PHQ' in f)
             & f.endswith('.json')]

    files.sort()
    for file in files:
        print(file)
        json_content = ''
        with open(path + '/' + file, 'rt') as evening_protocol:
            content = evening_protocol.read()
            content = content.replace("\'", "\"")
            content = content.replace("\"contents\": \"{", "\"contents\": {")
            content = content.replace("}\"", "}")
            json_content = json.loads(content)
            evening_protocol.close()
        with open(path + '/' + file, 'w') as evening_protocol:
            json.dump(json_content, evening_protocol)
            evening_protocol.close()