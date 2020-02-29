#!/usr/bin/env python3
"""Define some functions for object introspections."""
import inspect
import re


def getClassName(cls):
    """Return the class name of the object.

    Throws an exception if the object is not a class.
    """
    if not inspect.isclass(cls):
        raise Exception("{} is not a class".format(cls))
    m = re.match(r"<class '(.*)'>", str(cls))
    if m is None:
        raise Exception("This shouldn't happen")
    return m.group(1)


def getClassMembers(cls, predicate=None):
    """Return the non-hidden class members as key value pairs.

    Throws an exception if the object is not a class.
    """
    return [(k, v) for k, v in inspect.getmembers(cls, predicate)
            if not k.find("__") == 0]


def getClassesInModule(module):
    """Return the classes defined in a module as key value pairs."""
    if not module.__class__.__name__ == 'module':
        raise Exception("{} is not a module".format(module))
    return [v
            for k, v in inspect.getmembers(module, inspect.isclass)
            if v.__module__.find(module.__name__+".") == 0]
