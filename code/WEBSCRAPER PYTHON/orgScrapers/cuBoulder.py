#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------
# Penji OpDev Fall 2019
# CU Boulder Student Orgs Scraper
# Author: Cory Paik
# Updated: 08.27.19
# ------------------------

# General
import parse
import numpy as np
import pandas as pd
# Local
from core import logger
from core.config import cfg
from core.so_scraper import SoScraper

import time

class Scraper(SoScraper):
    def __init__(self, args):
        SoScraper.__init__(self, args)


    def run(self):
        num_orgs = self.locate(type='class', locator='osw-portals-summary-message', text=True)
        p_num_orgs = parse.parse('Showing all {num} portals.', num_orgs)['num']

        SCROLL_PAUSE_TIME = 0.01

        # Get scroll height
        bottom_height = self.driver.execute_script("return document.body.scrollHeight")

        all_org_infos = []
        for i in range(0,bottom_height, 200):
            # Scroll down
            self.driver.execute_script(f"window.scrollTo(0, {i});")
            time.sleep(SCROLL_PAUSE_TIME)
            orgs = self.locate(type='xpath', locator='//div[@class="osw-portals-list-item"]/a', multiple=True)
            # Tuple of data: ('Name', 'URL', 'Email')
            org_infos = [(self.locate(driver=org, type='class', locator='osw-portals-list-item-name', text=True),
                          org.get_attribute('href'), '') for org in orgs]
            [all_org_infos.append(org_info) for org_info in org_infos if org_info not in all_org_infos]

        # Assert we found all the organizations
        assert int(p_num_orgs) == len(all_org_infos)
        logger.info(f'Found links for {len(all_org_infos)} organizations')
        # Create data dict for pd.df
        gs_data = {
            'Name' : [info[0] for info in all_org_infos],
            'URL'  : [info[1] for info in all_org_infos],
            'Email': [info[2] for info in all_org_infos]
        }
        self.df = pd.DataFrame(data=gs_data, columns=('Name', 'URL', 'Email'))
        self.df = self.df.apply(self.df_get_email, axis=1)

        print(self.df.head(10))

        if self.args.save:
            self._save()

    def df_get_email(self, row):
        if '@' not in row['email']:
            self.driver.get(row['url'])
            self._click(self.locate(type='link_text', locator='Profile'))
            email = self.locate(type='p_link_text', locator='@colorado.edu', text=True, report=False, secs=1)
            row['email'] = email if email else None
        return row
