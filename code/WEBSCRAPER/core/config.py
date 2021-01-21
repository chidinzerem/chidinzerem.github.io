#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------
# Penji OpDev Fall 2019
# Configuration file
# Author: Cory Paik
# ------------------------

# -------------------------------------
# Consumers can get config by:
#   from core.config import cfg
#
# Add in your profiles (see below)
# python run.py -user <your name>
# -------------------------------------


from easydict import EasyDict as edict

__C                             = edict()
cfg                             = __C

# --------------------------------------
# User Profiles
# --------------------------------------
## Cory Paik
__C.PAIK                        = edict()
__C.PAIK.MACOS_DRIVER           = '/Users/corypaik/JetBrains/PycharmProjects/penjiDev/venv/bin/chromedriver'
__C.PAIK.WIND_DRIVER            = 'C:/Users/Cory Paik/JetBrains/PycharmProjects/penjiDev/venv/Scripts/chromedriver.exe'
## Chidi Nzerem
__C.NZEREM                      = edict()
__C.NZEREM.MACOS_DRIVER         = '/Users/chidinzerem/PycharmProjects/penjiDev/venv/bin/chromedriver'
__C.NZEREM.WIND_DRIVER          = None
## Ben Holmquist
__C.HOLMQUIST                   = edict()
__C.HOLMQUIST.MACOS_DRIVER      = None
__C.HOLMQUIST.WIND_DRIVER       = None
# ...
# Add your user profile here
# ...

# --------------------------------------
# School Configurations
# --------------------------------------
## Template
__C.TEMPLATE                    = edict()
__C.TEMPLATE.START_URL          = 'https://www.google.com/'
__C.TEMPLATE.UPDATE_SUBJECTS    = None
__C.TEMPLATE.CLASS_TYPES        = None
__C.TEMPLATE.EMAIL              = edict()
__C.TEMPLATE.EMAIL.START_URL    = 'https://www.google.com/'
__C.TEMPLATE.FOLDER_ID          = '<>'
__C.TEMPLATE.NICE_NAME          = 'Template'
## CU Boulder
__C.CUBOULDER                   = edict()
__C.CUBOULDER.START_URL         = 'https://classes.colorado.edu'
__C.CUBOULDER.UPDATE_SUBJECTS   = None
__C.CUBOULDER.CLASS_TYPES       = ('LEC', 'SEM')
__C.CUBOULDER.EMAIL             = edict()
__C.CUBOULDER.EMAIL.START_URL   = 'https://www.colorado.edu/search'
__C.CUBOULDER.FOLDER_ID         = '1VrBdnju5dWj-bKGraXGw3LujnaK46yvY'
__C.CUBOULDER.NICE_NAME         = 'CU Boulder'
__C.CUBOULDER.ORGS              = edict()
__C.CUBOULDER.ORGS.START_URL    = 'http://buffconnectdirectory.orgsync.com/'
## USC
__C.USC                         = edict()
__C.USC.START_URL               = 'https://classes.usc.edu/term-20193/'
__C.USC.UPDATE_SUBJECTS         = None
__C.USC.CLASS_TYPES             = ('Lecture', 'Seminar')
__C.USC.EMAIL                   = edict()
__C.USC.EMAIL.START_URL         = 'https://uscdirectory.usc.edu/web/directory/faculty-staff/'
__C.USC.FOLDER_ID               = '1y009T1cHgMQ357u2DJ1W1703iF_--I0c'
__C.USC.NICE_NAME               = 'USC'
__C.USC.ORGS                    = edict()
__C.USC.ORGS.START_URL          = 'https://usc.campuslabs.com/engage/organizations'
## UCLA
__C.UCLA                        = edict()
__C.UCLA.START_URL              = 'https://sa.ucla.edu/ro/public/soc'
__C.UCLA.UPDATE_SUBJECTS        = None
__C.UCLA.CLASS_TYPES            = ('Lec', 'Sem')
__C.UCLA.EMAIL                  = edict()
__C.UCLA.EMAIL.START_URL        = ''
__C.UCLA.FOLDER_ID              = ''
__C.UCLA.NICE_NAME              = 'UCLA'

