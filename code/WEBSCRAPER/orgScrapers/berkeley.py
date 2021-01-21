#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------
# Penji OpDev Fall 2019
# Template Student Org Scraper
# Author: Cory Paik
# Updated: < MM.DD.YEAR >
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
import itertools

class Scraper(SoScraper):
    def __init__(self, args):
        SoScraper.__init__(self, args)


    def run(self):
        """ Main Loop: Find Names and Links of Organizations through scrolling """
        # TODO: Find Number of orgs if possible to assert against (or manually enter)
        num_orgs = 1338 # self.locate()
        #num_orgs = parse.parse('Showing all {num} portals.', num_orgs)['num']
        # Get bottom height for loop
        all_org_infos = self._load()
        #all_org_links = [ info[1] for info in all_org_infos]
        scroll_pause_time = 0.01
        start_height = 0
        # Load More loop
        while True:

            bottom_height = self.driver.execute_script("return document.body.scrollHeight")

            # Scrolling Loop
            for i in range(start_height, bottom_height, 100):
                # Scroll down
                self.driver.execute_script(f"window.scrollTo(0, {i});")
                time.sleep(scroll_pause_time)

                # TODO: locate org links, setup tuple; ('Name', 'URL', 'Email')
                orgs = self.locate(type='xpath', locator='//div[@id="org-search-results"]'
                                                         '/div/div/div/a', multiple=True)
                org_infos = [('',org.get_attribute('href'), '') for org in orgs]

                # Append if not previously found
                [all_org_infos.append(org_info) for org_info in org_infos if org_info[1] not in itertools.chain(*all_org_infos)]
                #for org_info in org_infos:


            try:
                load_more = self.locate(type='tag', locator='button', multiple=True)[0]
                self._click(load_more)
                start_height = bottom_height
            except AttributeError:
                break

            logger.info(f'{int((len(all_org_infos)/1338)*100)}% complete')

        # Assert we found all the organizations, won't
        # assert int(num_orgs) == len(all_org_infos), f'Only found {len(all_org_infos)} / {num_orgs}'
        logger.info(f'Found links for {len(all_org_infos)}  out of {num_orgs} organizations')
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
        """ df apply function to find emails """
        if '@' not in row['Email']:
            self.driver.get(row['URL'])
            name = self.locate(type='tag', locator='h1', text=True)
            info_arr = self.locate(type='xpath', locator='//div[@role="main"]/div/div/div/div/div/div/div/div/div',
                                   text=True, multiple=True)
            email = None
            for info in filter(lambda x : (x), info_arr):
                sp_info = info.split('\n')
                if sp_info[0] == 'Contact Email':
                    email = sp_info[1].rsplit(' ', 1)[-1]
                    break
            #print(name)
            row['Name'] = name
            row['Email'] = email if email else None
        return row
