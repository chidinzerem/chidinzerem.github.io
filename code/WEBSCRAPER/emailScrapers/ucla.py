#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------
# Penji OpDev Fall 2019
# UCLA Email Scraper
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


class Scraper(EmScraper):
    def __init__(self, args):
        EmScraper.__init__(self, args)
        self.prof_df = None


    def run(self):
        """ Main Function, loads up the professor data frame and applies function get_email """
        self.prof_df = self._load()
        df_split_len = math.ceil(len(self.prof_df.index) / 10)
        for i in range(10):
            self.eval_range = (i * df_split_len, (i + 1) * df_split_len)
            self.prof_df = self.prof_df.apply(self.get_email, axis=1)
            logger.info(f'{(i + 1) * 10}% Complete')
            if self.args.save:
                self._save()


    def get_email(self, row):
        """ Secondary Function, does all the actual search and processing on each row """
        # If already found email
        if '@' not in str(row['Email']) and self.eval_range[0] <= row.name <= self.eval_range[1]:
            self._click(self.locate(type='link_text', locator="advanced search"))
            search_input = self.locate(type='id', locator="search-term")
            self._click(search_input)
            search_input.clear()
            name_in = row['Full Name'].split()
            search_name = name_in[-1] + ', ' + name_in[0]
            search_input.send_keys(search_name, Keys.RETURN)
            # Only works on single page
            results = self.locate(type='xpath', locator='//section[@class="search-results"]/p', multiple=True)
            for result in filter(lambda x: (x != False), results):
                inner_text = result.get_attribute('innerText')
                if 'Email' in inner_text:
                    email = inner_text.split('\n')[1]
                    logger.debug(f'Found email div: {email}')
                    row['Email'] = email
        return row

