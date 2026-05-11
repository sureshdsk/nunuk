from a import greet
from b import shout

def loud_greet(name):
    return shout(greet(name))
