

## A function to map a reading to a value in a range
def map_reading(in_val, output_values, raw_readings=[4,20], ignore_below=3):

    if in_val < ignore_below:
        return None

    ## Choose the value set to map between
    lower_val_ind = 0
    found = False
    for i in range(0, len(raw_readings)):
        if in_val <= raw_readings[i]:
            lower_val_ind = i-1
            found = True
            break

    if not found:
        lower_val_ind = len(raw_readings)-2

    # Figure out how 'wide' each range is
    inSpan = raw_readings[lower_val_ind + 1] - raw_readings[lower_val_ind]
    outSpan = output_values[lower_val_ind + 1] - output_values[lower_val_ind]

    # Convert the left range into a 0-1 range (float)
    valueScaled = float(in_val - raw_readings[lower_val_ind]) / float(inSpan)

    # Convert the 0-1 range into a value in the right range.
    return output_values[lower_val_ind] + (valueScaled * outSpan)


def find_object_with_key(obj, key_to_find):
    stack = [obj]

    while stack:
        current = stack.pop()

        if isinstance(current, dict):
            if key_to_find in current:
                return current[key_to_find]

            for key in current:
                stack.append(current[key])

    return None


def find_path_to_key(obj, key_to_find):
    stack = [{'current': obj, 'path': ''}]

    while stack:
        current_entry = stack.pop()
        current = current_entry['current']
        path = current_entry['path']

        if isinstance(current, dict):
            if key_to_find in current:
                return f"{path}.{key_to_find}" if path else key_to_find

            for key in current:
                new_path = f"{path}.{key}" if path else key
                stack.append({'current': current[key], 'path': new_path})

    return None