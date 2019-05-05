import random
from libraries import envparser

env_variables = envparser.parse_file('.env')

def envs():
    return env_variables


def env(key):
    return env_variables[key] or None

def random_string(size):
    # Ref: https://stackoverflow.com/questions/55556/characters-to-avoid-in-automatically-generated-passwords
    chars = '!#%+23456789:=?ABCDEFGHJKLMNPRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
    return ''.join(random.choice(chars) for _ in range(size))