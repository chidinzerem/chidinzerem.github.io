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

from pprint import pprint as pprint
#from scrapy.selector import Selector

# Sample Template Structure
CourseInfo = {
    # For updating reference
    'Reference_Number'        : None,
    # In process_subject()
    'Department_Abbreviation' : None, #
    'Department_Name'         : None, #
    'Course_Number'           : None,
    'Course_Name'             : None,
    # In process_course()
    'Section_Type'            : None, #TODO
    'Section_Number'          : None,
    'Section_Days'            : None,
    'Section_Time'            : None,
    'Section_Professor'       : None,
    'Number_Students'         : None,
    'ClassRoom'               : None,
}

class Scraper:
    def __init__(self, args):
        # Save Args and Configuration File
        self.args = args
        self.config = cfg[self.args.school.upper()]
        # Initialize web driver
        self.driver = webdriver.Chrome(self.args.driver)
        # Setup window to be full width and 3/4 height
        root = tkinter.Tk()
        self.driver.set_window_position(0, 0)
        self.driver.set_window_size(root.winfo_screenwidth(),
                                    root.winfo_screenheight() * 0.75)
        # Search Page to start
        self.driver.get(self.config.START_URL)
        self.locate = utils.Locator(main_driver=self.driver)

    def __del__(self):
        self.driver.quit()

    def _click(self, button):
        try:
            button.click()
        except:
            # print(f'INFO: Could not perform normal click on element\n'
            #       f'      Attempting ActionChain click ')
            ActionChains(self.driver).move_to_element(button).click(button).perform()

    def run(self):
        #expand_all = self.locate(type='xpath', locator='//a[@id="facetapi-link--6607"]').click()
        _all_subjects = self.locate(type='xpath', locator='//li[@class="expanded last"]'
                                                          '/div[@class="item-list"]'
                                                          '/ul/li[@class="leaf"]/a', multiple=True)
        all_subject_links = {subject.get_attribute('id') : subject.get_attribute('href') for subject in _all_subjects if subject}
        # Setup CSV and np array
        explored_subjects = utils.load(term=self.args.term, school=self.args.school, col_name='Department_Abbreviation', test=self.args.test, reset=self.args.reset)

        for code in filter(lambda x: (x not in explored_subjects), list(all_subject_links.keys())):
            self.subject_course_info = []
            course_info = CourseInfo.copy()
            self.driver.get(all_subject_links[code])
            self.process_subject(course_info)
            # Save to csv
            if self.args.save:
                explored_subjects = np.append(explored_subjects, code)
                utils.save(dict_list=self.subject_course_info, ref_template=CourseInfo,
                           term=self.args.term, school=self.args.school, explored_subjects=explored_subjects, test=self.args.test)
        return explored_subjects

    def process_subject(self, template_course_info):
        # Go to first page
        first_page_link = self.locate(type='xpath', locator='//ul[@class="pager"]'
                                                  '/li[@class="pager-first first"]/a', report=False, secs=1)
        if first_page_link:
            self.driver.get(first_page_link.get_attribute('href'))
        else:
            print('WARNING: Could not find fist page link')
        while True:
            self.process_page(template_course_info)
            next_page_link = self.locate(type='xpath', locator='//ul[@class="pager"]'
                                                          '/li[@class="pager-next"]/a', report=False)
            if next_page_link:
                self.driver.get(next_page_link.get_attribute('href'))
            else:
                break

    def process_page(self, template_course_info):
        all_course_a = self.locate(type='xpath', locator='//a[@class="ls-section-wrapper"]', multiple=True)
        all_course_ids = [course.get_attribute('href') for course in all_course_a if course]
        for course_link in filter(lambda x: (x != False), all_course_ids):
            self.driver.get(course_link)
            self.process_section_detail_page(template_course_info)

    def process_section_detail_page(self, template_course_info):
        title_div = self.locate(type='xpath', locator='//div[@class="detail-title"]')
        section_type = self.locate(driver=title_div, type='class', locator='detail-section-code', iText=True)
        # Filter Class Types
        if section_type in self.config.CLASS_TYPES:
            course_info = template_course_info.copy()
            # Get Course Name
            course_info['Course_Name'] = self.locate(type='xpath', locator='//div[@class="hbr"]'
                                                                              '/h2[@class="detail-course-title fmpbook"]', iText=True)
            # Process Title Div
            abb_name = self.locate(driver=title_div, type='class', locator='detail-section-name', iText=True).split()
            course_info['Department_Abbreviation'], course_info['Course_Number'] = abb_name
            course_info['Section_Number'] = self.locate(driver=title_div, type='class', locator='detail-section-count', iText=True)
            if not len(self.subject_course_info): print(f'Selected Subject {abb_name[0]}')
            # Process Course Details
            course = self.locate(type='xpath', locator='//div[@class="detail-left-column"]')
            department_str = self.locate(driver=course, type='class', locator='detail-section-dept', iText=True)
            course_info['Department_Name'] = parse.parse('offered through {dep}', department_str)['dep']
            course_info['Section_Type'] = section_type
            course_info['Section_Days'] = self.locate(driver=course, type='class', locator='detail-days', iText=True)
            course_info['Section_Time'] = self.locate(driver=course, type='class', locator='detail-time', iText=True)

            course_info['Section_Professor'] = self.locate(driver=course, type='xpath', locator='//div[contains(@class, "detail-instructors")]',
                                                           iText=True, report=False, secs=1)
            course_info['ClassRoom'] = self.locate(driver=course, type='class', locator='detail-location', iText=True)
            reference_str = self.locate(driver=course, type='class', locator='detail-section-number', iText=True)
            course_info['Reference_Number'] = parse.parse('Class #:{num}', reference_str)['num']
            enrollment_div = self.locate(type='xpath', locator='//div[@class="detail-class-enrollment-flex"]',
                                         iText=True).replace('\n', ' ').replace('\t', ' ')
            result = parse.parse('Enrolled: {in} Waitlisted: {w} Capacity: {cap} Waitlist Max: {wtot}', enrollment_div)
            course_info['Number_Students'] = int(result['cap']) - int(result['in'])
            course_info = { k: (None if v is False else v) for k, v in course_info.items() }
            #pprint(course_info)
            self.subject_course_info.append(course_info)
            self.driver.back()










