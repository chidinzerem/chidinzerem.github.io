#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------
# Penji OpDev Fall 2019
# GS Run Wrapper
# Author: Cory Paik
# Updated:
# ------------------------

# General
import os
import argparse
import pandas as pd
# For Google Sheets
import pygsheets
# Local
import core.utils as utils
from core import logger
import core.gs_api_utils as gs_api_
from core.config import cfg
from core.gs_parent import GoogleSheetsParent


class GoogleSheetsPullFromArchive(GoogleSheetsParent):
    def __init__(self, args):
        GoogleSheetsParent.__init__(self, args)

        # Ensure all files are created and saved properly
        self._setup_all()

        self.df_ct_prof = self._load('ct_prof')
        self.df_ct_courses = self._load('ct_courses')
        self.df_arch_prof = self._load('archive_prof')
        self.df_arch_courses = self._load('archive_courses')

    def run(self, *args, **kwargs):
        # Pull data for prof file
        self.df_ct_prof = self.df_ct_prof.apply(self.pull_arch_prof, axis=1)
        # Pull data for courses file
        #self.df_ct_courses = self.df_ct_courses.apply(self.pull_arch_courses, axis=1)
        print(self.df_ct_prof)
        if self.args.save:
            self._save(self.df_ct_prof, 'ct_prof')
            self._save(self.df_ct_courses, 'ct_courses')

    def pull_arch_prof(self, row):
        try:
            for ir in self.df_arch_prof.itertuples():
                if ir[1] == row['Full Name'] and '@' in str(ir[5]):
                    print(ir[1], ir[5])
                    row['Email'] = ir[5]
                    row['Previous Response'] = ir[6]
                    row['Term Last Sent'] = ir[7]
                    break
        except:
            logger.warn(f'Empty Archive Professor CSV')
        return row

    def pull_arch_courses(self, row):
        try:
            for ir in self.df_arch_courses.itertuples():
                if ir[1] == row['Course Code'] and not pd.isna(ir[4]):
                    print(ir[1], ir[4])
                    row['Archive Demand In'] = ir[4]
                    break
        except:
            logger.warn(f'Empty Archive Course CSV')
        return row


class GoogleSheetsPrep(GoogleSheetsParent):
    def __init__(self, args):
        GoogleSheetsParent.__init__(self, args)

        self.df_ct = self._load('ct')
        self.df_ct_prof = self._load('ct_prof')
        self.df_ct_courses = self._load('ct_courses')

        self.df_arch_courses = self._load('archive_courses')

    def run(self, *args, **kwargs):
        """ Sets up Professor df for google sheets upload
            Needs demand and ranking in order to deduct desired course
            Professor Row Reference #s
        """
        # Process Current term CSV: Demand, Ranking, Professor Row #
        self.df_ct = self.df_ct.apply(self.process_cur_term_csv, axis=1)
        # Process Professor CSV: Demand, Ranking, Professor Row #
        self.df_ct_prof = self.df_ct_prof.apply(self.process_prof_courses, axis=1)

        # Clear out those temporary values

        self.df_ct = self.df_ct.apply(self.clear_temp_values, axis=1)
        if self.args.save:
            self._save(self.df_ct, 'ct')
            self._save(self.df_ct_prof, 'ct_prof')
        else:
            print(self.df_ct)
            print(self.df_ct_prof)



    def clear_temp_values(self, row):
        row['Demand'], row['Ranking'] = None, None
        return row


    def process_cur_term_csv(self, row):
        # Term Sheet: Demand Column
        demand = 3 # Default
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
                [row_references.append(ir[0]+2) for name in prof_names_in if ir[1] == name]
            assert len(prof_names_in) == len(row_references), \
                f'ERROR: prof names {prof_names_in} != {row_references} row references'

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
                if ir[15] and str(row.name+2) in str(ir[15])[1:-1].split(', '):
                    all_courses.append((ir[1], ir[0]+2, ir[11]))

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


