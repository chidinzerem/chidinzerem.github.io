#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------
# Penji OpDev Fall 2019
# Course Scraper
# Author: Cory Paik
# Updated: 27.07.2019
# ------------------------

# General
import os
import csv
import tkinter
import numpy as np
import pandas as pd
# Web Scraping
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import WebDriverException
# Local
from core import logger
from core.config import cfg
import core.utils as utils


class ClScraper:
    def __init__(self, args):
        # Save Args and Configuration File
        self.args = args
        self.config = cfg[args.school.upper()]
        # Initialize web driver
        chrome_options = Options()
        if args.headless:
            chrome_options.add_argument('--headless')
        self.driver = webdriver.Chrome(executable_path=args.driver, options=chrome_options)
        # Setup window to be full width and 3/4 height
        root = tkinter.Tk()
        self.driver.set_window_position(0, 0)
        self.driver.set_window_size(root.winfo_screenwidth()*args.width,
                                    root.winfo_screenheight()*args.height)
        # Search Page to start
        self.driver.get(self.config.START_URL)
        self.locate = utils.Locator(main_driver=self.driver)
        # File Names
        self.csv_file_name = f'data/test_runs/{args.school}_course_list.csv' if args.test \
            else f'data/{args.school}/{args.term}/{args.school}_course_list.csv'
        self.npy_file_name = f'data/test_runs/{args.school}_explored_subj.npy' if args.test \
            else f'data/{args.school}/{args.term}/{args.school}_explored_subj.npy'

    def __del__(self):
        self.driver.quit()

    def _click(self, button, ac=False, off=None, pause=0):
        if ac:
            if isinstance(off, tuple):
                ActionChains(self.driver).move_to_element_with_offset(button, off[0], off[1]).pause(pause).click(button).perform()
            else:
                ActionChains(self.driver).move_to_element(button).click(button).perform()
            return
        try:
            button.click()
        except WebDriverException:
            logger.debug(f'Could not perform normal click on element\n'
                         f'       Attempting ActionChain click ')
            try:
                ActionChains(self.driver).move_to_element(button).click(button).perform()
            except:
                logger.debug(f'Could not perform ActionChain click on element')
        finally:
            pass



    def _save(self, dict_list, explored_subjects=None):
        """ Saves a csv of data and np file of explored subjects """
        np.save(self.npy_file_name, explored_subjects)
        write_header_bool = False if os.path.exists(self.csv_file_name) else True
        with open(self.csv_file_name, 'a', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=list(cfg.GENERAL.CL_COLUMNS.keys()))
            if write_header_bool:
                writer.writeheader()
            [writer.writerow(course) for course in dict_list]

    def _load(self, check_np_only=False):
        if os.path.exists(self.csv_file_name) and not self.args.reset:
            df = pd.read_csv(self.csv_file_name, encoding = "utf-8")
            all_subjects = list(df['Department_Abbreviation'])
            explored_subjects = list({}.fromkeys(all_subjects).keys())
            if os.path.exists(self.npy_file_name):
                npy_explored_subjects = np.load(self.npy_file_name, allow_pickle=True)
                if check_np_only:
                    explored_subjects = npy_explored_subjects
                else:
                    [explored_subjects.append(subject) for subject in npy_explored_subjects if
                     subject not in explored_subjects]
        # Reset explored subjects
        else:
            self._reset()
            explored_subjects = []
        return explored_subjects

    def _reset(self):
        [os.remove(file_name) for file_name in [self.csv_file_name, self.npy_file_name] if os.path.exists(file_name)]
        logger.info(f'Reset course list files for {self.args.school}')
        logger.info('Starting from scratch')


    def run(self):
        """ Main loop through all subjects
            Pseudocode:
            explored_subjects = self._load()
            explored_adj = len(explored_subjects)
            for idx, subject in enumerate(filter(lambda x: (x not in explored_subjects), all_subjects)):
                ...
                course_info = cfg.GENERAL.CL_COLUMNS.copy()
                ...
                logger.info(f'Selected Subject {course_info["Department_Abbreviation"]} - '
                            f'{int(((idx + explored_adj) / len(all_subjects)) * 100)}% complete')
                self.process_subject(course_info) # Process Subject
                ...
                # Save to csv
                if args.save:
                    explored_subjects = np.append(explored_subjects, code)
                    self._save(dict_list=self.subject_course_info, explored_subjects=explored_subjects)
            return explored_subjects
        """
        raise NotImplementedError

    def process_subject(self, template_course_info, *args, **kwargs):
        """ Secondary loop through all courses in subject
            Pseudocode:
            for course in all_courses
                ...
                self.process_course(course_info) # Process Course
        """
        raise NotImplementedError

    def process_course(self, template_course_info, *args, **kwargs):
        """ Third loop through all sections in course
            Pseudocode:
            for section in all_sections
                ...
                self.subject_course_info.append(course_info)
        """
        raise NotImplementedError
