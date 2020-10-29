import os


def get_or_env(value, name):
    if value is not None:
        return value
    return os.environ.get(name)
