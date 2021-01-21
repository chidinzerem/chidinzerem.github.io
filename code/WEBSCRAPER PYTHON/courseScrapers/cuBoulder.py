#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------
# Penji OpDev Fall 2019
# CU Boulder Course Scraper
# Author: Cory Paik
# Updated:
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
    'Section_Type'            : None,
    'Section_Number'          : None,
    'Section_Days'            : None,
    'Section_Time'            : None,
    'Section_Professor'       : None,
    # In process_section_details()
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
                                    root.winfo_screenheight() * 0.75)
        # Read in Configuration File
        self.config = cfg.CU_BOULDER
        # Search Page to start
        self.driver.get(self.config.START_URL)
        self.locate = utils.Locator(main_driver=self.driver)


    def __del__(self):
        self.driver.quit()

    def _click(self, button):
        ActionChains(self.driver).move_to_element(button).click(button).perform()


    def run(self, args):
        _subject_select = self.locate(type='xpath', locator="//select[@id='crit-subject']")
        _subject_options = self.locate(driver=_subject_select, type='tag', locator='option', multiple=True)
        _search_button = self.locate(type='id',locator='search-button')
        # Setup CSV and np array
        explored_subjects = utils.load(term=args.term, school=args.school, col_name='Department_Abbreviation', test=args.test, reset=args.reset)
        # Main Campus Only
        _campus_select_main_campus = self.locate(type='xpath',
                                                 locator="//select[@id='crit-camp']/option[@value='BLDR']").click()
        explored_adj = len(explored_subjects)
        for idx, subject in enumerate(filter(lambda x: (x.get_attribute('value') and x.get_attribute('value') not in explored_subjects), _subject_options)):
            # Make a class for the subject
            self.subject_course_info = []
            course_info = CourseInfo.copy()
            # Get the Subject Name, and add values to course_info
            course_info['Department_Abbreviation'] = saubject.get_attribute('value')
            course_info['Department_Name'] = subject.text.rsplit(' ', 1)[0]
            print(f'Selected Subject {course_info["Department_Abbreviation"]} - {int(((idx+explored_adj)/len(_subject_options))*100)}% complete')
            subject.click()
            # Eliminate Error of search button off-screen
            self._click(_search_button)
            self.process_subject(course_info)
            # Save to csv
            if args.save:
                explored_subjects = np.append(explored_subjects, course_info['Department_Abbreviation'])
                utils.save(dict_list=self.subject_course_info, ref_template=CourseInfo,
                           term=args.term, school=args.school, explored_subjects=explored_subjects, test=args.test)
        return explored_subjects


    def process_subject(self, template_course_info):
        all_courses = self.locate(type='xpath', locator="//div[@class='result result--group-start']"
                                                        "/a[@class='result__link']", multiple=True)
        for course in all_courses:
            abb_name = self.locate(driver=course, type='class', locator='result__code', text=True)
            if not abb_name: continue
            # Filter out Graduate courses
            if int(abb_name.split()[1]) < 5000:
                course_info = template_course_info.copy()
                course_info['Course_Number'] = abb_name.split()[1]
                course_info['Course_Name'] = self.locate(driver=course, type='class', locator='result__title', text=True)
                self._click(course)
                self.process_course(course_info)


    def process_course(self, template_course_info):
        # First find the reference numbers of sections to examine in detail, Workaround for panel refresh
        class_numbers = self.locate(type='xpath', locator="//a[contains(@class, 'course-section--matched')]"
                                                          "/div[@class='course-section-crn']", multiple=True , text=True)
        # Select section based on reference numbers
        for class_number in class_numbers:
            section = self.locate(type='xpath', locator=f"//a[contains(@class, 'course-section--matched') and contains(@data-key, '{class_number}')]")
            # Filter by Section Type
            section_type = self.locate(driver=section, type='class', locator='course-section-schd', text=True)
            if section_type in self.config.CLASS_TYPES:
                course_info = template_course_info.copy()
                course_info['Reference_Number'] = class_number
                course_info['Section_Type'] = section_type
                course_info['Section_Number'] = self.locate(driver=section, type='class', locator='course-section-section', text=True)
                # Days and Time must be split
                _section_days_time = self.locate(driver=section, type='class', locator='course-section-mp', text=True)
                section_days_time = _section_days_time.split()
                # Workaround for 'No Time Assigned'
                meet_bool, two_meet_bool = False, False
                if len(section_days_time) == 2 and _section_days_time != 'Meets online':
                    course_info['Section_Days'], course_info['Section_Time'] = section_days_time
                    meet_bool = True
                # Some classes have multiple meeting Times
                elif ';' in _section_days_time:
                    result = parse.parse('{days1} {time1}; {days2} {time2}',
                                         _section_days_time)
                    if result:
                        course_info['Section_Days'] = f'{result["days1"]}, {result["days2"]}'
                        course_info['Section_Time'] = f'{result["time1"]}, {result["time2"]}'
                    meet_bool = True
                    two_meet_bool = True
                else:
                    course_info['Section_Days'] = _section_days_time
                    course_info['Section_Time'] = 'N/A'
                    course_info['ClassRoom'] = 'N/A'
                    #meet_bool = False
                prof_bool = self.locate(driver=section, type='class', locator='course-section-instr', text=True)
                self._click(section)
                self.process_section_details(course_info, meet_bool, prof_bool, two_meet_bool)


    def process_section_details(self, course_info, meet_bool, prof_bool, two_meet_bool):
        # Find Seats
        seats_info = self.locate(type='xpath', locator='//div[@class="text detail-seats"]', text=True).split('\n')[0]
        result = parse.parse('Maximum Enrollment: {max_enr} / Seats Avail: {seats_avail}', seats_info)
        if result:
            course_info['Number_Students'] = int(result['max_enr']) - int(result['seats_avail'])
        # Find Professor Details
        if prof_bool:
            self.find_prof_info(course_info)
        # Find Meet Details
        if meet_bool:
            self.find_meet_info(course_info, two_meet_bool)
        # Add to list
        self.subject_course_info.append(course_info)


    def find_prof_info(self, course_info):
        panel = self.locate(type='xpath',
                            locator="//div[@class='panel panel--2x panel--kind-details panel--visible']")
        # Search for the Instructor Full Name
        professor_div = self.locate(driver=panel, type='class', locator='instructor-detail', info=course_info)
        if professor_div:
            # Some are Links
            professor_a = self.locate(driver=professor_div, type='tag', locator='a', info=course_info, report=False)
            course_info['Section_Professor'] = professor_a.text if professor_a else professor_div.text


    def find_meet_info(self, course_info, two_meet_bool):
        meeting_info = self.locate(type='class', locator='meet', info=course_info, multiple=two_meet_bool)
        if meeting_info:
            if two_meet_bool:
                classroom_info = ' '
                for info in meeting_info:
                    classroom_a = self.locate(driver=info, type='tag', locator='a',
                                              info=course_info, report=False)
                    classroom_info += ' ' + classroom_a.text if classroom_a else ' '.join(info.text.split()[3:])
                course_info['ClassRoom'] = classroom_info
            # Some are Links
            else:
                classroom_a = self.locate(driver=meeting_info, type='tag', locator='a',
                                          info=course_info, report=False)
                course_info['ClassRoom'] = classroom_a.text if classroom_a else ' '.join(meeting_info.text.split()[3:])
