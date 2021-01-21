#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------
# Penji OpDev Fall 2019
# USC Email Scraper
# Author: Cory Paik
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
        # Setup CSV First
        self.prof_df = self._load()
        self.prof_df= self.prof_df.apply(self.get_email, axis=1)
        if self.args.save:
            self._save()


    def get_email(self, row):
        # If already found email
        if '@' not in str(row['Email']):
            search_input = self.locate(type='id', locator="basic")
            self._click(search_input)
            search_input.clear()
            search_name = row['Full Name']
            search_input.send_keys(search_name, Keys.RETURN)
            if self.locate(type='xpath', locator="//p[@class='error']", report=False, secs=0):
                logger.info(f'No results for {search_name}')
            else:
                # Only works if only 1 result
                email = self.locate(type='xpath', locator="//td[@class='email']", text=True, report=False, secs=5)
                if not email:
                    # More than one
                    results = self.locate(type='xpath', locator="//tr[@class='result']", multiple=True)
                    for result in results:
                        name = self.locate(driver=result, type='xpath', locator=".//td[@class='name']/a[@class='person']", text=True).split(', ')
                        if name == [row['Last Name'], row['First Name']]:
                            email = self.locate(driver=result, type='xpath', locator=".//td[@class='contact']/div[@class='email']", text=True)
                            logger.debug(f'{len(results)} links for {search_name}, found direct match {name} with email {email}')
                            break
                    if results and not email:
                        logger.warn(f'{len(results)} links for {search_name}, no direct match')
                row['Email'] = email if email else None
        return row