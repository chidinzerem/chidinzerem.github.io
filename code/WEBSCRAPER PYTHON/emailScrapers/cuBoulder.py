#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------
# Penji OpDev Fall 2019
# CU Boulder Email Scraper
# Author: Cory Paik
# Updated:
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
        self.prof_df = self.prof_df.apply(self.get_email, axis=1)
        if self.args.save:
            self._save()


    def get_email(self, row):
        if '@' not in str(row['Email']):
            search_input = self.locate(type='xpath', locator="(.//*[normalize-space(text()) and normalize-space(.)="
                                                             "'Enter the terms you wish to search for.'])[3]"
                                                             "/following::input[1]")
            search_input.click()
            search_input.clear()
            search_name = row['Full Name']
            search_input.send_keys(search_name, Keys.RETURN)

            # Try to find from side CU directory
            row['Email'] = self.process_search(search_name=search_name)
            # Clear courses to return to previous page
            self.driver.get(self.config.START_URL)
        return row


    def process_search(self, search_name):
        # Try From CU Dir
        email = self.locate(type='xpath', locator="//ul[@class='cu-directory-results']/li"
                                                  "/div[@class='people-meta']"
                                                  "/div[@class='people-data']"
                                                  "/a[@class='email-long']", iText=True, report=False)

        if not email:
            results = self.locate(type='xpath', locator="//div[@class='gsc-results gsc-webResult']/div", multiple=True)
            # Workaround for spelling suggestion
            first_info = self.locate(driver=results[0], type='xpath', locator=".//div/div[@class='gs-title']/a")
            if not first_info and len(results)>1:
                first_info = self.locate(driver=results[1], type='xpath', locator=".//div/div[@class='gs-title']/a")
            if first_info:
                self.driver.get(first_info.get_attribute('href'))
                email = self.locate(type='xpath', locator="//div[@class='person-email person-contact-info-item']",
                                    text=True)
                if not email:
                    email = None
                    logger.warn(f'Error in {search_name}')
        return email
