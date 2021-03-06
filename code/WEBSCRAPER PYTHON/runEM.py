#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------
# Penji OpDev Fall 2019
# Email Scraping Run Wrapper
# Author: Cory Paik
# Updated:
# ------------------------

# General
import os
import argparse
import importlib.util
# Local
from core.config import cfg
from core.utils import setup_logger, load_user_profile
from core import logger


def run(args):
    path = f'emailScrapers/{args.school}.py'
    spec = importlib.util.spec_from_file_location('Scraper', path)
    email_scraper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(email_scraper)
    explored_professors = email_scraper.Scraper(args).run()
    logger.info(f'Explored Professors: \n{explored_professors}\n----------')


if __name__ == '__main__':
    # Parser for command input
    parser = argparse.ArgumentParser('Main Automation Runner')
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


    setup_logger(parser_args, 'email')

    run(args=parser_args)
