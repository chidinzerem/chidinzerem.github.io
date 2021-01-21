#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------
# Penji OpDev Fall 2019
# < File Function >
# Author: Cory Paik
# Updated: < DD.MM.YEAR >
# ------------------------

# General
import os
import time
import argparse
import pandas as pd
# For Google Sheets
import pygsheets
# Local
import core.utils as utils
from core import logger
#import core.gsheets_utils as gs_utils
import core.gs_api_utils as gs_api_
from core.config import cfg


class GoogleSheetsParent:
    def __init__(self, args):
        self.args = args
        self.reset_gs = args.reset

        # Get the term (<nice name>, <file name>, <abbr>)
        try:
            self.cterm = cfg.GENERAL[args.term.upper()]
            self.pterm = cfg.GENERAL[args.term.upper()+'_PREV']
        except KeyError:
            logger.error(f'{args.term} not a valid option for term')
            raise SystemExit
        # Get the school config
        try:
            self.school_config = cfg[args.school.upper()]
        except KeyError:
            logger.error(f'{args.school} not a valid option for school')
            raise SystemExit


        self.files = {
            # Current Term Files
            'ct'              : (0, f'{self.cterm[0]}', self._setup_term,
                                 f'data/{args.school}/{self.cterm[1]}/gs_{self.cterm[1]}_{args.school}_0.csv'),
            'ct_prof'         : (1, f'Professors {self.cterm[2]}', self._setup_prof ,
                                 f'data/{args.school}/{self.cterm[1]}/gs_{self.cterm[1]}_{args.school}_1.csv'),
            'ct_courses'      : (2, f'Courses {self.cterm[2]}', self._setup_courses ,
                                 f'data/{args.school}/{self.cterm[1]}/gs_{self.cterm[1]}_{args.school}_2.csv'),
            # Previous Term Files
            'pt'              : (3, f'{self.pterm[0]}', self._setup_term,
                                 f'data/{args.school}/{self.pterm[1]}/gs_{self.pterm[1]}_{args.school}_0.csv'),
            'pt_prof'         : (4, f'Professors {self.pterm[2]}', self._setup_prof ,
                                 f'data/{args.school}/{self.pterm[1]}/gs_{self.pterm[1]}_{args.school}_1.csv'),
            'pt_courses'      : (5, f'Courses {self.pterm[2]}', self._setup_courses ,
                                 f'data/{args.school}/{self.pterm[1]}/gs_{self.pterm[1]}_{args.school}_2.csv'),
            # Archive Files
            'archive_tutors'  : (6, 'Tutors' , self._setup_tutors ,
                                 f'data/{args.school}/archive/gs_archive_{args.school}_6.csv'),
            'archive_prof'    : (7, 'Professor Archive', self._setup_archive_prof ,
                                 f'data/{args.school}/archive/gs_archive_{args.school}_7.csv'),
            'archive_courses' : (8, 'Course Archive', self._setup_archive_courses ,
                                 f'data/{args.school}/archive/gs_archive_{args.school}_8.csv'),
            # Scraped Course Lists
            'ct_cl'           : (-1, None, None,f'data/{args.school}/{self.cterm[1]}/{args.school}_course_list.csv'),
            'pt_cl'           : (-1, None, None, f'data/{args.school}/{self.pterm[1]}/{args.school}_course_list.csv'),

            # Student Orgs
            'student_orgs'    : (-1, 'Student Orgs', None, f'data/{args.school}/{self.cterm[1]}/gs_{args.school}_{self.cterm[1]}_Student_Orgs.csv')

        }

        self.file_keys = ('ct', 'ct_prof', 'ct_courses', 'pt', 'pt_prof', 'pt_courses',
                          'archive_tutors', 'archive_prof', 'archive_courses')

    def _load_all(self):
        return [self._load(key) for key in self.file_keys]


    def _load(self, file_name_key):
        file_name = self.files[file_name_key][3]
        try:
            df = pd.read_csv(file_name)
            logger.info(f'Found Existing {self.files[file_name_key][1]}')
            return df
        except FileNotFoundError:
            #logger.error(f'File not found: {file_name}')
            self._setup(file_name_key)
            # raise SystemExit

    def _save(self, df, file_name_key):
        file_name = self.files[file_name_key][3]
        df.to_csv(index=False, path_or_buf=file_name)

    def _connect_google_sheet(self, sheet_name_in=None):
        # Create a new sheet in folder
        sheet_name = sheet_name_in if sheet_name_in else f'{self.school_config.NICE_NAME} Course List'
        gc = pygsheets.authorize(service_file='core/credentials/penji_dev_key.json')
        try:
            sh = gc.open(sheet_name)
            if self.reset_gs:
                gc.drive.delete(sh.id, supportsTeamDrives=True)
                sh = gc.create(sheet_name, folder=self.school_config.FOLDER_ID)
                logger.info(f'Reset {sheet_name} in google drive')
            else:
                logger.info(f'Found {sheet_name} in google drive, modifying sheet')
        except (pygsheets.exceptions.SpreadsheetNotFound, pygsheets.exceptions.WorksheetNotFound) as e:
            logger.info(f'Could not find {sheet_name} in google drive, creating a new one')
            sh = gc.create(sheet_name, folder=self.school_config.FOLDER_ID)
            self.reset_gs = True
        return sh

    def _setup_all(self):
        for key in self.file_keys:
            if not os.path.exists(self.files[key][3]):
                df = self._setup(key)
                self._save(df, key)
                while not os.path.exists(self.files[key][3]):
                    time.sleep(1)

    def _setup(self, file_name_key):
        file_info = self.files[file_name_key]
        sheet_idx = file_info[0]
        gs_cl_df = None
        # Current term setup
        if sheet_idx in (0, 1, 2):
            try:
                gs_cl_df = pd.read_csv(self.files['ct'][3])
            except FileNotFoundError:
                logger.info(f'No existing Google Sheets current term file in location {self.files["ct"][3]}')
                try:
                    cl_df = pd.read_csv(self.files['ct_cl'][3])
                except FileNotFoundError:
                    logger.info(f'No existing course list csv file found in location {self.files["ct_cl"][3]}')
                    raise SystemExit
                gs_cl_df = self._setup_term(cl_df)
                if self.args.save:
                    self._save(gs_cl_df, 'ct')
            # If current term csv
            gs_df = gs_cl_df if sheet_idx == 0 else file_info[2](gs_cl_df)
        # Previous Term
        elif sheet_idx in (3, 4, 5):
            try:
                gs_cl_df = pd.read_csv(self.files['pt'][3])
            except FileNotFoundError:
                logger.info(f'No existing Google Sheets current term file in location {self.files["ct"][3]}')
            gs_df = file_info[2](gs_cl_df)
        # Tutors & Archive
        elif sheet_idx in (6, 7, 8):
            gs_df = file_info[2](None)
        # Error, invalid sheet
        else:
            logger.error(f'{sheet_idx} not valid sheet index')
            raise SystemExit
        if self.args.save:
            self._save(gs_df, file_name_key)
        return gs_df

    def _setup_term(self, df):
        gs_data = None
        if isinstance(df, pd.DataFrame):
            num_rows = len(df.index)
            gs_data = {key: [None] * num_rows for key in cfg.GENERAL.WKS_COLUMNS['Term']}
            key_set = {
                'Abbreviation': 'Department_Abbreviation',
                'Course': 'Course_Number',
                'Name': 'Department_Name',
                'Title': 'Course_Name',
                'Professor': 'Section_Professor',
                '# Students': 'Number_Students',
                'Time': 'Section_Time',
                'Days': 'Section_Days',
                'Classroom': 'ClassRoom',
                'Section Reference #': 'Reference_Number'
            }

            for idx, col in df.iterrows():
                # Set Directly transferable data
                for gs_key, df_key in key_set.items():
                    temp_val = df[df_key][idx]
                    if isinstance(temp_val, str):
                        #print(temp_val)
                        temp_val = temp_val.strip()  # TODO: Correct formatting to avoid whitespace
                    gs_data[gs_key][idx] = temp_val
                # Set Course Code
                gs_data['Course Code'][idx] = str(df['Department_Abbreviation'][idx]) + ' ' + str(
                    df['Course_Number'][idx])

            term_df = pd.DataFrame(data=gs_data, columns=cfg.GENERAL.WKS_COLUMNS['Term'])


            print(f'num students col\n',term_df['# Students'])
            term_df = term_df[term_df['# Students'] != 'Canceled']
            term_df['# Students'] = term_df['# Students'].fillna(0)
            term_df = term_df.astype(dtype={'# Students': 'int64'})
            # Workaround: If School had no student count
            if not sum(term_df['# Students']) == 0:
                term_df = term_df[term_df['# Students'] > 10]
        else:
            term_df = pd.DataFrame(data=gs_data, columns=cfg.GENERAL.WKS_COLUMNS['Term'])
        print(term_df.head())
        return term_df

    def _setup_prof(self, df):
        gs_data = None
        if isinstance(df, pd.DataFrame):
            all_prof = list(df['Professor'])
            professors = list({}.fromkeys(all_prof).keys())
            professors = list(set(filter(lambda v: v == v and v != '', professors)))
            full_names, first_names, last_names = [], [], []
            for all_names in professors:
                names_split = all_names.split(', ')
                for name in names_split:
                    if name not in full_names:
                        full_names.append(name)
                        split_name = name.split()
                        first_names.append(split_name[0])
                        last_names.append(' '.join(split_name[1:]))

            gs_data = {'Full Name': full_names, 'Salutation': ['Dr.'] * len(full_names), 'First Name': first_names,
                       'Last Name': last_names, }
        prof_df = pd.DataFrame(data=gs_data, columns=cfg.GENERAL.WKS_COLUMNS['Professors'])
        return prof_df

    def _setup_courses(self, term_df):
        gs_data = None
        if isinstance(term_df, pd.DataFrame):
            # takes in term df
            data = {key: [] for key in cfg.GENERAL.WKS_COLUMNS['Courses']}
            for idx, col in term_df.iterrows():
                if term_df['Course Code'][idx] not in data['Course Code']:
                    data['Course Code'].append(term_df['Course Code'][idx])
                    data['Name'].append(term_df['Name'][idx])
                    data['Title'].append(term_df['Title'][idx])
            num_rows = len(data['Course Code'])
            gs_data = {key: ([None] * num_rows if lst == [] else lst) for key, lst in data.items()}
        courses_df = pd.DataFrame(data=gs_data, columns=cfg.GENERAL.WKS_COLUMNS['Courses'])
        return courses_df

    def _setup_tutors(self, df):
        gs_data = None
        if isinstance(df, pd.DataFrame):
            tutors_df = df
            # num_rows = len(df.index)
            # gs_data = {key: [None] * num_rows for key in cfg.GENERAL.WKS_COLUMNS['Tutors']}
        tutors_df = pd.DataFrame(data=gs_data, columns=cfg.GENERAL.WKS_COLUMNS['Tutors'])
        return tutors_df

    def _setup_archive_prof(self, df):
        gs_data = None
        if isinstance(df, pd.DataFrame):
            all_prof = list(df['Professor'])
            professors = list({}.fromkeys(all_prof).keys())
            professors = list(set(filter(lambda v: v == v, professors)))
            full_names, first_names, last_names = [], [], []
            for all_names in professors:
                names_split = all_names.split(', ')
                for name in names_split:
                    if name not in full_names:
                        full_names.append(name)
                        split_name = name.split()
                        first_names.append(split_name[0])
                        last_names.append(' '.join(split_name[1:]))

            gs_data = {'Full Name': full_names, 'Salutation': ['Dr.'] * len(full_names), 'First Name': first_names,
                       'Last Name': last_names, }

        prof_df = pd.DataFrame(data=gs_data, columns=cfg.GENERAL.WKS_COLUMNS['Professor Archive'])
        return prof_df


    def _setup_archive_courses(self, term_df):
        gs_data = None
        if isinstance(term_df, pd.DataFrame):
            data = {key: [] for key in cfg.GENERAL.WKS_COLUMNS['Course Archive']}
            for idx, col in term_df.iterrows():
                if term_df['Course Code'][idx] not in data['Course Code']:
                    data['Course Code'].append(term_df['Course Code'][idx])
                    data['Name'].append(term_df['Name'][idx])
                    data['Title'].append(term_df['Title'][idx])
            num_rows = len(data['Course Code'])
            gs_data = {key: ([None] * num_rows if lst == [] else lst) for key, lst in data.items()}
        courses_df = pd.DataFrame(data=gs_data, columns=cfg.GENERAL.WKS_COLUMNS['Course Archive'])
        return courses_df




    def run(self, *args, **kwargs):


        raise NotImplementedError



