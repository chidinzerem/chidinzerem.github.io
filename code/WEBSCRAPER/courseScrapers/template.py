#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------
# Penji OpDev Fall 2019
# Template Course Scraper
# Author: Cory Paik
# Updated: 27.07.2019
# ------------------------

# General
import numpy as np
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
        ...
        explored_subjects = self._load()
        explored_adj = len(explored_subjects)
        for idx, subject in enumerate(filter(lambda x: (x not in explored_subjects), all_subjects)):
            ...
            course_info = cfg.GENERAL.CL_COLUMNS.copy()
            ...
            logger.info(f'Selected Subject {course_info["Department_Abbreviation"]} - '
                        f'{int(((idx + explored_adj) / len(all_subjects)) * 100)}% complete')
            self.process_subject(course_info)  # Process Subject
            ...
            # Save to csv
            if self.args.save:
                explored_subjects = np.append(explored_subjects, code)
                self._save(dict_list=self.subject_course_info, explored_subjects=explored_subjects)
        return explored_subjects

    def process_subject(self, template_course_info, *args, **kwargs):
        """ Secondary loop through all courses in subject """
        all_courses = self.locate()
        for course in all_courses:
            ...
            course_info = template_course_info.copy()
            ...
            self.process_course(course_info)

    def process_course(self, template_course_info, *args, **kwargs):
        """ Third loop through all sections in course """
        all_sections = self.locate()
        for section in all_sections:
            ...
            course_info = template_course_info.copy()
            ...
            self.subject_course_info.append(course_info)
