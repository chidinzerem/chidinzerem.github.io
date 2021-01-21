#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------
# Penji OpDev Fall 2019
# < File Function >
# Author: Cory Paik
# Updated: < MM.DD.YEAR >
# ------------------------

# General
import os
import argparse
import importlib.util
# Local
from core.config import cfg
from core.utils import setup_logger, load_user_profile, setup_data_dir
from core import logger


def run(args):
    path = f'orgScrapers/{args.school}.py'
    spec = importlib.util.spec_from_file_location('Scraper', path)
    web_scraper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(web_scraper)
    explored_subjects = web_scraper.Scraper(args).run()
    logger.info(f'Explored Subjects: \n{explored_subjects}\n----------')


if __name__ == '__main__':
    # Parser for command inputs
    parser = argparse.ArgumentParser('Course Scraping Runner')
    # General PenjiDev Args
    parser.add_argument('-user', help='Enter user from config', default='PAIK')
    parser.add_argument('-school', help='Enter a school name', required=True)
    parser.add_argument('-term', help='Enter a term', default='fall19')
    parser.add_argument('-test', action='store_true', help='Test Runs')
    parser.add_argument('-ns', action='store_true', help='No Saving')
    parser.add_argument('-log', help='Enter logger level: debug, info, warn, error, none', default='info', type=str)
    # General Variable Help messages
    parser.add_argument('-reset', action='store_true', help='Reset Files')
    # Special Args
    parser.add_argument('-width', help='Width Ratio', default=1, type=float)
    parser.add_argument('-height', help='Height Ratio', default=0.75, type=float)
    parser.add_argument('-headless', action='store_true', help='Headless')

    parser_args = parser.parse_args()
    parser_args.save = not parser_args.ns
    parser_args = load_user_profile(parser_args)
    setup_logger(parser_args, 'student_org')
    setup_data_dir(args=parser_args)
    run(args=parser_args)
