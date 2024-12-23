import io
import json
import h5py

import pandas as pd

from src.redis_client import redis
from keras.models import load_model

arguments_cache = {}


def get_from_cache(lpg_group_id, file_name):
    try:
        file_from_cache = arguments_cache.get(lpg_group_id).get(file_name)
        return file_from_cache
    except:
        return None

def get_from_server(lpg_group_id, file_name):
    file_from_redis = redis.get_files(lpg_group_id, file_name)
    return file_from_redis


def get_model(lpg_group_id):
    if (get_from_cache(lpg_group_id, 'model_multiclass.h5')) is not None:
        model_multiclass = get_from_cache(lpg_group_id, 'model_multiclass_h5')
        print('load cache ===> model_multiclass.h5')
        return model_multiclass

    if not get_from_server(lpg_group_id, 'model_multiclass.h5'):
        raise FileNotFoundError("Model H5 for Landing Page Group ID not found!")

    if get_from_server(lpg_group_id, 'model_multiclass.h5'):
        model_multiclass = get_from_server(lpg_group_id, 'model_multiclass.h5')
        model_buffer = io.BytesIO(model_multiclass)
        model_file = h5py.File(model_buffer, 'r')
        print('load server ===> model_multiclass.h5')
        return load_model(model_file)


def get_map_encode_data(lpg_group_id, map_encode_data_file):
    if (get_from_cache(lpg_group_id, map_encode_data_file)) is not None:
        loaded_encode_data = get_from_cache(lpg_group_id, map_encode_data_file)
        print('load cache ===> ', map_encode_data_file)
        return loaded_encode_data

    if not get_from_server(lpg_group_id, map_encode_data_file):
        raise FileNotFoundError("Assets for Landing Page Group ID not found!")

    if get_from_server(lpg_group_id, map_encode_data_file):
        encode_data = get_from_server(lpg_group_id, map_encode_data_file)
        encode_data_buffer = io.BytesIO(encode_data)
        loaded_encode_data = json.load(encode_data_buffer)
        print('load server ===> ', map_encode_data_file)
        return loaded_encode_data


def get_train_data(lpg_group_id, train_data_file):
    if (get_from_cache(lpg_group_id, train_data_file)) is not None:
        loaded_train_data = get_from_cache(lpg_group_id, train_data_file)
        print('load cache ===> ', train_data_file)
        return loaded_train_data

    if not get_from_server(lpg_group_id, train_data_file):
        raise FileNotFoundError("Assets for Landing Page Group ID not found!")

    if get_from_server(lpg_group_id, train_data_file):
        train_data = get_from_server(lpg_group_id, train_data_file)
        train_data_buffer = io.BytesIO(train_data)
        loaded_train_data = pd.read_csv(train_data_buffer,header=0, delimiter=",",low_memory=False)
        print('load server ===> ', train_data_file)
        return loaded_train_data


def create_cache_entry(lpg_group_id):
    try:
        loaded_model = get_model(lpg_group_id)
        arguments_cache[lpg_group_id] = dict()
        arguments_cache[lpg_group_id]['model_multiclass_h5'] = dict()
        arguments_cache[lpg_group_id]['model_multiclass_h5'] = loaded_model

        loaded_encode_data_output = get_map_encode_data(lpg_group_id, 'map_encode_data_output.json')
        arguments_cache[lpg_group_id]['encode_data_output'] = dict()
        arguments_cache[lpg_group_id]['encode_data_output'] = loaded_encode_data_output

        loaded_encode_data_input = get_map_encode_data(lpg_group_id, 'map_encode_data_input.json')
        arguments_cache[lpg_group_id]['encode_data_input'] = dict()
        arguments_cache[lpg_group_id]['encode_data_input'] = loaded_encode_data_input

        loaded_encode_data_training = get_train_data(lpg_group_id, 'encode_data_training.csv')
        arguments_cache[lpg_group_id]['encode_data_training'] = dict()
        arguments_cache[lpg_group_id]['encode_data_training'] = loaded_encode_data_training

        loaded_encode_data_training_y= get_train_data(lpg_group_id, 'encode_data_training_y.csv')
        arguments_cache[lpg_group_id]['encode_data_training_y'] = dict()
        arguments_cache[lpg_group_id]['encode_data_training_y'] = loaded_encode_data_training_y

    except FileNotFoundError as ex:
        raise ex


