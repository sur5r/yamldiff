# -*- coding: utf-8 -*-
"""
yamldiff.py

Compute the difference between two YAML files.

Created on Thu Dec 24 18:19:07 2015

@author: Zahari Kassabov
"""
import sys
from collections import namedtuple, OrderedDict
import contextlib
import argparse
import pickle

import ruamel.yaml as yaml
import blessings

Diff = namedtuple("Diff", ('first_only', 'second_only', 'different_vals'))

class HashAny:
    """Simple utility to class to make any object hashable, using the
    pickle representation of the object. It does not check for the inmutability
    of the object, and usig mutated HasAny objects as keys is a bad idea."""
    def __init__(self, val):
        self.val = val

    def __hash__(self):
        return hash(pickle.dumps(self.val))

    def __eq__(self, other):
        return self.val == other.val

#This might need to be a fancier transparent proxy object.
class Label(HashAny):
    def __init__(self, val, index_key):
        self.val = val
        self.index_key = index_key

    def __str__(self):
        return str(self.val)

    def spec_str(self):
        return dict_repr({self.index_key: self.val})

def val_diff(v1,v2):
    if isinstance(v1, dict) and isinstance(v2, dict):
        return dict_diff(v1, v2)
    elif isinstance(v1, set) and isinstance(v2, set):
        return set_diff(v1, v2)
    return (v1, v2)

def dict_diff(dict1, dict2):

    #Keep ordering if we have it
    if isinstance(dict1, OrderedDict):
        first_only_keys = [k for k in dict1.keys() if k not in dict2.keys()]
    else:
        first_only_keys = dict1.keys() - dict2.keys()
    first_only = {k:dict1[k] for k in first_only_keys}

    if isinstance(dict2, OrderedDict):
        second_only_keys = [k for k in dict2.keys() if k not in dict1.keys()]
    else:
        second_only_keys = dict2.keys() - dict1.keys()
    second_only = {k:dict2[k] for k in second_only_keys}

    if isinstance(dict1, OrderedDict):
        same_keys = [k for k in dict1.keys() if k in dict2.keys()]
    else:
        same_keys = dict1.keys() & dict2.keys()
    different_vals = type(dict1)((k, val_diff(dict1[k], dict2[k]))
                                 for k in same_keys
                                 if dict1[k] != dict2[k])
    return Diff(first_only, second_only, different_vals)

def set_diff(set1, set2):
    first_only = set1 - set2
    second_only = set2 - set1
    return Diff(first_only, second_only, set())

def print_indent(s, indent_level=0):
    s = str(s)
    t = blessings.Terminal()
    if s.startswith('+'):
        s = t.bold_green(s)
    elif s.startswith('-'):
        s = t.bold_red(s)
    elif s.startswith('#'):
        s = t.yellow(s)
    indent = '    '*indent_level
    print(indent + s)

def reprocess_dict(d, set_keys):
    if not isinstance(d, dict):
        return d
    reproc = PrintableOrderedDict()
    for k, v in d.items():
        if isinstance(v, dict):
            result = reprocess_dict(v, set_keys)
        elif (isinstance(v, list) or isinstance(v, set)):
            if k in set_keys:
                index = set_keys[k]
                if index is NoKey:
                    #Can't use dict comprehension here because we have to
                    # hash the reprocessed item
                    result = {}
                    for item in v:
                        reprocessed = reprocess_dict(item, set_keys)
                        result[HashAny(reprocessed)] = reprocessed
                else:
                    result = {Label(item[index], index):
                              reprocess_dict(item, set_keys)
                              for item in v}
            else :
                result = [reprocess_dict(item, set_keys) for item in v]
        else:
            result = v

        reproc[k] = result
    return reproc


class PrintableOrderedDict(OrderedDict):
    def __repr__(self):
        return dict_repr(self)


def dict_repr(dic):
    return '{%s}' % ', '.join(keyvalue_string(*item) for item in dic.items())

def keyvalue_string(key, value):
    #Cast ruamel.yaml types for priting.

    if isinstance(value, list) or isinstance(value, tuple):
        value = [keyvalue_string(HashAny(None), item) for item in value]
    if isinstance(value, dict):
        value = dict_repr(value)
    if isinstance(key, HashAny) or isinstance(key, Label):
        return str(value)
    else:
        return '{}: {}'.format(key, value)


def print_diff(diff, *, file=None, indent_level=0):
    first_only, second_only, different_keys = diff
    if file is None:
        file = sys.stdout
    with contextlib.redirect_stdout(file):
        if first_only:
            print_indent("# Removed keys:", indent_level=indent_level)
            for k in first_only:
                if isinstance(k, Label):
                        print_indent("# {}: {}".format(k.index_key, k),
                                     indent_level=indent_level)
                if isinstance(first_only, dict):
                    print_indent("- %s" % keyvalue_string(k, first_only[k]),
                      indent_level=indent_level)
                else:
                    print_indent("- {}".format(k),
                      indent_level=indent_level)
        if second_only:
            print_indent("# Added keys:", indent_level=indent_level)
            for k in second_only:
                if isinstance(k, Label):
                        print_indent("# {}: {}".format(k.index_key, k),
                                      indent_level=indent_level)
                if isinstance(second_only, dict):
                    print_indent("+ %s" % keyvalue_string(k, second_only[k]),
                      indent_level=indent_level)
                else:
                    print_indent("+ {}".format(k),
                      indent_level=indent_level)

        if different_keys:
            print_indent("# Modified keys:", indent_level=indent_level)
            for k in different_keys:
                if isinstance(k, Label):
                        print_indent("# Matching:", indent_level=indent_level)
                        print_indent(k.spec_str(),
                                     indent_level=indent_level)
                else:
                    print_indent(str(k) + ":", indent_level=indent_level)
                v = different_keys[k]
                if isinstance(v, Diff):
                    print_diff(v, indent_level = indent_level+1)
                else:
                    print_indent("- " + str(v[0]), indent_level=indent_level+1)
                    print_indent("+ " + str(v[1]), indent_level=indent_level+1)

def yaml_diff(p1, p2,  *, set_keys=None):
    with open(p1) as f1:
        d1 = yaml.load(f1,Loader=yaml.RoundTripLoader)
    with open(p2) as f2:
        d2 = yaml.load(f2, Loader=yaml.RoundTripLoader)

    try:
        d1 = reprocess_dict(d1, set_keys)
        d2 = reprocess_dict(d2, set_keys)
    except KeyError as e:
        raise ValueError("Bad set key: {}".format(next(iter(e.args))))
    diff = dict_diff(d1, d2)
    print_diff(diff)

class NoKey: pass

def parse_keys(keys):
    if not keys:
        return
    for key in keys:
        spec = key.split(':')
        if len(spec) == 2:
            name, index = spec
        elif len(spec) == 1:
            name, index = *spec, NoKey
        else:
            raise ValueError("Wrong spec")
        yield (name, index)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('file1')
    parser.add_argument('file2')
    parser.add_argument('--set-keys', nargs='+')
    args = parser.parse_args()
    try:
        set_keys = dict(parse_keys(args.set_keys))
    except ValueError:
        sys.exit("Bad spec")
    try:
        yaml_diff(args.file1, args.file2, set_keys=set_keys)
    except ValueError as e:
        sys.exit(str(e))

if __name__ == '__main__':
    main()