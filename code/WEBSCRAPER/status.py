#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------
# Penji OpDev Fall 2019
# Check Status of School
# Author: Cory Paik
# Updated: 02.08.2019
# ------------------------

# General
import os
import shutil
import pickle
import argparse
from collections import OrderedDict
from pprint import pprint as pprint
# Local
from core.config import cfg
from core.utils import setup_logger, load_user_profile
from core import logger



s_temp = OrderedDict()
s_temp['ready'] = 'No'
s_temp['course_scraper'] = 'Not Started'
s_temp['email_scraper'] = 'Not Started'
s_temp['Professor Archive'] = 'Not Started'
s_temp['Course Archive'] = 'Not Started'
s_temp['Archive Updated'] = '<term>'
s_temp['GS Prepped'] = 'No'
s_temp['GS Uploaded'] = 'No'
s_temp['Notes'] = ''

update_columns = (
        'Signoff (Name, Date)',
        'Pre-Approval Status',
        'LHP Response (yes/no)',
        'Planned Date',
        'Notes')






def update_status(args, status_dict):
    print('For each displayed argument enter a value or leave it blank\n'
          '------------------------------------------------------------')
    for key, value in status_dict.items():
        print(f'CURRENT: {key} = {value}')
        new_val = input(f'INPUT -> {key} = ')
        print('------------------------------')
        if new_val != '':
            status_dict[key] = new_val
    info_str ='Will Update Information To:\n' \
              '------------------------------'
    for key, value in status_dict.items():
        info_str += f'\n      {key} : {value}'
    logger.info(info_str)
    to_save = input(f'Press enter to continue')
    file_name = f'data/{args.school}/status.p'
    pickle.dump(status_dict, open(file_name, 'wb'))



def check_status(args):
    # Open pickle file or create one
    file_name = f'data/{args.school}/status.p'
    if os.path.exists(file_name):
        status_dict = pickle.load(open(file_name, 'rb'))
    else:
        status_dict = s_temp
        pickle.dump(status_dict, open(file_name, 'wb'))

    info_str = f'Current Status for {cfg[args.school.upper()].NICE_NAME}'
    for key, value in status_dict.items():
        info_str += f'\n      {key} : {value}'
    logger.info(info_str)
    return status_dict

def reset_status(args):
    if os.path.exists(f'data/{args.school}/status.p'):
        os.remove(f'data/{args.school}/status.p')

def reset_logs(args):
    if os.path.exists(f'data/{args.school}/logs'):
        shutil.rmtree(f'data/{args.school}/logs')

if __name__ == '__main__':
    # Parser for command input
    parser = argparse.ArgumentParser('Check or Update Status of School ')
    # General PenjiDev Args
    parser.add_argument('-school', help='Enter a school name', required=True)
    parser.add_argument('-term', help='Enter a term', default='fall19')
    parser.add_argument('-test', action='store_true', help='Test Runs')
    parser.add_argument('-log', help='Enter logger level: debug, info, warn, error, none', default='info', type=str)
    # Special Args
    parser.add_argument('-update', action='store_true', help='Update Status')
    parser.add_argument('-reset_status', action='store_true', help='Reset Status')
    parser.add_argument('-reset_logs', action='store_true', help='Reset Log Files')
    parser_args = parser.parse_args()
    setup_logger(parser_args, 'status')
    # Always Check Status First
    if parser_args.reset_status:
        reset_status(parser_args)
    status_dict = check_status(parser_args)
    if parser_args.update:
        update_status(parser_args, status_dict)
    if parser_args.reset_logs:
        reset_logs(parser_args)