class GoogleSheetsUpload(GoogleSheetsParent):
    def __init__(self, args):
        GoogleSheetsParent.__init__(self, args)
        self.status_arr = ['No', 'Sent for different course', 'Match Error', 'Awaiting Response', 'Yes']


    def run(self):
        # Create a new sheet in folder
        sh = self._connect_google_sheet()



        # Make sure the sheets are setup properly
        gs_df_arr = self._load_all()
        self.num_wks = len(gs_df_arr)
        # TODO: Professor row Reference #s add 2

        # Find number of rows and columns for each
        shapes = []
        setup_formulas = [self.setup_term_formulas, self.setup_professor_formulas, self.setup_course_formulas,
                          None, None, None, None, None, self.setup_arch_course_formulas]


        for idx in range(len(gs_df_arr)):
            # load csv as pd df and upload it
            gs_df = gs_df_arr[idx]
            shapes.append(gs_df.shape)
            # Create new sheets
            if self.reset_gs:
                wks = sh.add_worksheet(self.files[self.file_keys[idx]][1], rows=shapes[idx][0]+10, cols=shapes[idx][1], index=idx)
                if idx == 0:
                    sh.del_worksheet(sh.worksheet_by_title('Sheet1'))
            else:
                wks = sh[idx]
            # Upload the data
            if self.args.data:
                wks.set_dataframe(gs_df, (1, 1))
                wks.replace('NaN', '')
            # Add The Formulas
            if self.args.formulas and setup_formulas[idx]:
                term = self.pterm if idx in (3,4,5) else self.cterm
                setup_formulas[idx](wks, term)

        if self.args.format:
            self.format_sheet(sh, shapes)

    def format_sheet(self, sh, shapes):
        # Format Tutor Columns
        gs_api_.format_tutor_col(sh=sh, wks=sh[0], shape=shapes[0], col_idx=10) # Current Term
        gs_api_.format_tutor_col(sh=sh, wks=sh[2], shape=shapes[2], col_idx=7)  # Current Courses
        gs_api_.format_tutor_col(sh=sh, wks=sh[3], shape=shapes[3], col_idx=10) # Prev Term
        gs_api_.format_tutor_col(sh=sh, wks=sh[5], shape=shapes[5], col_idx=7)  # Prev Courses

        gs_api_.format_tutor_col(sh=sh, wks=sh[8], shape=shapes[8], col_idx=6)  # Archive Courses

        # Freeze first row of each wks
        [gs_api_.freeze_row(sh=sh, wks=sh[i]) for i in range(self.num_wks)]
        # Headers of editable columns: Add blue background
        editable_col_cells = [sh[1].cell('G1'), sh[1].cell('H1'), sh[1].cell('I1'),
                              sh[1].cell('J1'), sh[1].cell('K1'), sh[1].cell('L1'), sh[2].cell('E1'),
                              sh[4].cell('G1'), sh[4].cell('H1'), sh[4].cell('I1'),
                              sh[4].cell('J1'), sh[4].cell('K1'), sh[4].cell('L1'), sh[5].cell('E1')]
        for cell in editable_col_cells:
            cell.color = (207/255, 226/255, 243/255, 1.0)
        tutors_range = sh[6].get_values('A1', 'O1', returnas='range')
        for cell in tutors_range[0]:
            cell.color = (207/255, 226/255, 243/255, 1.0)

        # All Headers: Set Bold
        # Current Term
        [cell.set_text_format('bold', True) for cell in sh[0].get_values('A1', 'Q1', returnas='range')[0]]
        [cell.set_text_format('bold', True) for cell in sh[1].get_values('A1', 'P1', returnas='range')[0]]
        [cell.set_text_format('bold', True) for cell in sh[2].get_values('A1', 'G1', returnas='range')[0]]
        # Previous Term
        [cell.set_text_format('bold', True) for cell in sh[3].get_values('A1', 'Q1', returnas='range')[0]]
        [cell.set_text_format('bold', True) for cell in sh[4].get_values('A1', 'P1', returnas='range')[0]]
        [cell.set_text_format('bold', True) for cell in sh[5].get_values('A1', 'G1', returnas='range')[0]]
        # Tutors & Archive
        [cell.set_text_format('bold', True) for cell in sh[6].get_values('A1', 'O1', returnas='range')[0]]
        [cell.set_text_format('bold', True) for cell in sh[7].get_values('A1', 'G1', returnas='range')[0]]
        [cell.set_text_format('bold', True) for cell in sh[8].get_values('A1', 'F1', returnas='range')[0]]

        # Format Status Column
        gs_api_.format_status_col(sh=sh, wks=sh[0], shape=shapes[0], col_idx=17, stat_arr=self.status_arr)
        gs_api_.format_status_col(sh=sh, wks=sh[3], shape=shapes[3], col_idx=17, stat_arr=self.status_arr)


    def setup_term_formulas(self, wks, term):
        # Demand
        wks.cell('B1').formula = 'ArrayFormula(IF(ROW(A:A)=1,"Demand", VLOOKUP(A1:A, ' + f"'Courses {term[2]}'" + '!$A:$D, 4, FALSE)))'
        # Previous Response
        wks.cell('H1').formula = 'ArrayFormula(IF(ROW(C:C)=1,"Previous Response",IF(ISBLANK(G1:G), "", ' \
                                 'VLOOKUP(G1:G, ' + f"'Professors {term[2]}'" + '!$A:$F, 6, False))))'
        # # Tutors
        wks.cell('J1').formula = f'ArrayFormula(IF(ROW(A:A)=1,"# Tutors", IF(ISBLANK(A1:A), "", COUNTIFS(' \
            f'Tutors!E:E, "{self.school_config.NICE_NAME}", Tutors!L:L, "*"&C1:C&D1:D&"*", Tutors!I:I, "TRUE", Tutors!J:J,"YES"))))'
        # Ranking
        wks.cell('K1').formula = 'ArrayFormula(IF(ROW(A:A)=1,"Ranking", IF(ISBLANK(A1:A), "", B1:B+(I1:I/100))))'
        # Course Status: color coded professor info
        self.status_arr = stat = ['No', 'Sent for different course', 'Match Error', 'Awaiting Response', 'Yes']
        wks.cell('Q1').formula = f'ArrayFormula(IF(ROW(A:A)=1,"Status", IF(ISBLANK(A1:A), "", ' \
            f'IFERROR(IF((O1:O="[]") + (VLOOKUP(G1:G, ' + f"'Professors {term[2]}'" + f'!$A:$N, 14, False) = "") > 0, "{stat[2]}", ' \
            f'IFERROR(IFS(VLOOKUP(G1:G, ' + f"'Professors {term[2]}'" + f'!$A:$N, 9, False)="No", "{stat[0]}",' \
            f'VLOOKUP(G1:G, ' + f"'Professors {term[2]}'" + f'!$A:$N, 9, False)="Yes", "{stat[4]}", ' \
            f'VLOOKUP(G1:G, ' + f"'Professors {term[2]}'" + f'!$A:$N, 8, False)="No", "{stat[0]}", ' \
            f'VLOOKUP(G1:G, ' + f"'Professors {term[2]}'" + f'!$A:$N, 8, False)="Yes", "{stat[4]}", ' \
            f'VLOOKUP(G1:G, ' + f"'Professors {term[2]}'" + f'!$A:$N, 6, False)="No", "{stat[0]}", ' \
            f'VLOOKUP(G1:G, ' + f"'Professors {term[2]}'" + f'!$A:$N, 6, False)="Yes", "{stat[4]}" ), ' \
            f'IF(NE(A1:A, VLOOKUP(G1:G, ' + f"'Professors {term[2]}'" + f'!$A:$N, 14, False)), "{stat[1]}", ' \
            f'IF(VLOOKUP(G1:G, ' + f"'Professors {term[2]}'" + f'!$A:$N, 12, False)="Fall 19","{stat[3]}",)))),"{stat[2]}" ))))'

    def setup_professor_formulas(self, wks, term):
        # Previous Response
        # To Send
        wks.cell('M1').formula = 'ArrayFormula(IF(ROW(A:A)=1,"To Send",IF(ISBLANK(A:A),"", ' \
                                 'IF(RegExMatch(E1:E,"@"), ' \
                                 'IFERROR(' \
                                 'IFS(L1:L="Fall 19", "No",F1:F="No", "No",H1:H="No", "No",I1:I="No", "No"),' \
                                 ' "Yes"), "No"))))'

    def setup_course_formulas(self, wks, term):
        # Demand out
        wks.cell('D1').formula = 'ArrayFormula(IF(ROW(F:F)=1,"Demand Out", IFS(' \
                                 'IF((F1:F), F1:F+E1:E, 3+E1:E)>5, 5, ' \
                                 'IF((F1:F), F1:F+E1:E, 3+E1:E)<0, 0, ' \
                                 'IF((F1:F), F1:F+E1:E, 3+E1:E)<5, IF((F1:F), F1:F+E1:E, 3+E1:E))))'
        # Demand in
        wks.cell('F1').formula = 'ArrayFormula(IF(ROW(E:E)=1,"Archive Demand In", ' \
                                 'IFERROR(VLOOKUP(A1:A, '+"'Spring 19'"+'!$A:$B, 2, FALSE), )))'
        # # Tutors
        wks.cell('G1').formula = f'ArrayFormula(IF(ROW(A:A)=1,"# Tutors", IF(ISBLANK(A1:A), "", ' \
                                 f'COUNTIFS(Tutors!E:E, "{self.school_config.NICE_NAME}", Tutors!L:L, "*"&SUBSTITUTE(A1:A," ","")&"*", ' \
                                 f'Tutors!I:I, "TRUE", Tutors!J:J, "YES"))))'
    def setup_arch_course_formulas(self, wks, term):
        # # Tutors
        wks.cell('F1').formula = f'ArrayFormula(IF(ROW(A:A)=1,"# Tutors", IF(ISBLANK(A1:A), "", ' \
                                 f'COUNTIFS(Tutors!E:E, "{self.school_config.NICE_NAME}", Tutors!L:L, "*"&SUBSTITUTE(A1:A," ","")&"*", ' \
                                 f'Tutors!I:I, "TRUE", Tutors!J:J, "YES"))))'




