import json


def processor_name(name: str) -> str:
    return "#" + name.lstrip("#")


def task_name(name: str) -> str:
    return "!" + name.lstrip("!")


def maybe_json(data: str):
    try:
        return json.loads(data)
    except json.JSONDecodeError:
        pass

    num_occ = len([n for n in data if n == "'"])
    if num_occ > 0 and num_occ % 2 == 0 and len([n for n in data if n == "{"]) == len([n for n in data if n == "}"]):
        return maybe_json(data.replace("'", '"'))

    return data


class BoolFlag:
    def __call__(self, *args, **kwargs):
        return
