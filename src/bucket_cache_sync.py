import os
import tempfile

import boto3
import redis
from keras import models


def copy_file_to_redis(bucket_name, dataset, file_name):
    key_name=dataset + "/" + file_name

    s3 = boto3.resource('s3',
                        aws_access_key_id=os.environ.get('aws_access_key_id'),
                        aws_secret_access_key=os.environ.get('aws_secret_access_key'),
                        region_name=os.environ.get('region_name'))

    bucket = s3.Bucket(bucket_name)
    obj = bucket.Object(key_name)
    redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)
    redis_client.hset('api-cache', key_name, obj.get()['Body'].read())

def copy_model_to_redis(bucket_name, dataset, model_name):
    client = boto3.client('s3',
                          aws_access_key_id=os.environ.get('aws_access_key_id'),
                          aws_secret_access_key=os.environ.get('aws_secret_access_key'),
                          region_name=os.environ.get('region_name'))

    key_name = dataset + "/" + model_name

    response_data = client.get_object(
        Bucket=bucket_name,
        Key=key_name
    )
    response_data = response_data['Body']
    response_data = response_data.read()
    with tempfile.TemporaryDirectory() as tempdir:
        with open(f"{tempdir}/{model_name}", 'wb') as my_data_file:
            my_data_file.write(response_data)
            gotten_model = models.load_model(f"{tempdir}/{model_name}").to_json()
            redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)
            redis_client.hset('api-cache', key_name, gotten_model)


BUCKET_NAME = "ai.artifacts.clickster.io"
dataset = '65513757cf7194001ae53caa'
file_names = [
    'encode_data_training.csv',
    'map_encode_data_input.json',
    'encode_data_training_y.csv',
    'map_encode_data_output.json',
    'model_parameters.json',
    'model_multiclass.h5'
]

for file_name in file_names:
    copy_file_to_redis(BUCKET_NAME, dataset, file_name)