## Berkeley
__C.BERKELEY                    = edict()
#__C.BERKELEY.START_URL          = 'https://classes.berkeley.edu/search/site/?f%5B0%5D=im_field_term_name%3A851&f%5B1%5D=ts_course_level%3Alow&f%5B2%5D=ts_course_level%3Aup'
__C.BERKELEY.START_URL          = 'https://classes.berkeley.edu/search/site/?f%5B0%5D=im_field_term_name%3A851&f%5B1%5D=ts_course_level%3Alow&f%5B2%5D=ts_course_level%3Aup'
__C.BERKELEY.UPDATE_SUBJECTS    = None
__C.BERKELEY.CLASS_TYPES        = ('LEC', 'SEM')
__C.BERKELEY.EMAIL              = edict()
__C.BERKELEY.EMAIL.START_URL    = ''
__C.BERKELEY.FOLDER_ID          = '114imz0pWu2iUswyTZIMjLYqFcEqV3Lgw'
__C.BERKELEY.NICE_NAME          = 'UC Berkeley'
__C.BERKELEY.ORGS               = edict()
__C.BERKELEY.ORGS.START_URL     = 'https://callink.berkeley.edu/organizations'
## UC Davis
__C.UCDAVIS                     = edict()
__C.UCDAVIS.START_URL           = 'https://registrar-apps.ucdavis.edu/courses/search/index.cfm'
__C.UCDAVIS.UPDATE_SUBJECTS     = None
__C.UCDAVIS.CLASS_TYPES         = ('Lecture', 'Seminar')
__C.UCDAVIS.EMAIL               = edict()
__C.UCDAVIS.EMAIL.START_URL     = ''
__C.UCDAVIS.FOLDER_ID           = '1CWOLF2VCqt-Kka2BglrwD0VZ4oXtU9AX'
__C.UCDAVIS.NICE_NAME           = 'UC Davis'
__C.UCDAVIS.ORGS                = edict()
__C.UCDAVIS.ORGS.START_URL      = 'https://aggielife.ucdavis.edu/organizations'
## CalPoly SLO
__C.CALPOLY                     = edict()
__C.CALPOLY.START_URL           = 'https://pass.calpoly.edu/main.html'
__C.CALPOLY.UPDATE_SUBJECTS     = None
__C.CALPOLY.CLASS_TYPES         = ('LEC', 'SEM')
__C.CALPOLY.IGNORE_CLASS_TYPES  = ('IND', 'LAB', 'ACT', 'DIS')
__C.CALPOLY.EMAIL               = edict()
__C.CALPOLY.EMAIL.START_URL     = ''
__C.CALPOLY.FOLDER_ID           = '1mszzoStrgWpwS_-WQspT0cx11TJlgCpF'
__C.CALPOLY.NICE_NAME           = 'Cal Poly'
## MICH
__C.MICH                        = edict()
__C.MICH.START_URL              = 'https://www.lsa.umich.edu/cg/default.aspx'
__C.MICH.UPDATE_SUBJECTS        = None
__C.MICH.CLASS_TYPES            = ('Lecture', 'Seminar')
__C.MICH.EMAIL                  = edict()
__C.MICH.EMAIL.START_URL        = 'https://mcommunity.umich.edu/#advanced_search:'
__C.MICH.FOLDER_ID              = '1apxlrTdmlyHxM3WlPXNByFLhD8zVS3EB'
__C.MICH.NICE_NAME              = 'Michigan'
## Texas A&M
__C.TEXASAM                     = edict()
__C.TEXASAM.START_URL           = 'https://compass-ssb.tamu.edu/pls/PROD/bwckschd.p_disp_dyn_sched'
__C.TEXASAM.UPDATE_SUBJECTS     = None
__C.TEXASAM.CLASS_TYPES         = ('Lecture', 'Seminar')
__C.TEXASAM.IGNORE_CLASS_TYPES  = ('Examination', 'Practicum', 'Independent Study', 'Research', 'Laboratory', 'Recitation', 'Internship')
__C.TEXASAM.EMAIL               = edict()
__C.TEXASAM.EMAIL.START_URL     = 'https://services.tamu.edu/directory-search/#adv-search'
__C.TEXASAM.FOLDER_ID           = '1CIxmHt6_l5T6Ch6gAcninjmO7QwpaKM6'
__C.TEXASAM.NICE_NAME           = 'Texas A&M'
__C.TEXASAM.ORGS                = edict()
__C.TEXASAM.ORGS.START_URL      = 'https://stuactonline.tamu.edu/app/search/index/index/search/name?q='
## University of Illinois
__C.ILLINOIS                    = edict()
__C.ILLINOIS.START_URL          = 'https://courses.illinois.edu/search/form'
__C.ILLINOIS.UPDATE_SUBJECTS    = None
__C.ILLINOIS.CLASS_TYPES        = ('Lecture-Discussion', 'Lecture')
__C.ILLINOIS.EMAIL              = edict()
__C.ILLINOIS.EMAIL.START_URL    = 'https://directory.illinois.edu/search'
__C.ILLINOIS.FOLDER_ID          = '1AeGNB7pPI1hj7VJEcGMShnRLzUUs55D9'
__C.ILLINOIS.NICE_NAME          = 'University of Illinois'
__C.ILLINOIS.ORGS               = edict()
__C.ILLINOIS.ORGS.START_URL     = 'https://illinois.campuslabs.com/engage/organizations'
# NYU
__C.NYU                         = edict()
__C.NYU.START_URL               = 'https://m.albert.nyu.edu/app/catalog/classSearch/1198'
__C.NYU.UPDATE_SUBJECTS         = None
__C.NYU.CLASS_TYPES             = ('LEC', 'SEM')
__C.NYU.EMAIL                   = edict()
__C.NYU.EMAIL.START_URL         = 'https://www.nyu.edu/search.directory.html?st=people'
__C.NYU.FOLDER_ID               = '1MZPIibpdmdpgoXNNNXgE_Z-lN8iZvDPs'
__C.NYU.NICE_NAME               = 'NYU'







