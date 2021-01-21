#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------
# Penji OpDev Fall 2019
# CalPoly Course Scraper
# Author: Cory Paik
# Updated: 27.07.2019
# ------------------------

# General
import parse
import numpy as np
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
        # Popup Window workaround
        popup_button = self.locate(type='xpath', locator="//button[@id='dismissNew']")
        if popup_button:
            popup_button.click()
        # Sorter All Programs Button
        all_subjects = self.locate(type='xpath', locator="//select[@class='filter-section border-all' and contains(@data-filter, 'dept')]/option", multiple=True)
        # Setup CSV and np array
        explored_subjects = self._load()
        def subject_parser(element):
            parsed = parse.parse('{abbr}-{name}', element.text)
            return (parsed['name'], parsed['abbr']) if parsed else (element.text, element.text)
        all_codes = {subject_parser(subject)[1] : subject.get_attribute("value") for subject in all_subjects}
        explored_adj = len(explored_subjects)
        for idx, code in enumerate(filter(lambda x: (x not in explored_subjects), list(all_codes.keys()))):

            subject = self.locate(type='xpath', locator=f"//select[@class='filter-section border-all']/option[contains(.,'{code}')]")
            self.subject_course_info = []
            course_info = cfg.GENERAL.CL_COLUMNS.copy()
            course_info['Department_Name'], course_info['Department_Abbreviation'] = subject_parser(subject)
            logger.info(f'Selected Subject {course_info["Department_Abbreviation"]} - {int(((idx + explored_adj) / len(list(all_codes.keys()))) * 100)}% complete')
            subject.click()
            self.process_subject(course_info)
            # Save to csv
            if self.args.save:
                explored_subjects = np.append(explored_subjects, code)
                self._save(dict_list=self.subject_course_info, explored_subjects=explored_subjects)
            # Clear courses to return to previous page
            select = self.locate(type='xpath', locator="//li[@id='cart-list-divider']/a[@id='removeAllCourses']")
            self._click(select)
        return explored_subjects


    def process_subject(self, template_course_info, *args, **kwargs):
        all_courses_buttons = self.locate(type='xpath', locator="//div[@class='course-list clearfix']/table/tbody/tr"
                                                        "/td[@class='selectCol']/button", multiple=True)
        [self._click(button) for button in all_courses_buttons]
        # Expand Selected Courses
        self.locate(type='xpath', locator="//a[@id='nextBtn']").click()

        all_courses = self.locate(type='xpath', locator="//div[@class='content']"
                                                        "/div[@class='select-course']", multiple=True)


        for course in filter(lambda x: (x!=False), all_courses):
            course_info = template_course_info.copy()
            num_name = self.locate(driver=course, type='xpath', locator='.//h3', text=True).split('\n')[0]
            result = parse.parse('{abbr} {num:d} - {name} — Units: {units}', num_name)
            course_info['Course_Number'] = result['num']
            course_info['Course_Name'] = result['name']
            self.process_course(course_info, course=course)


    def process_course(self, template_course_info, *args, **kwargs):
        all_sections = self.locate(driver=kwargs['course'], type='xpath', locator='.//table/tbody/tr',
                                   multiple=True, info=template_course_info)
        def section_not_found(split_section):
            logger.warn(f'No match for section {split_section} with length of {len(split_section)}')

        for section in filter(lambda x: (x != False), all_sections):
            split_section = self.locate(driver=section, type='xpath', locator='.//td', multiple=True, info=template_course_info, text=True)
            if len(split_section) == 15:
                if split_section[1] in self.config.CLASS_TYPES:
                    # Format: [Section #, Section Type, Reference #,  Instructor, Open Seats, reserved , taken seats, waiting, status, days, start, end, building, room, course materials
                    course_info = template_course_info.copy()
                    course_info['Section_Number'], course_info['Section_Type'], \
                    course_info['Reference_Number'], prof_to_form, \
                    _, _, course_info['Number_Students'], _, _, course_info['Section_Days'], start, end, building, room, _ = split_section

                    prof_to_form = prof_to_form.split(',')
                    prof_to_form.reverse()
                    course_info['Section_Professor'] = ' '.join(prof_to_form) if prof_to_form else None

                    course_info['Section_Time'] = ' - '.join((start,end))
                    course_info['ClassRoom'] = ' '.join((building, room))
                    self.subject_course_info.append(course_info)
                elif split_section[1] in self.config.IGNORE_CLASS_TYPES:
                    continue
                else:
                    section_not_found(split_section)

            elif len(split_section) == 16:
                if split_section[2] in self.config.CLASS_TYPES:
                    # Format: [Section #, Section Type, Reference #,  Instructor, Open Seats, reserved , taken seats, waiting, status, days, start, end, building, room, course materials
                    course_info = template_course_info.copy()
                    _, course_info['Section_Number'], course_info['Section_Type'], \
                    course_info['Reference_Number'], prof_to_form, \
                    _, _, course_info['Number_Students'], _, _, course_info['Section_Days'], start, end, building, room, _ = split_section


                    prof_to_form = prof_to_form.split(',')
                    prof_to_form.reverse()
                    course_info['Section_Professor'] = ' '.join(prof_to_form) if prof_to_form else None

                    course_info['Section_Time'] = ' - '.join((start, end))
                    course_info['ClassRoom'] = ' '.join((building, room))

                    self.subject_course_info.append(course_info)
                elif split_section[2] in self.config.IGNORE_CLASS_TYPES:
                    continue
                else:
                    section_not_found(split_section)
            # Section Notes
            elif len(split_section) == 2:
                pass
            # Other?
            else:
                section_not_found(split_section)