class GoogleSheetsUploadStudentOrgs(GoogleSheetsParent):
    def __init__(self, args):
        GoogleSheetsParent.__init__(self, args)


    def run(self):
        # Create a new sheet in folder
        sh = self._connect_google_sheet(sheet_name_in=f'{self.school_config.NICE_NAME} Student Orgs')

        gs_df = self._load(file_name_key='student_orgs')
        shape = gs_df.shape
        if self.reset_gs:
            wks = sh.add_worksheet(self.files['student_orgs'][1], rows=shape[0] + 10, cols=shape[1], index=0)
            sh.del_worksheet(sh.worksheet_by_title('Sheet1'))
        else:
            wks = sh[0]

        # Upload the data
        if self.args.data:
            wks.set_dataframe(gs_df, (1, 1))
            wks.replace('NaN', '')


        if self.args.format:
            #self.format_sheet(sh, shape)
            [cell.set_text_format('bold', True) for cell in sh[0].get_values('A1', 'C1', returnas='range')[0]]


class GoogleSheetsDownload:
    def __init__(self, args):
        self.args = args

    def run(self):
        """ Pulls Data From GS Previous Term and saves to proper csv format

        """
        config = cfg[self.args.school.upper()]
        sheet_name = f'{config.NICE_NAME} Class List'  # f'{config.NICE_NAME} Course List'
        gc = pygsheets.authorize(service_file='core/credentials/penji_dev_key.json')
        try:
            sh = gc.open(sheet_name)
            logger.info(f'Found {sheet_name} in google drive, downloading sheet')
        except pygsheets.exceptions.SpreadsheetNotFound:
            logger.error(f'Could not find {sheet_name} in google drive')
            return
        self.download_tutor_csv(sh)
        df = self.download_prev_term_csv(sh)
        df.rename(columns={'Class': 'Course Code'}, inplace=True)
        print(df.head())


        # prof_df = self.cu_prof_setup(df)
        #
        # course_df = self.cu_courses_setup(df)
        #
        # self.add_prev_term_to_archive()
        #
        # gs_utils.save(gs_df=prof_df, term=cfg.GENERAL.PREV_TERM, school=self.args.school,
        #               sheet_idx=2, test=self.args.test)
        # gs_utils.save(gs_df=course_df, term=cfg.GENERAL.PREV_TERM, school=self.args.school,
        #               sheet_idx=3, test=self.args.test)

        self.add_prev_term_to_archive(df)


    def download_tutor_csv(self, sh):
        wks = sh.worksheet_by_title("Tutors")
        tutors_df = wks.get_as_df()
        tutors_df = tutors_df[tutors_df['Date Added'] != '']
        tutors_df = tutors_df.drop('', axis=1)

        self._save(gs_df=tutors_df, file_name=f'data/{self.args.school}/archive/gs_archive_{self.args.school}_6.csv')



    def download_prev_term_csv(self, sh):
        wks = sh.worksheet_by_title("Spring '19")
        df = wks.get_as_df()
        df = df[df['Course'] != '']
        df = df.drop('', axis=1)
        gs_utils.save(gs_df=df, term=cfg.GENERAL.PREV_TERM, school=self.args.school,
                      sheet_idx=0, test=self.args.test)
        return df


    def add_prev_term_to_archive(self, term_df):
        file_names = (f'data/{self.args.school}/archive/gs_archive_{self.args.school}_7.csv',
                      f'data/{self.args.school}/archive/gs_archive_{self.args.school}_8.csv')
        arch_prof_df, arch_course_df = self.load_archive_files(file_names)

        ca_data = {key: [] for key in cfg.GENERAL.WKS_COLUMNS['Course Archive']}
        pr_data = {key: [] for key in cfg.GENERAL.WKS_COLUMNS['Professor Archive']}


        for idx, col in term_df.iterrows():
            if term_df['Course Code'][idx] not in ca_data['Course Code']:
                ca_data['Course Code'].append(term_df['Course Code'][idx])
                ca_data['Name'].append(term_df['Name'][idx])
                ca_data['Title'].append(term_df['Title'][idx])
                ca_data['Previous Demand'].append(term_df['Demand'][idx])
                ca_data['Term Last Updated'].append('Spring 19')

            if term_df['Professor'][idx] not in pr_data['Full Name']:
                pr_data['Full Name'].append(term_df['Professor'][idx])
                pr_data['First Name'].append(term_df['First Name'][idx])
                pr_data['Last Name'].append(term_df['Last Name'][idx])
                # Find Previous Response : Previous response, Pre-approval status, LHP
                prev_response = (' ', term_df['Previous Response'][idx], term_df['Pre-approval status'][idx],
                                 term_df['LHP Response (yes/no)'][idx])
                cons_response = [resp for resp in prev_response if resp != '']
                pr_data['Previous Response'].append(cons_response[-1])
                pr_data['Term Last Sent'].append('Spring 19')



        num_rows = len(ca_data['Course Code'])
        gs_ca_data = {key: ([None] * num_rows if lst == [] else lst) for key, lst in ca_data.items()}
        courses_df = pd.DataFrame(data=gs_ca_data, columns=cfg.GENERAL.WKS_COLUMNS['Course Archive'])

        num_rows_2 = len(pr_data['Full Name'])
        gs_pr_data = {key: ([None] * num_rows_2 if lst == [] else lst) for key, lst in pr_data.items()}
        prof_df = pd.DataFrame(data=gs_pr_data, columns=cfg.GENERAL.WKS_COLUMNS['Professor Archive'])


        prof_df = prof_df[prof_df['Previous Response'] != ' ']
        print(prof_df['Previous Response'])

        #self._save(gs_df=prof_df, file_name=file_names[0])
        #self._save(gs_df=courses_df, file_name=file_names[1])

        return


    def process_cur_term_csv(self, row):
        # Term Sheet: Demand Column
        demand = 3
        try:
            for ir in self.df_arr[1].itertuples():
                if ir[0] == row['Course Code']:
                    demand = ir[2]
                    break
        except:
            logger.warn(f'Empty Previous Term CSV')
        ranking = demand + (row['# Students'] / 100)

        # Term Sheet: Professor Row Reference #
        row_references = []
        if isinstance(row['Professor'], str):
            prof_names_in = row['Professor'].split(', ')
            for ir in self.df_arr[2].itertuples():
                [row_references.append(ir[0]+2) for name in prof_names_in if ir[1] == name]
            assert len(prof_names_in) == len(row_references), \
                f'ERROR: prof names {prof_names_in} != {row_references} row references'

        row['Demand'], row['Ranking'], row['Professor Row #'] = demand, ranking, row_references
        return row


    def process_prof_info(self, row):
        # Professor Sheet: All Courses
        # Don't select a class if no email available
        all_courses = []  # (None, None, 0)  # Course Code, Course Row #, Ranking
        best_course = (None, None, 0)
        if '@' in str(row['Email']):
            prof_name = row['Full Name']
            for ir in self.df_arr[0].itertuples():
                if ir[15] and str(row.name+2) in str(ir[15])[1:-1].split(', '):
                    all_courses.append((ir[1], ir[0]+2, ir[11]))

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



    def load_archive_files(self, file_names):

        pr_df = pd.read_csv(file_names[0]) if os.path.exists(file_names[0]) \
            else pd.DataFrame(columns=cfg.GENERAL.WKS_COLUMNS['Professor Archive'])

        ca_df = pd.read_csv(file_names[1]) if os.path.exists(file_names[1]) \
            else pd.DataFrame(columns=cfg.GENERAL.WKS_COLUMNS['Course Archive'])

        return pr_df, ca_df

    def _save(self, gs_df, file_name):
        gs_df.to_csv(index=False, path_or_buf=file_name)




