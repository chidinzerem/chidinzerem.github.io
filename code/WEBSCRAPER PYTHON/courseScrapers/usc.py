#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------
# Penji OpDev Fall 2019
# USC Course Scraper
# Author: Cory Paik
# ------------------------

# General
import time
import parse
import tkinter
import numpy as np
# Web Scraping
import scrapy
import selenium
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
# Local
import core.utils as utils
from core.config import cfg


# Sample Template Structure
CourseInfo = {
    # For updating reference
    'Reference_Number'        : None,
    # In run()
    'Department_Abbreviation' : None,
    'Department_Name'         : None,
    # In process_subject()
    'Course_Number'           : None,
    'Course_Name'             : None,
    # In process_course()
    'Section_Type'            : None, #TODO
    'Section_Number'          : None, #N/A
    'Section_Days'            : None,
    'Section_Time'            : None,
    'Section_Professor'       : None,
    'Number_Students'         : None,
    'ClassRoom'               : None,
}

class Scraper:
    def __init__(self, driver_location):
        # Initialize web driver
        self.driver = webdriver.Chrome(driver_location)
        # Setup window to be full width and 3/4 height
        root = tkinter.Tk()
        self.driver.set_window_position(0, 0)
        self.driver.set_window_size(root.winfo_screenwidth(),
                                    root.winfo_screenheight()*0.75)
        # Read in Configuration File
        self.config = cfg.USC
        # Search Page to start
        self.driver.get(self.config.START_URL)
        self.locate = utils.Locator(main_driver=self.driver)

    def __del__(self):
        self.driver.quit()

    def _click(self, button):
        ActionChains(self.driver).move_to_element(button).click(button).perform()


    def run(self, args):
        # Sorter All Programs Button
        self.locate(type='xpath', locator="//ul[@id='sorter-classes']/li/a[@data-sort-by='data-code']").click()
        _all_programs = self.locate(type='xpath', locator="//ul[@id='sortable-classes']/li", multiple=True)
        # Setup CSV and np array
        explored_subjects = utils.load(term=args.term, school=args.school, col_name='Department_Abbreviation', test=args.test, reset=args.reset)
        all_codes = [element.get_attribute('data-code') for element in _all_programs]
        explored_adj = len(explored_subjects)
        for idx, code in enumerate(filter(lambda x: (x not in explored_subjects), all_codes)):
            self.locate(type='xpath', locator="//ul[@id='sorter-classes']/li/a[@data-sort-by='data-code']").click()
            subject = self.locate(type='xpath', locator=f"//ul[@id='sortable-classes']/li[@data-code='{code}']")
            self.subject_course_info = []
            course_info = CourseInfo.copy()
            course_info['Department_Name'] = subject.get_attribute('data-title')
            course_info['Department_Abbreviation'] = code
            print(f'Selected Subject {code} - {int(((idx+explored_adj)/len(all_codes))*100)}% complete')
            subject_link = self.locate(driver=subject, type='tag', locator='a').get_attribute('href')
            self.driver.get(subject_link)
            self.process_subject(course_info)
            # Save to csv
            if args.save:
                explored_subjects = np.append(explored_subjects, code)
                utils.save(dict_list=self.subject_course_info, ref_template=CourseInfo,
                          term=args.term, school=args.school, explored_subjects=explored_subjects, test=args.test)
            # Return to home page each iteration
            self.driver.back()
        return explored_subjects


    def process_subject(self, template_course_info):
        expand_all = self.locate(type='xpath', locator='//a[@class="expand"]').click()
        all_courses = self.locate(type='xpath', locator="//div[@class='course-table']"
                                                        "/div[@class='course-info expanded']"
                                                        "/div[@class='course-id']"
                                                        "/h3/a[@class='courselink']", multiple=True, text=True)
        for course in filter(lambda x: (x!=False), all_courses):
            course_info = template_course_info.copy()
            result = parse.parse('{abb} {num}: {name} ({units})', course)
            if result:
                course_info['Course_Number'] = result['num']
                course_info['Course_Name'] = result['name']
            self.process_course(course_info)


    def process_course(self, template_course_info):
        course_number = template_course_info['Course_Number'][:3]
        all_sections = self.locate(type='xpath', locator=f"//div[@class='course-table']"
                                                         f"/div[@class='course-info expanded']"
                                                         f"/div[@class='course-details' and contains(@id, '{course_number}')]"
                                                         f"/table[@class='sections responsive']"
                                                         f"/tbody/tr", multiple=True)
        for section in filter(lambda x: (x.get_attribute('class') != 'headers' and 'firstline' not in x.get_attribute('class')), all_sections):
            section_type = self.locate(driver=section, type='class', locator='type', text=True, info=template_course_info)
            if section_type in self.config.CLASS_TYPES:
                course_info = template_course_info.copy()
                course_info['Section_Type'] = section_type
                course_info['Section_Number'] = 'N/A'
                course_info['Reference_Number'] = self.locate(driver=section, type='class', locator='section', text=True)
                course_info['Section_Time'] = self.locate(driver=section, type='class', locator='time', text=True)
                course_info['Section_Days'] = self.locate(driver=section, type='class', locator='days', text=True)
                course_info['Number_Students'] = self.locate(driver=section, type='class', locator='registered', text=True).split()[0]
                course_info['Section_Professor'] = self.locate(driver=section, type='class', locator='instructor', text=True).replace('\n', ' ').replace('\t', ' ')
                course_info['ClassRoom'] = self.locate(driver=section, type='class', locator='location', text=True)
                self.subject_course_info.append(course_info)