# ...
# Add additional schools here
# ...

__C.GENERAL                     = edict()

__C.GENERAL.FALL19              = ('Fall 19', 'fall19', 'F19')
__C.GENERAL.FALL19_PREV         = ('Spring 19', 'spring19', 'S19')


__C.GENERAL.SPRING19            = ('Spring 19', 'spring19', 'S19')
__C.GENERAL.CUR_TERM            = ('Fall 19', 'fall19', 'F19')
__C.GENERAL.PREV_TERM           = ('Spring 19', 'spring19', 'S19')
__C.GENERAL.ARCHIVE             = ('Archive', 'archive', 'ARCH')
__C.GENERAL.WKS_NAMES           = (__C.GENERAL.CUR_TERM[0], __C.GENERAL.PREV_TERM[0],
                                   f'Professors {__C.GENERAL.CUR_TERM[2]}', f'Courses {__C.GENERAL.CUR_TERM[2]}',
                                   f'Professors {__C.GENERAL.PREV_TERM[2]}', f'Courses {__C.GENERAL.PREV_TERM[2]}',
                                   'Tutors', 'Professors Archive', 'Courses Archive')
__C.GENERAL.LOGGER_LEVELS       = {'DEBUG': 10, 'INFO' : 20, 'WARN' : 30, 'ERROR' : 40, 'NONE' : 50}
# Shared Course List Template Structure
__C.GENERAL.CL_COLUMNS          = {
    # For updating reference
    'Reference_Number'          : None,
    # In run()
    'Department_Abbreviation'   : None,
    'Department_Name'           : None,
    # In process_subject()
    'Course_Number'             : None,
    'Course_Name'               : None,
    # In process_course()
    'Section_Type'              : None,
    'Section_Number'            : None,
    'Section_Days'              : None,
    'Section_Time'              : None,
    'Section_Professor'         : None,
    # In process_section_details()
    'Number_Students'           : None,
    'ClassRoom'                 : None,
    'Email'                     : None,
}
# __C.GENERAL.CL_COLUMNS          = {
#     'Course Code',
#     'Demand',
#     'Abbreviation', #'Department_Abbreviation'
#     'Course', # 'Course_Number'
#     'Name', # 'Department_Name'
#     'Title', # 'Course_Name'
#     'Professor', # 'Section_Professor'
#     '# Students', # 'Number_Students'
#     'Time', # 'Section_Time'
#     'Days', # 'Section_Days'
#     'Classroom', # 'ClassRoom'
#     'Professor Row #',
#     'Section Reference #', #'Reference_Number'
#     'Status'
# }
__C.GENERAL.WKS_COLUMNS         = {
    'Term' : (
        'Course Code',
        'Demand',
        'Abbreviation', #'Department_Abbreviation'
        'Course', # 'Course_Number'
        'Name', # 'Department_Name'
        'Title', # 'Course_Name'
        'Professor', # 'Section_Professor'
        'Previous Response',
        '# Students', # 'Number_Students'
        '# Tutors',
        'Ranking',
        'Time', # 'Section_Time'
        'Days', # 'Section_Days'
        'Classroom', # 'ClassRoom'
        'Professor Row #',
        'Section Reference #', #'Reference_Number'
        'Status'),

    'Professors' : (
        'Full Name',
        'Salutation',
        'First Name',
        'Last Name',
        'Email',
        f'Previous Response {cfg.GENERAL.PREV_TERM[2]}',
        'Signoff (Name, Date)',
        'Pre-Approval Status',
        'LHP Response (yes/no)',
        'Planned Date',
        'Notes',
        'Term Last Sent',
        'To Send',
        'Desired Course Code',
        'Desired Course Row #',
        'All Courses'
    ),

    'Courses'    : (
        'Course Code',
        'Name',
        'Title',
        f'{cfg.GENERAL.CUR_TERM[2]} Demand Out',
        'Demand Adjustments',
        f'{cfg.GENERAL.PREV_TERM[2]} Demand In',
        '# Tutors'),

    'Tutors'     : (
        'Date Added',
        'Email',
        'First Name',
        'Last Name',
        'School',
        'Year',
        'User Type',
        'Pal Meeting?',
        'Allowed to Teach',
        'Active?',
        'Active Updated At',
        'Classes Allowed to Teach',
        'Quals',
        'Channel',
        'Year when Added'),

    'Professor Archive' : (
        'Full Name',
        'Salutation',
        'First Name',
        'Last Name',
        'Email',
        f'Previous Response',
        'Term Last Sent'),

    'Course Archive'    : (
        'Course Code',
        'Name',
        'Title',
        'Previous Demand',
        'Term Last Updated',
        '# Tutors'),
}


