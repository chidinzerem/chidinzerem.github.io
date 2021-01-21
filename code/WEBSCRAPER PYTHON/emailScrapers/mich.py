#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------
# Penji OpDev Fall 2019
# Template Email Scraper
# Author: Cory Paik
# Updated: 08.05.2019
# ------------------------


# General
import parse
import numpy as np
import pandas as pd
# Web Scraping
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
# Local
from core import logger
from core.config import cfg
from core.em_scraper import EmScraper

import time

class Scraper(EmScraper):
    def __init__(self, args):
        EmScraper.__init__(self, args)
        self.prof_df = None


    def run1(self):
        """ Main Function, loads up the professor data frame and applies function get_email """
        self.prof_df = self._load()
        df_split_len = math.ceil(len(self.prof_df.index)/10)
        for i in range(10):
            self.eval_range = (i*df_split_len, (i+1)*df_split_len)
            self.prof_df = self.prof_df.apply(self.get_email, axis=1)
            logger.info(f'{(i+1)*10}% Complete')
            if self.args.save:
                self._save()

    def run(self):
        self.driver.get(self.config.START_URL)
        Select(self.locate(type='id', locator='givenNameSearchType')).select_by_visible_text('matches exactly')
        Select(self.locate(type='id', locator='snSearchType')).select_by_visible_text('matches exactly')

        fn_input = self.locate(type='id', locator='givenName')
        ln_input = self.locate(type='id', locator='sn')
        fn, ln = ('Howard', 'Stein')

        logger.debug(f'{fn, ln}')
        fn_input.send_keys(fn)
        ln_input.send_keys(ln, Keys.RETURN)

        self._click(self.locate(type='link_text', locator='Howard Stein'))
        email = self.locate(type='class', locator='email', iText=True)
        print(email)

        #done = input('Press Enter When Complete ')


    def get_email(self, row):
        """ Secondary Function, does all the actual search and processing on each row """

        # If already found email
        if '@' not in str(row['Email']):
            self.driver.get(self.config.START_URL)
            Select(self.locate(type='id', locator='givenNameSearchType')).select_by_visible_text('matches exactly')
            Select(self.locate(type='id', locator='snSearchType')).select_by_visible_text('matches exactly')

            fn_input = self.locate(type='id', locator='givenName')
            ln_input = self.locate(type='id', locator='sn')

            fn = row['Full Name'].split()[0]
            ln = row['Full Name'].split()[-1]

            logger.debug(f'{fn, ln}')
            fn_input.send_keys(fn)
            ln_input.send_keys(ln, Keys.RETURN)

            self._click(self.locate(type='link_text', locator='Howard Stein'))
            email = self.locate(type='class', locator='email', iText=True)
            row['Email'] = email
        return row
