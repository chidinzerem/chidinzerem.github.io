#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------
# Penji OpDev Fall 2019
# Template Email Scraper
# Author: Cory Paik
# Updated: 08.05.2019
# ------------------------


# General
import math
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


    def run(self):
        """ Main Function, loads up the professor data frame and applies function get_email """
        self.prof_df = self._load()
        df_split_len = math.ceil(len(self.prof_df.index)/10)
        for i in range(10):
            self.eval_range = (i*df_split_len, (i+1)*df_split_len)
            self.prof_df = self.prof_df.apply(self.get_email, axis=1)
            logger.info(f'{(i+1)*10}% Complete')
            if self.args.save:
                self._save()


    def get_email(self, row):
        """ Secondary Function, does all the actual search and processing on each row """

        # If already found email
        if '@' not in str(row['Email']) and self.eval_range[0] <= row.name <=self.eval_range[1]:
            self.driver.get(self.config.START_URL)
            fn_input = self.locate(type='id', locator='id_givenName')
            ln_input = self.locate(type='id', locator='id_sn')

            fn = row['Full Name'].split()[0]
            ln = row['Full Name'].split()[-1]
            logger.debug(f'{fn, ln}')
            fn_input.send_keys(fn)
            ln_input.send_keys(ln, Keys.RETURN)

            try:
                self.driver.get(self.locate(type='link_text', locator='View Profile', report=False, secs=1).get_attribute('href'))
                email = self.locate(type='p_link_text', locator='@tamu.edu', iText=True, report=False, secs=1)
                logger.debug(f'email:{email}')
                row['Email'] = email
            except AttributeError:
                logger.debug(f'No Email found for {row["Full Name"]}')
        return row
