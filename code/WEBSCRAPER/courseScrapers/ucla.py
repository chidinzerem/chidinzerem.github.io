#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------
# Penji OpDev Fall 2019
# UCLA Course Scraper
# Author: Cory Paik
# ------------------------

# General
import time
import parse
import numpy as np
# Web Scraping
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
# Local
from core import logger
from core.config import cfg
from core.cl_scraper import ClScraper


class Scraper(ClScraper):
    def __init__(self, args):
        # Use the parent class
        ClScraper.__init__(self, args)
        self.subject_course_info = None


    def run(self):
        # Sorter All Programs Button)
        select = self.locate(type='xpath', locator="//input[@id='select_filter_subject']")
        self._click(select)
        _all_subjects = self.locate(type='xpath', locator="//ul[@id='ui-id-1']/li/a", multiple=True)
        # Setup CSV and np array
        explored_subjects = self._load()

        def subject_parser(element):
            parsed = parse.parse('{name} ({abbr})', element.text)
            return (parsed['name'], parsed['abbr']) if parsed else (element.text, element.text)
        all_codes = {subject_parser(subject)[1] : subject.text for subject in _all_subjects}
        #assert len(_all_subjects) == len(all_codes)
        explored_adj = len(explored_subjects)
        for idx, code in enumerate(filter(lambda x: (x not in explored_subjects), list(all_codes.keys()))):

            subject = self.locate(type='xpath', locator=f"//ul[@id='ui-id-1']/li/a[contains(.,'{code}')]")
            self.subject_course_info = []
            course_info = cfg.GENERAL.CL_COLUMNS.copy()
            subject_text = subject.text
            course_info['Department_Name'], course_info['Department_Abbreviation'] = subject_parser(subject)
            logger.info(f'Selected Subject {course_info["Department_Abbreviation"]} - '
                        f'{int(((idx + explored_adj) / len(list(all_codes.keys()))) * 100)}% complete')
            select.send_keys(subject_text)
            time.sleep(1)
            select.send_keys(Keys.RETURN)
            while True:
                button = self.locate(type='id', locator='btn_go')
                if not button.get_attribute('style'):
                    break
            self._click(button)

            self.process_subject(course_info)
            # Save to csv
            if self.args.save:
                explored_subjects = np.append(explored_subjects, code)
                self._save(dict_list=self.subject_course_info, explored_subjects=explored_subjects)
            # Return to home page each iteration
            self.driver.get(self.config.START_URL)
            select = self.locate(type='xpath', locator="//input[@id='select_filter_subject']")
            self._click(select)
        return explored_subjects

    def _move_to(self, element=None, x_off=0, y_off=0, secs=0):
        # ActionChains(self.driver).move_to_element_with_offset(element, x_off, y_off).pause(secs).perform()
        self.driver.execute_script(f"window.scrollTo({x_off}, {y_off});")
        time.sleep(secs)


    def process_subject(self, template_course_info, *args, **kwargs):

        self._click(self.locate(type='id', locator="btn_filters"))
        if self.locate(type='id', locator="Level_options"):
            # Lower Division
            self._move_to(y_off=1000, secs=1)
            try:
                Select(self.locate(type='id', locator="Level_options")).select_by_visible_text("Lower Division")
                self.process_division(template_course_info)
            except NoSuchElementException:
                logger.warn(f'{template_course_info["Department_Abbreviation"]} has no Lower Division Courses')
            # Upper Division
            self._move_to(y_off=1000, secs=1)
            try:
                Select(self.locate(type='id', locator="Level_options")).select_by_visible_text("Upper Division")
                self.process_division(template_course_info)
            except NoSuchElementException:
                logger.warn(f'{template_course_info["Department_Abbreviation"]} has no Upper Division Courses')
        else:
            division_text = self.locate(type='id', locator='Level_filterContainer', text=True)
            logger.debug(f'{template_course_info["Department_Abbreviation"]} has only {division_text} Courses')
            if division_text in ("Lower Division", "Upper Division"):
                self.process_division(template_course_info)


    def process_division(self, template_course_info, *args, **kwargs):
        page_count_div = self.locate(type='id', locator='pageCount')
        page_count = int(page_count_div.get_attribute('value')) if page_count_div else 0
        for i in range(page_count):
            logger.debug(f'Processing page {i+1} of {page_count}')
            self.process_page(template_course_info)
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            next_pg = self.locate(type='xpath',
                                  locator="(.//*[normalize-space(text()) and normalize-space(.)='First'])[2]/following::span[3]", secs=1, info=template_course_info)
            if next_pg:
                self._click(next_pg)
            else:
                break

    def process_page(self, template_course_info, *args, **kwargs):
        expand_all = self.locate(type='xpath', locator='//a[@id="expandAll"]')
        self._move_to(y_off=1000,secs=1)
        self._click(expand_all, ac=True)
        all_courses = self.locate(type='xpath', locator="//div[@class='row-fluid class-title']", multiple=True)
        for course in filter(lambda x: (x!=False), all_courses):
            course_info = template_course_info.copy()
            num_name = self.locate(driver=course, type='xpath', locator='//h3/a[contains(@id, "title")]', text=True)
            result = parse.parse('{num} - {name}', num_name)
            course_info['Course_Number'] = result['num']
            course_info['Course_Name'] = result['name']
            course_ref = course.get_attribute('id')
            self.process_course(course_info, course=course)

    def process_course(self, template_course_info, *args, **kwargs):

        all_sections = self.locate(driver=kwargs['course'], type='xpath', locator='//div[contains(@id, "children")]/div[contains(@class, "data_row")]', multiple=True, info=template_course_info)
        for section in filter(lambda x: (x != False), all_sections):
            stype_snum = self.locate(driver=section, type='class', locator='sectionColumn', text=True).split()
            if stype_snum[0] in self.config.CLASS_TYPES:
                course_info = template_course_info.copy()
                course_info['Reference_Number'] = section.get_attribute('id')
                course_info['Section_Type'], course_info['Section_Number'] = stype_snum
                # Enrollment
                enrollment_str = self.locate(driver=section, type='class', locator='statusColumn', text=True).split('\n')
                if len(enrollment_str)==1:
                    pass
                elif enrollment_str[0] in ('Open'):
                    course_info['Number_Students'] = parse.parse('{in} of {cap} Enrolled', enrollment_str[1])['in']
                elif enrollment_str[0] in ('Waitlist', 'Closed'):
                    try:
                        course_info['Number_Students'] = parse.parse('Class Full ({cap})', enrollment_str[1])['cap']
                    except:
                        logger.debug(f'enr_str: {enrollment_str}')
                        course_info['Number_Students'] = parse.parse('Class Full ({cap}), Over Enrolled By {ov}', enrollment_str[1])['cap']
                elif ' '.join(enrollment_str[0].split()[:3]) == 'Closed by Dept' or enrollment_str[0]=='Cancelled':
                    break
                else:
                    logger.warn(f'Cannot parse number of students for course {course_info["Reference_Number"]} from string: {enrollment_str}')

                course_info['Section_Days'] = self.locate(driver=section, type='xpath', locator='.//div[contains(@class, "dayColumn")]', text=True)
                course_info['Section_Time'] = self.locate(driver=section, type='class', locator='timeColumn', text=True)
                course_info['ClassRoom'] = self.locate(driver=section, type='xpath', locator='.//div[contains(@class, "locationColumn")]', text=True)
                course_info['Section_Professor'] = self.locate(driver=section, type='xpath', locator='.//div[contains(@class, "instructorColumn")]',text=True)
                #pprint(course_info)
                self.subject_course_info.append(course_info)

