#!/usr/bin/env python
"""
Evaluate an annotation task.
"""

import os
import argparse
import json
import lmdb

from paths import Paths

def get_classes(args):
    """Get list of classes.

    Args:
        args: command line args

    Returns:
        list of classes
    """
    with open(Paths.tasks_json, 'r') as f:
        data = json.load(f)
    return data[args.task_id]['classes']

def main():
    parser = argparse.ArgumentParser(description='Evaluate task.')
    parser.add_argument('task_id', type=str, help='task id')
    args = parser.parse_args()

    # set up data and counters
    classes = get_classes(args)
    class_counter = {}
    for class_index, _ in enumerate(classes):
       class_counter[class_index] = 0
    total_counter = 0

    # read from lmdb
    with lmdb.open(Paths.annotations_db(args.task_id), map_size=pow(2, 40)) as env:
        with env.begin(write=False) as txn:
            cursor = txn.cursor()
            for key, value in cursor:
                value = int(value)
                if value not in class_counter:
                    raise ValueError('encountered unexpected label {0} for key {1}'.format(value, key))
                class_counter[value] += 1
                total_counter += 1

    # print results
    for class_index, class_label in enumerate(classes):
        print "Num {0}: {1}".format(class_label, class_counter[class_index])
    print "Total: {0}".format(total_counter)

main()
