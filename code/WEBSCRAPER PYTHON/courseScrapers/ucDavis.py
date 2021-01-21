# General
import numpy as np
import parse
# Local
from core import logger
import core.utils as utils
from core.config import cfg
from core.cl_scraper import ClScraper
from pprint import pprint as pprint

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
        _subject_select = self.locate(type='xpath', locator="//select[@name='subject']")
        _subject_options = self.locate(driver=_subject_select, type='tag', locator='option', multiple=True)
        _search_button = self.locate(type='class', locator="rounded-button")
        # Setup CSV and np array
        explored_subjects = self._load()

        for subject in filter(lambda x: (x.get_attribute('value') != "-" and x.get_attribute('value') not in explored_subjects), _subject_options):
            # Make a class for the subject
            self.subject_course_info = []
            course_info = CourseInfo.copy()
            # Get the Subject Name, and add values to course_info
            course_info['Department_Abbreviation'] = subject.get_attribute('value')
            course_info['Department_Name'] = subject.text.rsplit(' ', 1)[0]
            print(f'Selected Subject {course_info["Department_Abbreviation"]}')
            subject.click()
            # Eliminate Error of search button off-screen
            self._click(_search_button)
            self.process_subject(course_info)
            # Save to csv
            if args.save:
                explored_subjects = np.append(explored_subjects, course_info['Department_Abbreviation'])
                self._save(dict_list=self.subject_course_info, explored_subjects=explored_subjects)
        return explored_subjects


    def process_subject(self, template_course_info, *args, **kwargs):
        course_info = template_course_info.copy()
        all_courses = self.locate(type='xpath', locator="//div[@id='courseResultsDiv']/h2/table/tbody/tr", multiple=True)[4:-1]

        for course in all_courses:
            detail_td = self.locate(driver=course, type='xpath', locator= ".//td/a[contains(@title, 'View Course Detail')]")

            if not detail_td :
                reset = self.locate(type='xpath',
                                    locator="//button[value='Reset']")
                self._click(reset)

            self._click(detail_td)
            self.process_course(course_info)
            close = self.locate (type='')
            close = self.locate(type='xpath', )
            # close = self.locate(type='xpath', locator='.//div[contains(@class, "x-tool x-tool-close")]')
            # self._click(close)
            self.driver.back()



    def process_course(self,  template_course_info, *args, **kwargs):
        class_info_table, days_time_table = self.locate(type='xpath', locator= "//div[@id='detailWin_body']/div/table", multiple=True)[:2]



        class_info = self.locate(driver=class_info_table, type='xpath', locator='.//tbody/tr/td', multiple=True,
                                   info=template_course_info, text=True)
        days_time_info = self.locate(driver=days_time_table, type='xpath', locator='.//tbody/tr/td', multiple=True,
                                   info=template_course_info, text=True)

        #info we need
        #format: [section #, subject area, term ,reference #, instructor, units, random, random ,seats available, max enrolled]
        #[location, day, time, offcampus]

        course_info = template_course_info.copy()
        # Get Course Name
        course_info['Course_Name'] = class_info[0].split('- ')[1]

        # Process Title Div
            #course number
        result = parse.parse('{a} {c_num} {b} - {stype}', str(class_info[0]))
        if not result:
            result = parse.parse('{a} {c_num} {b} — {stype}', str(class_info[0]))
            print(f'ERROR: No result for {class_info[0]}')
        if result: course_info['Course_Number'] = result['c_num']

            #course Section
        result2 = parse.parse('{a} {b} {c_sec} - {stype}', str(class_info[0]))
        if not result2:
            result2 = parse.parse('{a} {b} {c_sec} - {stype}', str(class_info[0]))
            print(f'ERROR: No result for {class_info[0]}')
        if result2: course_info['Section_Number'] = result2['c_sec']


        # Process Course Details
        course_info['Department_Name'] = class_info[1].split(': ')[1]

            #course type
        result3 = parse.parse('{a} {b} {c} - {stype}', str(class_info[0]))
        if not result3:
            result3 = parse.parse('{a} {b} {c - {stype}', str(class_info[0]))
            print(f'ERROR: No result for {class_info[0]}')
        if result3: course_info['Section_Type'] = result2['stype']

        course_info['Section_Days'] = days_time_info[2]
        course_info['Section_Time'] = days_time_info[3]
        course_info['Section_Professor'] = class_info[4].split(': ')[1]
        course_info['ClassRoom'] = days_time_info[4]
        course_info['Reference_Number'] = class_info[3].split(': ')[1]
        #course_info['Number_Students'] = class_info[9].split(': ')[1] #can be in either index 7 or 9

        pprint(course_info)
        #self.subject_course_info.append(course_info)
        #print(class_info, days_time_info)
        #return

#TODO: test the reset, figure out how i can pick which index i need for which spot. then should be ready to go


















