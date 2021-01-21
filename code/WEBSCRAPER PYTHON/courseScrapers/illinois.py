# General
import parse
import numpy as np
# Scraping
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import InvalidArgumentException
# Local
from core import logger
import core.utils as utils
from core.config import cfg
from core.cl_scraper import ClScraper
from selenium.webdriver.common.keys import Keys
from pprint import pprint as pprint

import time
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


class Scraper(ClScraper):
    def __init__(self, args):
        # Use the parent class
        ClScraper.__init__(self, args)
        self.subject_course_info = None

    def run(self):
        time.sleep(1)
        self._click(self.locate(type='link_text', locator='I Agree'))

        _subject_select = self.locate(type='id', locator="subjectCode")
        _subject_options = self.locate(driver=_subject_select, type='tag', locator='option', multiple=True)[1:]

        subject_options = [(option.get_attribute('value'), option.text) for option in _subject_options]


        # Setup CSV and np array
        explored_subjects = self._load()

        for subject in filter(lambda x: (x[0] not in explored_subjects and x[0] != '-'), subject_options):
            # Make a class for the subject
            self.subject_course_info = []
            course_info = cfg.GENERAL.CL_COLUMNS.copy()
            # Get the Subject Name, and add values to course_info
            course_info['Department_Abbreviation'] = subject[0]
            course_info['Department_Name'] = subject[1].rsplit(' ', 1)[0]
            print(f'Selected Subject {course_info["Department_Abbreviation"]}')
            Select(self.locate(type='id', locator="subjectCode")).select_by_value(subject[0])
            # Eliminate Error of search button off-screen
            self.locate(type='id', locator="subjectCode").send_keys(Keys.ENTER)
            # self._click(_search_button)
            # _search_button.click()
            self.process_subject(course_info)
            # Save to csv
            if self.args.save:
                explored_subjects = np.append(explored_subjects, course_info['Department_Abbreviation'])
                self._save(dict_list=self.subject_course_info, explored_subjects=explored_subjects)
            self.driver.get(self.config.START_URL)

        return explored_subjects



    def process_page(self, template_course_info, *args, **kwargs):
        all_courses = self.locate(type='xpath', locator="//tbody/tr[@role='row']/td/a", multiple=True)[1:]
        all_links = [course.get_attribute('href') for course in all_courses]
        current_link = (self.driver.current_url, 'https://courses.illinois.edu/search?year=2019&term=fall&keyword=&keywordType=qs&instructor=&collegeCode=&subjectCode=ACCY&creditHour=&degreeAtt=&courseLevel=&genedCo',
                        'https://courses.illinois.edu/search?year=2019&term=fall&keyword=&keywordType=qs&instructor=&collegeCode=&subjectCode=ACCY&creditHour=&degreeAtt=&courseLevel=&genedCode1=&genedCode2=&genedCode3=&genedType=all&partOfTerm=&_online=on&_nonOnline=on&_open=on&_evenings=on#none')

        #print(all_links)
        for link in filter(lambda x: (x not in current_link), all_links):
            self.driver.get(link)
            #print(f'Got link {link}')
            self.process_course(template_course_info)
            self.driver.back()

        # course_dets = self.locat(type='xpath', locator= "//tbody/tr[@role='row']/td", multiple=True, info=template_course_info)
        # print(course_dets)


    def process_subject(self, template_course_info, *args, **kwargs):
        while True:
            self.process_page(template_course_info)
            try:
                next_page_link = self.locate(type='id', locator='search-result-dt_next') # report=False, secs=1
                self.driver.get(next_page_link.get_attribute('href'))
            except InvalidArgumentException:
                break



    def process_course(self, template_course_info, *args, **kwargs):
        temp_course_info = template_course_info.copy()
        all_sec = self.locate(type='xpath', locator= "//tbody/tr[@role='row']", multiple=True, info=template_course_info)

        temp_course_info['Course_Number'] = self.locate(type='xpath', locator= "//div[@class='col-sm-12']/h1[@class='app-inline']", iText=True)
        temp_course_info['Course_Name'] = self.locate(type='xpath', locator= "//div[@class='col-sm-12']/span[@class='app-label app-text-engage']", iText=True)

        #if temp_course_info['Course_Number'] < 500:

        for sec in all_sec:
            class_info_table = self.locate(driver=sec, type="xpath", locator=".//td", multiple = True, iText= True)
            if class_info_table[4] in  self.config.CLASS_TYPES:
                course_info = temp_course_info.copy()
                try:
                    course_info['Section_Number'] = class_info_table[3]
                    course_info['Section_Type'] = class_info_table[4]
                    course_info['Section_Time'] = class_info_table[6]
                    course_info['Section_Days'] = class_info_table[7]
                    course_info['ClassRoom'] = class_info_table[8]
                    course_info['Section_Professor'] = class_info_table[9]
                except IndexError:
                    pass
                self.subject_course_info.append(course_info)

            else:
                logger.debug(f'Skipped Class Type {class_info_table[4]}')



