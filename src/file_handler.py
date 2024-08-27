import json
import os


def ReadJSON(filename: str):
    with open(filename, "r") as file:
        data = json.load(file)
    return data


def CreateJSON(filename: str):
    if not filename.endswith(".json"):
        raise ValueError("Provided filename is not a JSON file.")

    base_filename = filename.removesuffix(".json")

    new_filename = f"{base_filename}_ptbr.json"
    if not os.path.exists(new_filename):
        return open(new_filename, "x")

    i = 1
    while os.path.exists(f"{new_filename}_ptbr ({i}).json"):
        i += 1
    return open(f"{new_filename}_ptbr ({i}).json", "x")
