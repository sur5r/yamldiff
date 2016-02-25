# -*- coding: utf-8 -*-
"""
Created on Thu Feb 25 12:01:58 2016

@author: Zahari Kassabov
"""
import sys
import argparse

from yamldiff import yaml_diff, parse_keys


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