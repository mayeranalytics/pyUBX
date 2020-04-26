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

def getMessageName(cls, withUBX=True, withMessageClass=True, withMessageName=True, separator="."):
    """
    Get the name of the message that corresponds to the class.

    The classname for a message is ubx.UBX.{msgclass}.{msgclass}.{msgname}
    with the .{msgname} missing if cls is the Message Class class rather than a submessge
    :param cls:
    :param withUBX:
    :param withMessageClass:
    :param withMessageName:
    :param separator: string to put between components
    :return:
    """
    classNameParts = getClassName(cls).split(".")
    assert classNameParts[0] == "ubx" and classNameParts[1] == "UBX"
    assert classNameParts[2] == classNameParts[3]   # Duplicated msgclass
    parts = []
    if withUBX:
        parts.append(classNameParts[1])
    if withMessageClass:
        parts.append(classNameParts[2])
    if withMessageName and len(classNameParts) > 4:
        parts.append(classNameParts[4])
    return separator.join(parts)



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
