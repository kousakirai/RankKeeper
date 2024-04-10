import json
import io
import pickle
import codecs

def jsonkey_to_int_when_possible(x):  # yamlと同様の挙動をさせたいときはこちら
    d = {}
    if isinstance(x, dict):
        for k, v in x.items():
            try:
                k = int(k)
            except ValueError:
                pass
            d[k] = v
        return d
