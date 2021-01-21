#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------
# Penji OpDev Fall 2019
# Course Scraper Utilities
# Author: Cory Paik
# ------------------------

import os
import csv
import time
import shutil
import functools

import pandas as pd
import numpy as np

# For the Locator Class
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
# Local
from core import logger
from core.config import cfg

#---------------
# Common core functions shared across all scrapers
#
#
#----------------

def setup_data_dir(args):
    # Base Directory
    base_dir = f'data/{args.school}'
    if not os.path.isdir(base_dir):
        os.mkdir(base_dir)
    # Get the term (<nice name>, <file name>, <abbr>)
    try:
        cterm = cfg.GENERAL[args.term.upper()]
        pterm = cfg.GENERAL[args.term.upper() + '_PREV']
    except KeyError:
        logger.error(f'{args.term} not a valid option for term')
        raise SystemExit
    # Current Term
    if not os.path.isdir(base_dir+'/'+cterm[1]):
        os.mkdir(base_dir+'/'+cterm[1])
    # Previous Term
    if not os.path.isdir(base_dir+'/'+pterm[1]):
        os.mkdir(base_dir+'/'+pterm[1])
    # Archive
    if not os.path.isdir(base_dir+'/archive'):
        os.mkdir(base_dir+'/archive')


def setup_logger(args, run_mode):
    # Setup the logger
    log_dir = os.getcwd() + f'/data/test_runs/log_{run_mode}' if args.test \
        else os.getcwd() + f'/data/{args.school}/logs/log_{args.term}_{run_mode}'
    if os.path.exists(log_dir):
        shutil.rmtree(log_dir)
    logger.configure(dir=log_dir)
    logger.set_level(cfg.GENERAL.LOGGER_LEVELS[args.log.upper()])

def load_user_profile(args):
    # Driver Args
    args.driver = None
    if os.name == 'nt':
        args.driver = cfg[args.user].WIND_DRIVER
    elif os.name == 'posix':
        args.driver = cfg[args.user].MACOS_DRIVER
    if not args.driver:
        raise RuntimeError(f'{os.name} driver not specified in config file for user {args.user}')
    return args

class Locator(object):
    def __init__(self, main_driver):
        self.types = {
            'class'       : By.CLASS_NAME,
            'css_selector': By.CSS_SELECTOR,
            'id'          : By.ID,
            'link_text'   : By.LINK_TEXT,
            'name'        : By.NAME,
            'p_link_text' : By.PARTIAL_LINK_TEXT,
            'tag'         : By.CSS_SELECTOR,
            'xpath'       : By.XPATH,
        }
        self.main_driver = main_driver

    def wait_for_ajax(self, driver=None):
        driver = driver if driver else self.main_driver
        wait = WebDriverWait(driver, 15)
        try:
            wait.until(lambda driver: driver.execute_script('return jQuery.active') == 0)
            wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
        except Exception as e:
            pass

    def __call__(self, type, locator, driver=None, multiple=False, info=None, text=False, iText=False, secs=10, report=True, button=False):
        self.wait_for_ajax()
        driver = driver if driver else self.main_driver
        try:
            if multiple:
                element = WebDriverWait(driver, secs).until(
                    EC.presence_of_all_elements_located((self.types[type], locator)))
                if text:
                    return [e.text for e in element]
                elif iText:
                    return [e.get_attribute('innerText') for e in element]
            else:
                element = WebDriverWait(driver, secs).until(
                    EC.presence_of_element_located((self.types[type], locator)))
                if button:
                    element = WebDriverWait(driver, secs).until(
                        EC.element_to_be_clickable((self.types[type], locator)))
                elif text:
                    return element.text
                elif iText:
                    return element.get_attribute('innerText')
            return element
        except:
            if secs>0 and report:
                if info:
                    logger.warn(f'Error In processing {info["Department_Abbreviation"]} {info["Course_Number"]} Section {info["Section_Number"]}\n'
                                f'Could not find locator "{locator}" of type "{type}"')
                else:
                    logger.warn(f'Could not find locator "{locator}" of type "{type}"\n'
                               f'More info can be provided by passing in info=course_info')
            return [False] if multiple else False
