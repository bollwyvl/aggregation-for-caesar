#!/usr/bin/env python

from collections import OrderedDict
import copy
from panoptes_aggregation import reducers
from panoptes_aggregation.csv_utils import flatten_data, unflatten_data, order_columns
import json
import math
import numpy as np
import io
import os
import pandas
import progressbar
import warnings


def first_filter(data):
    first_time = data.created_at.min()
    fdx = data.created_at == first_time
    return data[fdx]


def last_filter(data):
    last_time = data.created_at.max()
    ldx = data.created_at == last_time
    return data[ldx]


def reduce_csv(extracted_csv, filter='first', keywords={}, output='reductions', order=False, stream=False):
    if not isinstance(extracted_csv, io.IOBase):
        extracted_csv = open(extracted_csv, 'r')

    with extracted_csv as extracted_csv_in:
        extracted = pandas.read_csv(extracted_csv_in, infer_datetime_format=True, parse_dates=['created_at'])

    extracted.sort_values(['subject_id', 'created_at'], inplace=True)

    resume = False
    subjects = extracted.subject_id.unique()
    tasks = extracted.task.unique()
    workflow_id = extracted.workflow_id.iloc[0]
    extractor_name = extracted.extractor.iloc[0]
    reducer_name = extractor_name.replace('extractor', 'reducer')
    if (reducer_name == 'sw_reducer') or (reducer_name == 'line_text_reducer'):
        reducer_name = 'poly_line_text_reducer'
    if reducer_name == 'sw_graphic_reducer':
        reducer_name = 'rectangle_reducer'

    output_path, output_base = os.path.split(output)
    output_base_name, output_ext = os.path.splitext(output_base)
    output_name = os.path.join(output_path, '{0}_{1}.csv'.format(reducer_name, output_base_name))

    if stream:
        if os.path.isfile(output_name):
            print('resuming from last run')
            resume = True
            with open(output_name, 'r') as reduced_file:
                reduced_csv = pandas.read_csv(reduced_file)
                subjects = np.setdiff1d(subjects, reduced_csv.subject_id)

    blank_reduced_data = OrderedDict([
        ('subject_id', []),
        ('workflow_id', []),
        ('task', []),
        ('reducer', []),
        ('data', [])
    ])

    reduced_data = copy.deepcopy(blank_reduced_data)

    widgets = [
        'Reducing: ',
        progressbar.Percentage(),
        ' ', progressbar.Bar(),
        ' ', progressbar.ETA()
    ]

    pbar = progressbar.ProgressBar(widgets=widgets, max_value=len(subjects))
    pbar.start()
    for sdx, subject in enumerate(subjects):
        idx = extracted.subject_id == subject
        for task in tasks:
            jdx = extracted.task == task
            classifications = extracted[idx & jdx]
            classifications = classifications.drop_duplicates()
            if filter == 'first':
                classifications = classifications.groupby(['user_name'], group_keys=False).apply(first_filter)
            elif filter == 'last':
                classifications = classifications.groupby(['user_name'], group_keys=False).apply(last_filter)
            data = [unflatten_data(c) for cdx, c in classifications.iterrows()]
            reduction = reducers.reducers[reducer_name](data, **keywords)
            if isinstance(reduction, list):
                for r in reduction:
                    reduced_data['subject_id'].append(subject)
                    reduced_data['workflow_id'].append(workflow_id)
                    reduced_data['task'].append(task)
                    reduced_data['reducer'].append(reducer_name)
                    reduced_data['data'].append(r)
            else:
                reduced_data['subject_id'].append(subject)
                reduced_data['workflow_id'].append(workflow_id)
                reduced_data['task'].append(task)
                reduced_data['reducer'].append(reducer_name)
                reduced_data['data'].append(reduction)
        if stream:
            if (sdx == 0) and (not resume):
                pandas.DataFrame(reduced_data).to_csv(output_name, mode='w', index=False)
            else:
                pandas.DataFrame(reduced_data).to_csv(output_name, mode='a', index=False, header=False)
            reduced_data = copy.deepcopy(blank_reduced_data)
        pbar.update(sdx + 1)
    pbar.finish()

    if stream:
        reduced_csv = pandas.read_csv(output_name)
        if 'data' in reduced_csv:
            reduced_csv.data = reduced_csv.data.apply(eval)
            flat_reduced_data = flatten_data(reduced_csv)
        else:
            return output_name
    else:
        flat_reduced_data = flatten_data(reduced_data)
    if order:
        flat_reduced_data = order_columns(flat_reduced_data, front=['choice', 'total_vote_count', 'choice_count'])
    flat_reduced_data.to_csv(output_name, index=False)
    return output_name


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="reduce data from panoptes classifications based on the extracted data (see extract_panoptes_csv)")
    parser.add_argument("extracted_csv", help="the extracted csv file output from extract_panoptes_csv", type=argparse.FileType('r'))
    parser.add_argument("-F", "--filter", help="how to filter a user makeing multiple classifications for one subject", type=str, choices=['first', 'last', 'all'], default='fisrt')
    parser.add_argument("-k", "--keywords", help="keywords to be passed into the reducer in the form of a json string, e.g. \'{\"eps\": 5.5, \"min_samples\": 3}\'  (note: double quotes must be used inside the brackets)", type=json.loads, default={})
    parser.add_argument("-O", "--order", help="arrange the data columns in alphabetical order before saving", action="store_true")
    parser.add_argument("-o", "--output", help="the base name for output csv file to store the reductions", type=str, default="reductions")
    parser.add_argument("-s", "--stream", help="stream output to csv after each redcution (this is slower but is resumable)", action="store_true")
    args = parser.parse_args()

    reduce_csv(args.extracted_csv, filter=args.filter, keywords=args.keywords, output=args.output, order=args.order, stream=args.stream)
