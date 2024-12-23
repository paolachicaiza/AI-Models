import time, sys, json, os
import numpy as np
import pandas as pd
from __main__ import app
from numpy import array
from flask import json, request
from sklearn.model_selection import train_test_split
from src.cache_manager import create_cache_entry, arguments_cache
from pylogger import logger

from src.constans import column_mapping, columns_df, columns_df_total
from src.get_value_from_json import get_value_from_json


@app.route('/predict', methods=['GET','POST'])
# @auth_required
def predictionOneRecordJsonPostHandler():
    """

      @format /predict?lpg_group_id=63883c4716dc8b001ad85ee1

    """
    try:
        args = request.args
        lpg_group_id = args.get("lpg_group_id", type=str)

        request_data = request.get_json()
        data_json_open_load = request_data

        create_cache_entry(lpg_group_id)


        model = arguments_cache.get(lpg_group_id).get("model_multiclass_h5")
        encode_data_output_load = arguments_cache.get(lpg_group_id).get("encode_data_output")
        encode_data_input_load = arguments_cache.get(lpg_group_id).get("encode_data_input")
        encode_data_training = arguments_cache.get(lpg_group_id).get("encode_data_training")
        encode_data_training_y = arguments_cache.get(lpg_group_id).get("encode_data_training_y")

        start = time.time()
        data = []

        for column in columns_df:
            json_path = column_mapping.get(column)
            value = get_value_from_json(data_json_open_load, json_path)
            data.append(value)

        tokens = data_json_open_load.get("visitor").get("tokens")

        if tokens:
            filter_adh = [visitor_token for visitor_token in tokens if visitor_token.get("parameter") == "adh"]
            if not filter_adh:
                filter_adh = "Unknown"
            else:
                filter_adh = filter_adh[0].get("value")
            data.append(filter_adh)

        if tokens:
            filter_cadid = [visitor_token for visitor_token in tokens if visitor_token.get("parameter") == "cadid"]
            if not filter_cadid:
                filter_cadid = "Unknown"
            else:
                filter_cadid = filter_cadid[0].get("value")
            data.append(filter_cadid)

        if tokens:
            filter_adi = [visitor_token for visitor_token in tokens if visitor_token.get("parameter") == "adi"]
            if not filter_adi:
                filter_adi = "Unknown"
            else:
                filter_adi = filter_adi[0].get("value")
            data.append(filter_adi)

        if not tokens:
            filter_adh = "Unknown"
            data.append(filter_adh)
            filter_cadid = "Unknown"
            data.append(filter_cadid)
            filter_adi = "Unknown"
            data.append(filter_adi)

        data.append(data_json_open_load.get('converted_yes', "1"))
        data.append(data_json_open_load.get('converted_no', "0"))

        data = [data]
        # print("data from customer: ", data)

        df = pd.DataFrame(data, columns=columns_df_total)

        df.isna().sum().sort_values()
        x_data_values = df

        columns = list(x_data_values.keys())
        x_real = []
        x_data = []
        for col in columns:
            x_data_real = (encode_data_input_load.get(str(col))).get(x_data_values[str(col)].iloc[0])
            x_real.append(x_data_real)
            x_data_item = (encode_data_input_load.get(str(col))).get(x_data_values[str(col)].iloc[0], 0)
            x_data.append(x_data_item)

        df_encoded_x_read = encode_data_training
        encoded_x = df_encoded_x_read.to_numpy()
        encoded_x = np.delete(encoded_x, 0, axis=1)

        df_dummy_y_read = encode_data_training_y
        dummy_y = df_dummy_y_read.to_numpy()
        dummy_y = np.delete(dummy_y, 0, axis=1)

        # split data into train and test sets
        x_train, x_test, y_train, y_test = train_test_split(encoded_x, dummy_y, test_size=0.30, random_state=123)
        x_test = array([x_data])

        from sklearn.preprocessing import StandardScaler
        scaler = StandardScaler()
        scaler.fit(x_train)
        x_test = scaler.transform(x_test)

        x_data_to_predict = x_test

        prediction_vector = (model.predict(x_data_to_predict))
        prediction_number = prediction_vector.argmax(1)
        predictions_int = prediction_number[0].astype(int)
        landing_page_id = (encode_data_output_load.get("landing_page_id")).get(str(predictions_int))

        fin = time.time()
        time_prediction = (fin - start) * 1000

        data = {
            "landing_page_id": landing_page_id,
            "prediction_time": time_prediction,
            "success": True
        }

        response = app.response_class(
            response=json.dumps(data),
            status=200,
            mimetype='application/json'
        )
        return response
    except Exception as error:
        #logger.error(error)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        response = app.response_class(
            response=json.dumps({
                'success': False,
                'type': error.__class__.__name__,
                'message': [
                    'Model from Redis:',
                    str(lpg_group_id),
                    str(exc_type),
                    str(fname),
                    str(exc_tb.tb_lineno)
                ]
            }),
            status=500,
            mimetype='application/json'
        )
        return response