wks_columns = {
    'Term' : (
        'Course Code',
        'Demand',
        'Abbreviation', #'Department_Abbreviation'
        'Course', # 'Course_Number'
        'Name', # 'Department_Name'
        'Title', # 'Course_Name'
        'Professor', # 'Section_Professor'
        'Previous Response',
        '# Students', # 'Number_Students'
        '# Tutors',
        'Ranking',
        'Time', # 'Section_Time'
        'Days', # 'Section_Days'
        'Classroom', # 'ClassRoom'
        'Professor Row #',
        'Section Reference #', #'Reference_Number'
        'Status'),

    'Professors' : (
        'Full Name',
        'Salutation',
        'First Name',
        'Last Name',
        'Email',
        f'Previous Response {cfg.GENERAL.PREV_TERM[2]}',
        'Signoff (Name, Date)',
        'Pre-Approval Status',
        'LHP Response (yes/no)',
        'Planned Date',
        'Notes',
        'Term Last Sent',
        'To Send',
        'Desired Course Code',
        'Desired Course Row #',
        'All Courses'
    ),

    'Courses'    : (
        'Course Code',
        'Name',
        'Title',
        f'{cfg.GENERAL.CUR_TERM[2]} Demand Out',
        'Demand Adjustments',
        f'{cfg.GENERAL.PREV_TERM[2]} Demand In',
        '# Tutors'),

    'Tutors'     : (
        'Date Added',
        'Email',
        'First Name',
        'Last Name',
        'School',
        'Year',
        'User Type',
        'Pal Meeting?',
        'Allowed to Teach',
        'Active?',
        'Active Updated At',
        'Classes Allowed to Teach',
        'Quals',
        'Channel',
        'Year when Added'),

    'Professor Archive' : (
        'Full Name',
        'Salutation',
        'First Name',
        'Last Name',
        'Email',
        f'Previous Response {cfg.GENERAL.PREV_TERM[2]}',
        'Term Last Sent',
    ),

    'Course Archive'    : (
        'Course Code',
        'Name',
        'Title',
        'Previous Demand',
        'Term Last Updated'
        '# Tutors'),
}






