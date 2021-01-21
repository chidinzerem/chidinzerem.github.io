#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------
# Penji OpDev Fall 2019
# Student Org  Scraper
# Author: Cory Paik
# Updated: 27.07.2019
# ------------------------

# General
import os
import csv
import tkinter
import numpy as np
import pandas as pd
# Web Scraping
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import WebDriverException
# Local
from core import logger
from core.config import cfg
import core.utils as utils


class SoScraper:
    def __init__(self, args):
        # Save Args and Configuration File
        self.args = args
        self.config = cfg[args.school.upper()].ORGS
        # Initialize web driver
        chrome_options = Options()
        if args.headless:
            chrome_options.add_argument('--headless')
        self.driver = webdriver.Chrome(executable_path=args.driver, options=chrome_options)
        # Setup window to be full width and 3/4 height
        root = tkinter.Tk()
        self.driver.set_window_position(0, 0)
        self.driver.set_window_size(root.winfo_screenwidth()*args.width,
                                    root.winfo_screenheight()*args.height)
        # Search Page to start
        self.driver.get(self.config.START_URL)
        self.locate = utils.Locator(main_driver=self.driver)
        # Get the term (<nice name>, <file name>, <abbr>)
        try:
            self.cterm = cfg.GENERAL[args.term.upper()]
            self.pterm = cfg.GENERAL[args.term.upper() + '_PREV']
        except KeyError:
            logger.error(f'{args.term} not a valid option for term')
            raise SystemExit
        # File Name
        self.csv_file_name = f'data/{args.school}/{self.cterm[1]}/gs_{args.school}_{self.cterm[1]}_Student_Orgs.csv'
        # sheet_idx = 7 if args.term == 'archive' else 2
        # self.file_name = f'data/test_runs/gs_{args.term}_{args.school}_{sheet_idx}.csv' if args.test \
        #     else f'data/{args.school}/{args.term}/gs_{args.term}_{args.school}_{sheet_idx}.csv'

    def __del__(self):
        self.driver.quit()

    def _click(self, button):
        try:
            button.click()
        except WebDriverException:
            logger.debug(f'Could not perform normal click on element\n'
                         f'       Attempting ActionChain click ')
            ActionChains(self.driver).move_to_element(button).click(button).perform()
        finally:
            pass

    def _save(self):
        """ Saves a csv of professor data"""
        self.df.to_csv(index=False, path_or_buf=self.csv_file_name)

    def _load(self):
        if self.args.reset:
            self._reset()
        try:
            df = pd.read_csv(self.csv_file_name)
            logger.info(f'Found Existing CSV File')
            df = df.fillna('')
            subset = df[['Name', 'URL', 'Email']]
            tuples = [tuple(x) for x in subset.values]
            print(tuples)
            #raise SystemExit
            return tuples
        except FileNotFoundError:
            logger.error('CSV File not found')
            return []
            # raise SystemExit

    def _reset(self):
        if os.path.exists(self.csv_file_name):
            os.remove(self.csv_file_name)
        logger.info(f'Reset of Student org files for {self.args.school}')


    def run(self):
        """ Main Function, loads up the professor data frame and applies function get_email
            Pseudocode:
            self.prof_df = self._load()
            self.prof_df = self.prof_df.apply(self.get_email, axis=1)
            if args.save:
                self._save()
        """
        raise NotImplementedError

    def df_get_email(self, row):
        """ Secondary Function, does all the actual search and processing on each row
            Pseudocode:
            # If already found email
            if '@' not in in str(row['Email']):
                ...
                search_name = row['Full Name']
                search_input.send_keys(search_name, Keys.RETURN)
                ...
                row['Email'] = email
            return row
        """
        raise NotImplementedError
