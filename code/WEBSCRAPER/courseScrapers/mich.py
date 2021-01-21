# General
import parse
import numpy as np
# Scraping
from selenium.webdriver.support.ui import Select
# Local
from core import logger
import core.utils as utils
from core.config import cfg
from core.cl_scraper import ClScraper

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
        explored_subjects = self._load()
        explored_adj = len(explored_subjects)

        _subject_select = self.locate(type='xpath', locator="//div[@class='input-group input-group-cg']")
        all_subjects = self.locate(driver=_subject_select, type='tag', locator='option', multiple=True)


        #self._click(_search_button)

        #all_subj_print = [x.get_attribute('value') for x in _subject_options]
        #print(all_subj_print)
        #return

        def subject_parser(element):
            itext = element.get_attribute('innerText')
            parsed = parse.parse('{abbr}: {name}', itext)
            return (parsed['name'], itext) if parsed else (itext, itext)
        all_codes = {subject.get_attribute("value") : subject_parser(subject) for subject in all_subjects}
        explored_adj = len(explored_subjects)

        for idx, code in enumerate(filter(lambda x: (x not in explored_subjects), list(all_codes.keys()))):
            print(code, all_codes[code])

            # Make a class for the subject
            self.subject_course_info = []
            course_info = cfg.GENERAL.CL_COLUMNS.copy()

            # Get the Subject Name, and add values to course_info
            course_info['Department_Abbreviation'] = code
            course_info['Department_Name'] = all_codes[code][0]

            logger.info(f'Selected Subject {course_info["Department_Abbreviation"]} - '
                        f'{int(((idx + explored_adj) / len(all_subjects)) * 100)}% complete')
            # Select subject code
            #Select(self.locate(type='id', locator='contentMain_lbSubject')).select_by_value(code)
            self._click(self.locate(type='xpath', locator="(.//*[normalize-space(text()) and normalize-space(.)='Subject'])[1]/following::button[1]"))
            self._click(self.locate(type='xpath', locator=f"(.//*[normalize-space(text()) and normalize-space(.)='{all_codes[code][1]}'])[2]/input[1]"))
            self._click(self.locate(type='xpath',
                                    locator="(.//*[normalize-space(text()) and normalize-space(.)='Subject'])[1]/following::button[1]"))

            # Eliminate Error of search button off-screen
            _search_button = self.locate(type='id', locator='contentMain_btnSearch')
            self._click(_search_button)

            self.process_subject(course_info)

            # Save to csv
            if self.args.save:
                explored_subjects = np.append(explored_subjects, course_info['Department_Abbreviation'])
                self._save(dict_list=self.subject_course_info, explored_subjects=explored_subjects)
            # Search Page to start
            self.driver.get(self.config.START_URL)

        return explored_subjects


    def process_page(self, template_course_info, *args, **kwargs):
        all_courses = self.locate(type='xpath', locator="//div[@class='col-sm-12']/a", multiple=True)
        if not any(all_courses):
            self.locate(type='xpath', locator='//div[@class="pull-left"]')

        all_links = [course.get_attribute('href') for course in all_courses if course]

        for link in all_links:
            self.driver.get(link)
            self.process_course(template_course_info)
            self.driver.back()
            # if not link:
            #     self.locate(type='xpath', locator='//div[@class="pull-left"]')
            # # exit = self.locate(type='xpath', locator='.//a[contains(@href, "javascript:history.back();")]')
            # # self._click(exit)


    def process_subject(self, template_course_info, *args, **kwargs):
        while True:
            self.process_page(template_course_info)
            next_page_link = self.locate(type='id', locator='contentMain_hlnkNextBtm') # report=False, secs=1
            if next_page_link:
                self.driver.get(next_page_link.get_attribute('href'))
            else:
                break




    def process_course(self, template_course_info, *args, **kwargs):
        course_info = template_course_info.copy()
        title_head = self.locate(type='xpath', locator='//div[@class="panel-title"]')
        course_info['Course_Name'] = self.locate(driver=title_head, type='id', locator='contentMain_lblLongTitle', iText=True)
        course_info['Course_Number'] = self.locate(driver=title_head, type='id', locator='contentMain_lblCatNo', iText=True)
        course_info['Department_Abbreviation'] = self.locate(driver=title_head, type='id', locator='contentMain_lblSubject', iText=True)

        title_bod = self.locate(type='xpath', locator='//div[@class="panel-body"]')
        course_info['Section_Number'] = self.locate(driver=title_bod, type='id', locator='contentMain_lblSection', iText=True)
        course_info['Department_Name'] =  self.locate(driver=title_bod, type='id', locator='contentMain_lblSubjectDescr', iText=True)

        #details
        course_info['Number_Students'] = self.locate( type='id', locator="contentMain_lblWaitCap", iText=True)
        try:
            professor = self.locate(type='xpath', locator='//div[@class="col-sm-10"]/a', iText=True, info=course_info).split(',')
            professor = reversed(professor)
            logger.debug(f'{professor}')
            course_info['Section_Professor'] = ' '.join(professor)
            logger.debug(f"{course_info['Section_Professor']}")
        except AttributeError:
            pass


        #schedule
        course_info['Section_Days'] = self.locate(type='class', locator= "MPCol_Day", iText=True)
        course_info['Section_Time'] = self.locate(type='class', locator= "MPCol_Time", iText=True)
        course_info['ClassRoom'] = self.locate(type='class', locator= "loc_link", iText=True)

        self.subject_course_info.append(course_info)





















