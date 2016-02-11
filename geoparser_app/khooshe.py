'''
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''

import os
import shutil
import csv
import numpy as np
from scipy.cluster.vq import kmeans,vq


def remove_tiles_folder(tile_name):
    '''
    '''
    if os.path.exists(tile_name):
        shutil.rmtree(tile_name)


def create_folder(folder_name):
    '''
    '''
    if os.path.exists(folder_name):
        shutil.rmtree(folder_name)
    os.makedirs(folder_name)


def get_points_count(points_file):
    '''
    '''
    with open(points_file) as f:
        count = sum(1 for line in f)

    return count


def read_point_data(points_file, point_array):
    '''
    '''
    with open(points_file) as csv_f:
        reader = csv.reader(csv_f)
        try:
            for index, row in enumerate(reader):
                point_array[index] = [float(row[0]),float(row[1])]
        except:
            raise error("Cannot read data from point text file.")
    return point_array


def unique_array(point_array):
    '''
    '''
    a = np.ascontiguousarray(point_array)
    unique_a = np.unique(a.view([('', a.dtype)]*a.shape[1]))

    return unique_a.view(a.dtype).reshape((unique_a.shape[0], a.shape[1]))


def init_dictionary(tile_name):
    '''
    '''
    with open('{0}/dict.csv'.format(tile_name), 'w') as dic_csv:
        writer = csv.writer(dic_csv)
        #adding header
        writer.writerow(['folder','file','extent'])


def make_dictionary(temp, tile_name):
    '''
    '''
    with open('{0}/dict.csv'.format(tile_name), 'a') as dic_csv:
        writer = csv.writer(dic_csv)
        for each in temp:
            writer.writerow([each[0], each[1], "{0}, {1}, {2}, {3}".format(min(each[3]),min(each[2]),max(each[3]), max(each[2]))])


def make_first_layer(unique_points, centroids_number, tile_name):
    '''
    '''
    new_data = {}
    centroids,_ = kmeans(unique_points,centroids_number)
    idx,_ = vq(unique_points,centroids)
    shapes = []
    temp = []
    for each in range(len(centroids)):
        points = unique_points[idx==each]
        new_data['{0}'.format(each)] = points
        shapes.append(points.shape[0])
    create_folder('{0}/0'.format(tile_name))
    with open('{0}/0/0.csv'.format(tile_name),'w') as csv_n:
        writer = csv.writer(csv_n, delimiter=',')
        writer.writerow(['latitude', 'longitude', 'label'])
        temp_lat = []
        temp_lon = []
        for index, centroid in enumerate(centroids):
            writer.writerow([centroid[0],centroid[1], shapes[index]])
            temp_lat.append(centroid[0])
            temp_lon.append(centroid[1])
        temp.append([0, 0, temp_lat, temp_lon])
    init_dictionary(tile_name)
    make_dictionary(temp, tile_name)

    return centroids, shapes, new_data


def make_rest_of_layers(data, centroids, shapes, centroids_number, tile_name):
    '''
    '''
    count = 1
    temp = []
    while True:
        create_folder('{0}/{1}'.format(tile_name, count))
        new_datas = {}
        for key in data.keys():
            if data[key].shape[0] < 10:
                with open('{0}/{1}/{2}.csv'.format(tile_name, count, key), 'w') as csv_n:
                    writer = csv.writer(csv_n)
                    writer.writerow(['latitude', 'longitude', 'label'])
                    temp_lat = []
                    temp_lon = []
                    for point in data[key]:
                        writer.writerow([point[0], point[1], 'p'])
                        temp_lat.append(point[0])
                        temp_lon.append(point[1])
                    temp.append([count, key, temp_lat, temp_lon])
            else:
                centroids,_ = kmeans(data[key], centroids_number)
                idx,_ = vq(data[key],centroids)
                for each in range(len(centroids)):
                    points = data[key][idx==each]
                    new_datas['{0}_{1}'.format(key, each)] = points
                    shapes.append(points.shape[0])
                with open('{0}/{1}/{2}.csv'.format(tile_name, count, key),'w') as csv_n:
                    writer = csv.writer(csv_n)
                    writer.writerow(['latitude', 'longitude', 'label'])
                    temp_lat = []
                    temp_lon = []
                    for a, centroid in enumerate(centroids):
                        writer.writerow([centroid[0], centroid[1], shapes[a]])
                        temp_lat.append(centroid[0])
                        temp_lon.append(centroid[1])
                    temp.append([count, key, temp_lat, temp_lon])
                shapes = []
        data = 0
        data = new_datas
        new_datas = 0
        count += 1
        if data == {}:
            break
        make_dictionary(temp, tile_name)


def run_khooshe(points_obj, points_file, tile_name):
    '''
    '''
    CENTROIDS_NUMBER = 15
    remove_tiles_folder(tile_name)
    if points_file:
        points_count = get_points_count(points_file)
        point_array = np.zeros([points_count, 2])
        point_array = read_point_data(points_file, point_array)
        print "Reading points --> DONE."
    else:
        point_array = points_obj

    unique_points = unique_array(point_array)
    print "Finding unique points --> DONE."

    centroids, shapes, new_data = make_first_layer(unique_points, CENTROIDS_NUMBER, tile_name)

    make_rest_of_layers(new_data, centroids, shapes, CENTROIDS_NUMBER, tile_name)
    print "Creating layers --> DONE."


if __name__ == '__main__':
    run_khooshe(None, 'sample_points.csv', 'tiles')
