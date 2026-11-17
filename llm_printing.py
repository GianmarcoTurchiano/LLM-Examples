import json

def print_dictionary(d):
    j = json.dumps(d, indent=4)
    print(j)