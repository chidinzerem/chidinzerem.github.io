#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------
# Penji OpDev Fall 2019
# Parent File for Google Collab
# Author: Cory Paik
# Updated: < MM.DD.YEAR >
# ------------------------

# Consumers: From core.gc_parent import *

# General
import os
import numpy as np
import pandas as pd
from easydict import EasyDict as edict
from collections import namedtuple
# Local
import core.utils as utils
from core import logger
from core.config import cfg


class GoogleCollabParent:
    """ Parent Class For Google Collab Files
    """
    def __init__(self, args):
        self.args = args

        # Get the term (<nice name>, <file name>, <abbr>)
        try:
            self.cterm = cfg.GENERAL[args.term.upper()]
            self.pterm = cfg.GENERAL[args.term.upper() + '_PREV']
        except KeyError:
            logger.error(f'{args.term} not a valid option for term')
            raise SystemExit
        # Get the school config
        try:
            self.school_config = cfg[args.school.upper()]
        except KeyError:
            logger.error(f'{args.school} not a valid option for school')
            raise SystemExit

        File = namedtuple('File', ['name', 'path'])
        files = [File('ct', path=f'data/{args.school}/{self.cterm[1]}/gc_{args.school}_{self.cterm[1]}.csv')]
        print(files[0].name)

        self.files = {
            # Current Term Files
            'ct': f'data/{args.school}/{self.cterm[1]}/gc_{args.school}_{self.cterm[1]}.csv',
            'ct_prof': f'data/{args.school}/{self.cterm[1]}/gc_{args.school}_{self.cterm[1]}_professors.csv',
            'ct_courses': f'data/{args.school}/{self.cterm[1]}/gc_{args.school}_{self.cterm[1]}_courses.csv',
            # Previous Term Files
            'pt': f'data/{args.school}/{self.pterm[1]}/gc_{args.school}_{self.pterm[1]}.csv',
            'pt_prof': f'data/{args.school}/{self.pterm[1]}/gc_{args.school}_{self.pterm[1]}_professors.csv',
            'pt_courses': f'data/{args.school}/{self.pterm[1]}/gc_{args.school}_{self.pterm[1]}_courses.csv',
            # Archive Files
            'archive_tutors': f'data/{args.school}/archive/gc_{args.school}_archive_tutors.csv',
            'archive_prof': f'data/{args.school}/archive/gc_{args.school}_archive_professors.csv',
            'archive_courses': f'data/{args.school}/archive/gc_{args.school}_archive_courses.csv',
            # Scraped Course Lists
            'ct_cl': f'data/{args.school}/{self.cterm[1]}/{args.school}_course_list.csv',
            'pt_cl': f'data/{args.school}/{self.pterm[1]}/{args.school}_course_list.csv',

        }

    def run(self):
        self.update_status()


    def _load(self, file_name_key):
        file_name = self.files[file_name_key]
        df = pd.read_csv(file_name)
        logger.info(f'Found Existing {file_name_key}')
        return df

    def _setup(self):
        """ Setups """
        self.df_ct = self._load('ct')
        self.df_ct_prof = self._load('ct_prof')
        self.df_ct_courses = self._load('ct_courses')

        self.df_arch_courses = self._load('archive_courses')
        self.df_ct = self.df_ct.apply(self.process_cur_term_csv, axis=1)
        # Process Professor CSV: Demand, Ranking, Professor Row #
        self.df_ct_prof = self.df_ct_prof.apply(self.process_prof_courses, axis=1)

        return self.df_ct, self.df_ct_prof

    def _sync_sheets(self):
        """ Sync Infor"""

    def update_status(self):

        self.df_ct = self._load('ct')
        self.df_ct_prof = self._load('ct_prof')
        self.df_ct = self.df_ct.apply(self._df_update_status, axis=1)


    def _convert_string_arr(self, string, dim=1):
        if dim==1:
            string = string.replace('[', '').replace(']', '')
            string = string.split(',')
            array = [int(num.strip()) for num in string if num != '']
            return array

    def _df_update_status(self, row):
        if not row['Professor Row #']:
            row['Status'] = 'Match Error'
        else:
            str_arr = self._convert_string_arr(row['Professor Row #'])
            for num in str_arr:
                prof_row = self.df_ct_prof.loc[num]
                print(prof_row)
                break







    def _get_emails_to_send(self):
        """ Returns a list of namedtuples() to be used for sending emails
            Prof(

        """
        Professor = namedtuple('Professor', 'salutation, first, last, full, desired_course, prev_resp')
        ct_prof = self._load('ct_prof')
        prof_nt_arr = []
        for ir in ct_prof.itertuples():
            if '@' not in str(ir.Email):
                prof_nt_arr.append(ir)

        print(prof_nt_arr)



    def process_cur_term_csv(self, row):
        # Term Sheet: Demand Column
        demand = 3  # Default
        try:
            for ir in self.df_ct_courses.itertuples():
                if ir[1] == row['Course Code'] and not pd.isna(ir[6]):
                    print(ir[1], ir[6])
                    demand = ir[6]
                    break
        except:
            logger.warn(f'Empty Archive Course CSV')
        ranking = demand + (row['# Students'] / 100)

        # Term Sheet: Professor Row Reference #
        row_references = []
        if isinstance(row['Professor'], str):
            prof_names_in = row['Professor'].split(', ')
            for ir in self.df_ct_prof.itertuples():
                [row_references.append(ir[0]) for name in prof_names_in if ir[1] == name]
            assert len(prof_names_in) == len(row_references), \
                f'ERROR: prof names {prof_names_in} != {row_references} row references'

        if row_references == []:
            row_references = None

        row['Demand'], row['Ranking'], row['Professor Row #'] = demand, ranking, row_references
        return row


    def process_prof_courses(self, row):
        # Professor Sheet: All Courses
        # Don't select a class if no email available
        all_courses = []  # (None, None, 0)  # Course Code, Course Row #, Ranking
        best_course = (None, None, 0)
        if '@' in str(row['Email']):
            prof_name = row['Full Name']
            for ir in self.df_ct.itertuples():
                if ir[15] and str(row.name) in str(ir[15])[1:-1].split(', '):
                    all_courses.append((ir[1], ir[0], ir[11]))

            if all_courses:
                # Find their course with the highest ranking
                for course in all_courses:
                    if course[2] > best_course[2]:
                        best_course = course
            else:
                all_courses = None

        row['Desired Course Code'] = best_course[0]
        row['Desired Course Row #'] = int(best_course[1]) if best_course[1] else best_course[1]
        row['All Courses'] = all_courses
        return row



if __name__ == '__main__':
    GoogleCollabParent()