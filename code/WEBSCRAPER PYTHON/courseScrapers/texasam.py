#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------
# Penji OpDev Fall 2019
# Texas A&M Course Scraper
# Author: Cory Paik
# Updated: 8.12.2019
# ------------------------

# General
import parse
import numpy as np
# Scraping
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
# Local
from core import logger
import core.utils as utils
from core.config import cfg
from core.cl_scraper import ClScraper


class Scraper(ClScraper):
    def __init__(self, args):
        # Use the parent class
        ClScraper.__init__(self, args)
        self.subject_course_info = None


    def run(self):
        """ Main loop through all subjects """
        explored_subjects = self._load()
        explored_adj = len(explored_subjects)
        # Select term
        Select(self.locate(type='name', locator='p_term')).select_by_visible_text('Fall 2019 - College Station')
        self._click(self.locate(type='xpath', locator="(.//*[normalize-space(text()) and normalize-space(.)='Term'])[1]"
                                                      "/following::input[1]"))
        all_subjects = self.locate(type='xpath', locator='//select[@name="sel_subj"]/option', multiple=True)

        def subject_parser(element):
            parsed = parse.parse('{abbr}-{name}', element.text)
            return (parsed['name'], parsed['abbr']) if parsed else (element.text, element.text)
        all_codes = {subject.get_attribute("value"): subject_parser(subject) for subject in all_subjects}
        explored_adj = len(explored_subjects)
        for idx, code in enumerate(filter(lambda x: (x not in explored_subjects), list(all_codes.keys()))):
            # Restart Each Iteration
            self.subject_course_info = []
            self.driver.get(self.config.START_URL)
            # Select Term / Campus
            Select(self.locate(type='name', locator='p_term')).select_by_visible_text('Fall 2019 - College Station')
            self._click(
                self.locate(type='xpath', locator="(.//*[normalize-space(text()) and normalize-space(.)='Term'])[1]"
                                                  "/following::input[1]"))
            #self.locate(type='name', locator='p_term').send_keys(Keys.RETURN)
            # Select subject code
            self._click(self.locate(type='xpath', locator=f'//select[@name="sel_subj"]/option[@value="{code}"]'))
            # Select Undergrad Level
            self._click(self.locate(type='xpath', locator=f'//select[@name="sel_levl"]/option[@value="UG"]'))
            # Fill Course Info
            course_info = cfg.GENERAL.CL_COLUMNS.copy()  # TODO: New version
            course_info['Department_Abbreviation'] = code
            course_info['Department_Name'] = all_codes[code][0]
            logger.info(f'Selected Subject {course_info["Department_Abbreviation"]} - '
                        f'{int(((idx + explored_adj) / len(all_subjects)) * 100)}% complete')
            # Search
            self.locate(type='xpath', locator=f'//select[@name="sel_levl"]').send_keys(Keys.RETURN)
            self.process_subject(course_info)  # Process Subject
            # Save to csv
            if self.args.save:
                explored_subjects = np.append(explored_subjects, code)
                self._save(dict_list=self.subject_course_info, explored_subjects=explored_subjects)
        return explored_subjects

    def process_subject(self, template_course_info, *args, **kwargs):
        """ Secondary loop through all courses in subject """
        all_courses = self.locate(type='xpath', locator='//table[@summary="This layout table is used to present the sections found"]'
                                                         '/tbody/tr', multiple=True)
        for course in all_courses:
            header = self.locate(driver=course, type='xpath', locator='.//th[@scope="colgroup"]', iText=True, secs=1, report=False)
            body = self.locate(driver=course, type='xpath', locator='.//td/table', secs=1, report=False)
            if header:
                p_header = parse.parse('{name} - {ref:d} - {abbr} {num} - {sec_num}', header)
                p_header_2 = parse.parse('{name} - {ref:d} - {abbr} {num} - {sec_num:d} (Syllabus)', header)
                #print(p_header.type)
                if isinstance(p_header, parse.Result):
                    course_info = template_course_info.copy()
                    course_info['Course_Name'] = p_header['name']
                    course_info['Reference_Number'] = p_header['ref']
                    course_info['Course_Number'] = p_header['num']
                    course_info['Section_Number'] = p_header['sec_num']
                elif isinstance(p_header_2, parse.Result):
                    course_info = template_course_info.copy()
                    course_info['Course_Name'] = p_header_2['name']
                    course_info['Reference_Number'] = p_header_2['ref']
                    course_info['Course_Number'] = p_header_2['num']
                    course_info['Section_Number'] = p_header_2['sec_num']
                else:
                    logger.warn(f'Cannot Parse Header: {header}')
            elif body:
                self.process_course(course_info, course_table=body)
            else:
                logger.warn(f'Unknown Element: {course.get_attribute("innerText")}')


    def process_course(self, template_course_info, *args, **kwargs):
        """ Third loop through all sections in course """
        try :
            if int(template_course_info['Course_Number']) >= 500:
                return
        except:
            logger.warn(f'Skipping {template_course_info["Course_Number"]}, could not level')
        all_sections = self.locate(driver=kwargs['course_table'], type='xpath', locator='.//tbody/tr', multiple=True)[1:]
        for section in all_sections:
            section_info_items = self.locate(driver=section, type='tag', locator='td', multiple=True, iText=True)
            if section_info_items[0] in self.config.CLASS_TYPES:
                course_info = template_course_info.copy()
                course_info['Section_Type'] = section_info_items[0]
                course_info['Section_Time'] = section_info_items[1]
                course_info['Section_Days'] = section_info_items[2]
                course_info['ClassRoom'] = section_info_items[3]
                # Parse out prof name
                prof_all = section_info_items[6].split(', ')
                for prof in prof_all:
                    prof_name = parse.parse('{name} (P)', prof)
                    if isinstance(prof_name, parse.Result):
                        course_info['Section_Professor'] = prof_name['name']
                        break
                if course_info['Section_Professor'] is None and section_info_items[6] != 'TBA':
                    logger.warn(f'Could not Parse Professor (P): {section_info_items[6]}')
                    course_info['Section_Professor'] = section_info_items[6]
                self.subject_course_info.append(course_info)
            elif section_info_items[0] in self.config.IGNORE_CLASS_TYPES:
                pass
            else:
                logger.warn(f'Skipping unknown course type: {section_info_items[0]}')
