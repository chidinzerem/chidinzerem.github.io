#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------
# Penji OpDev Fall 2019
# Template Course Scraper
# Author: Cory Paik
# Updated: 27.07.2019
# ------------------------

# General
import os
import numpy as np
import parse
# Scraping
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
# Local
from core import logger
import core.utils as utils
from core.config import cfg
from core.cl_scraper import ClScraper

import time

class Scraper(ClScraper):
    def __init__(self, args):
        # Use the parent class
        ClScraper.__init__(self, args)
        self.subject_course_info = None


    def run(self):
        """ Main loop through all subjects """


        # Initial Parameter Setup
        Select(self.locate(type='id', locator='filter-campus')).select_by_value('WS')
        Select(self.locate(type='id', locator='filter-career')).select_by_value('UGRD')
        Select(self.locate(type='id', locator='filter-instruct-mode')).select_by_value('P')

        all_schools = self.locate(type='xpath', locator='//select[@id="search-acad-group"]'
                                                        '/option', multiple=True)
        all_codes = dict()
        for school in all_schools:
            school_value = school.get_attribute('value')
            school_name = school.text
            if school_value not in ('', ' ', 'dummy') and school_name.split()[-1] not in ('Grad', 'Cont Ed', 'Graduate') \
                and not any([school_word in ('Shanghai', 'Abu', 'Dhabi') for school_word in school_name.split()]):
                Select(self.locate(type='id', locator='search-acad-group')).select_by_value(school_value)
                all_subjects = self.locate(type='xpath', locator='//select[@id="subject"]/option', multiple=True)
                for subject in all_subjects:
                    subject_value = subject.get_attribute('value')
                    if subject_value not in ('', ' ', 'dummy'):
                        all_codes[(school_value, subject_value)] = subject.text

        explored_subjects = self._load(check_np_only=True)
        explored_adj = len(explored_subjects)
        if explored_subjects == []:
            explored_subjects = np.empty(len(all_codes.keys()), dtype='O')



        #logger.debug(list(all_codes.keys()))
        #mask = np.isin(explored_subjects, [['UT', 'FMTV-UT'],['UW', 'UPADM-GP']])
        #print(explored_subjects, mask, explored_subjects[mask])

        for idx, code in enumerate(filter(lambda x: (x[1] not in explored_subjects), list(all_codes.keys()))):
            self.subject_course_info = []
            Select(self.locate(type='id', locator='search-acad-group')).select_by_value(code[0])
            Select(self.locate(type='id', locator='subject')).select_by_value(code[1])

            course_info = cfg.GENERAL.CL_COLUMNS.copy()
            course_info['Department_Name'] = all_codes[code]
            course_info['Department_Abbreviation'] = code[1]
            self._click(self.locate(type='id', locator='buttonSearch'))
            logger.info(f'Selected Subject {course_info["Department_Abbreviation"]} - '
                        f'{int(((idx + explored_adj) / len(all_codes.keys())) * 100)}% complete')
            self.process_subject(course_info) # Process Subject
            # Save to csv
            if self.args.save:
                code = code
                explored_subjects = np.append(explored_subjects, code, axis=0)
                self._save(dict_list=self.subject_course_info, explored_subjects=explored_subjects)
        print(explored_subjects[0])
        return explored_subjects

    def process_subject(self, template_course_info, *args, **kwargs):
        """ Secondary loop through all courses in subject """
        all_sections = self.locate(type='xpath', locator='//div[@id="search-results"]/a', multiple=True)
        base_window = self.driver.current_window_handle
        #logger.debug(f'base window handle: {base_window}')
        windows_arr = []
        course_info_arr = []
        #all_course_links = [course.get_attribute('href') for course in all_courses]
        for section in all_sections:
            section_info = self.locate(driver=section, type='xpath', locator='.//div[not(contains(@style, "display: none"))]'
                                                                             '/div[@class="strong section-body"]', iText=True, secs=0, report=False)
            if section_info:
                p_section_info = parse.parse('Section: {s_num}-{s_type} ({ref_num})', section_info)
                if p_section_info['s_type'] in self.config.CLASS_TYPES:
                    # logger.debug(f'Processing Section {p_section_info["ref_num"]}')
                    course_info = template_course_info.copy()
                    course_info['Section_Type'] = p_section_info['s_type']
                    course_info['Reference_Number'] = p_section_info['ref_num']
                    self.driver.execute_script(f'''window.open("{section.get_attribute('href')}", "_blank");''')
                    windows_after = self.driver.window_handles
                    new_window = [x for x in windows_after if x != base_window and x not in windows_arr][0]
                    # logger.debug(f'old handle arr: {windows_arr}')
                    windows_arr.append(new_window)
                    course_info_arr.append(course_info)
                    # logger.debug(f'new window handle: {new_window}')

        for window, course_info in zip(windows_arr, course_info_arr):
            self.driver.switch_to_window(window)
            self.process_details(course_info)
            self.driver.close()

        self.driver.switch_to_window(base_window)




    def process_course(self, template_course_info, *args, **kwargs):
        """ Third loop through all sections in course """
        pass


    def process_details(self, course_info):
        course_info['Course_Name'] = self.locate(type='xpath', locator='//div[@itemprop="name"]', iText=True)
        course_info['Course_Number'] = self.locate(type='xpath', locator='//h1[@class="page-title  with-back-btn"]', iText=True).split()[1]
        detail_rows = self.locate(type='xpath', locator='//section[@itemtype="http://schema.org/Class"]'
                                                        '/div[@class="section-content clearfix"]', multiple=True)
        detail_rows.append(self.locate(type='xpath', locator='//section[@itemtype="http://schema.org/Class"]'
                                                             '/a/div[@class="section-content clearfix"]'))
        for detail_row in detail_rows:
            row_h = self.locate(driver=detail_row, type='class', locator='pull-left', iText=True)
            if row_h == 'Instructor(s)':
                course_info['Section_Professor'] = self.locate(driver=detail_row, type='class', locator='pull-right', iText=True)
            elif row_h == 'Meets':
                days_time = self.locate(driver=detail_row, type='class', locator='pull-right', iText=True).split()
                course_info['Section_Days'] = days_time[0]
                course_info['Section_Time'] = ' '.join(days_time[1:])
            elif row_h == 'Room':
                course_info['ClassRoom'] = self.locate(driver=detail_row, type='xpath', locator='.//div[@class="pull-right"]/div', text=True)
            else:
                pass

        self.subject_course_info.append(course_info)
        #logger.debug(course_info)