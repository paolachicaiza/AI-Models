def get_value_from_json(json_obj, path):
    keys = path.split('.')
    current_obj = json_obj

    try:
        for key in keys:
            current_obj = current_obj.get(key)
            if current_obj is None:
                return "Unknown"
    except (AttributeError, KeyError):
        return "Unknown"

    return current_obj
