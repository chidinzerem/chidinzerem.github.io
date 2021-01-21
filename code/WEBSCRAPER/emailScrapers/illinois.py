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
        names = ('A* Chatterton', 'P* Silhan', 'C* Billing', 'M* Fisher')
        self.driver.get(self.config.START_URL)
        capcha_done = input('Press Enter When Capcha Complete ')
        time.sleep(1)
        for name in names:
            # self.driver.get(self.config.START_URL)
            # capcha_done = input('Press Enter When Capcha Complete ')
            # time.sleep(1)

            name_input = self.locate(type='id', locator='search-text')

            name_input.clear()
            ...
            name_input.send_keys(name, Keys.RETURN)
            ...
            #print(email)
            time.sleep(1)

    def get_email(self, row):
        """ Secondary Function, does all the actual search and processing on each row """

        # If already found email
        if '@' not in str(row['Email']):
            self.driver.get(self.config.START_URL)
            fn_input = self.locate(type='id', locator='givenName')
            ln_input = self.locate(type='id', locator='sn')

            fn, ln = ('A', 'Chatterton')
            ...
            logger.debug(f'{fn, ln}')
            fn_input.send_keys(fn)
            ln_input.send_keys(ln, Keys.RETURN)
            ...
            row['Email'] = email
        return row
        raise NotImplementedError