if __name__ == '__main__':
    # Parser for command input
    parser = argparse.ArgumentParser('Google Sheets Automation Runner')
    # General PenjiDev Args
    parser.add_argument('-user', help='Enter user from config', default='PAIK')
    parser.add_argument('-school', help='Enter a school name', required=True)
    parser.add_argument('-term', help='Enter a term', default='fall19')
    parser.add_argument('-test', action='store_true', help='Test Runs')
    parser.add_argument('-ns', action='store_true', help='No Saving')
    parser.add_argument('-log', help='Enter logger level: debug, info, warn, error, none', default='info', type=str)
    # General Variable Help messages
    parser.add_argument('-pull_arch', action='store_true', help='Pull Data From Archive to Term Sheets')
    parser.add_argument('-prep', action='store_true', help='Prep CSVs for upload')
    parser.add_argument('-upload', action='store_true', help='Upload to Google Sheets')

    parser.add_argument('-upload_so', action='store_true', help='Upload to Student Orgs to Google Sheets')


    parser.add_argument('-reset', action='store_true', help='Reset Google Drive Spreadsheet')
    # Special Args
    parser.add_argument('-formulas', action='store_true', help='Add Formulas')
    parser.add_argument('-data', action='store_true', help='Add Data')
    parser.add_argument('-format', action='store_true', help='Add Formatting')
    # Add Saving Arg
    parser_args = parser.parse_args()
    parser_args.save = not parser_args.ns

    modes = [(parser_args.prep, GoogleSheetsPrep), (parser_args.upload, GoogleSheetsUpload)]
    utils.setup_data_dir(args=parser_args)
    if parser_args.pull_arch:
        utils.setup_logger(parser_args, 'gs_pull_arch')
        GoogleSheetsPullFromArchive(args=parser_args).run()
    elif parser_args.prep:
        utils.setup_logger(parser_args, 'gs_prep')
        GoogleSheetsPrep(args=parser_args).run()
    elif parser_args.upload:
        utils.setup_logger(parser_args, 'gs_upload')
        GoogleSheetsUpload(args=parser_args).run()
    elif parser_args.upload_so:
        utils.setup_logger(parser_args, 'gs_upload')
        GoogleSheetsUploadStudentOrgs(args=parser_args).run()
    else:
        logger.error(f'No running mode functionality specified')
