#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------
# Penji OpDev Fall 2019
# NYU Email Scraper
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
        """ Secondary Function, does all the actual search and processing on each row """2
        # If already found email
        if '@' not in str(row['Email']) and self.eval_range[0] <= row.name <=self.eval_range[1]:
            self.driver.get(self.config.START_URL)
            n_input = self.locate(type='id', locator='search-form-field')
            name = row['Full Name']
            n_input.send_keys(name, Keys.RETURN)

            all_results = self.locate(type='xpath', locator='//div[@class="result-item people"]', multiple=True, secs=1,
                                      report=False)
            email = None
            if not any(all_results):
                try:
                    self._click(self.locate(type='p_link_text', locator='Web'))
                except AttributeError:
                    logger.error(f'Could not search professor in row {row.name}')
                    return row
                logger.debug(f'No People results for {name}, attempting Web')
                all_results = self.locate(type='xpath', locator='//div[@class="result-item"]', multiple=True, secs=1)
                for result in all_results:
                    header = self.locate(driver=result, type='xpath', locator=f'.//h2[contains(text(),"{name}")]',
                                         text=True, secs=1, report=False)
                    if header:
                        self.driver.get(
                            self.locate(driver=all_results[0], type='tag', locator='a').get_attribute('href'))
                        email = self.locate(type='p_link_text', locator='@nyu.edu', iText=True, report=False, secs=1)
                        logger.debug(name, email)
                        break
            else:
                for result in all_results:
                    header = self.locate(driver=result, type='xpath', locator=f'.//h2[contains(text(),"{name}")]',
                                         text=True, secs=1, report=False)
                    if header:
                        email = self.locate(type='p_link_text', locator='@nyu.edu', iText=True, report=False, secs=1)
                        logger.debug(name, email)
                        break
            row['Email'] = email
        return row
