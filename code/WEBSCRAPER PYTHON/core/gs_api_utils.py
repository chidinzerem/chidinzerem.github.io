#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ------------------------
# Penji OpDev Fall 2019
# GS API V4 Utilities
# Author: Cory Paik
# ------------------------

# General
import os
import time
import parse
import tkinter
import numpy as np
import pandas as pd
from core import logger


import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

def freeze_row(sh, wks):
    service = setup_service()

    requests = [{
        'update_sheet_properties': {
            'properties': {
                'sheet_id': wks.id,
                'grid_properties': {'frozen_row_count': 1}
            },
            'fields': 'gridProperties.frozenRowCount'
        }

    }]
    body = {
        'requests': requests
    }
    response = service.spreadsheets() \
        .batchUpdate(spreadsheetId=sh.id, body=body).execute()
    print('{0} cells updated.'.format(len(response.get('replies'))))


def setup_service():
    SCOPES = ['https://www.googleapis.com/auth/drive']
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('core/credentials/token.pickle'):
        with open('core/credentials/token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'core/credentials/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('core/credentials/token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)
    return service

def format_tutor_col(sh, wks, shape, col_idx):
    # Col idx start at 1
    service = setup_service()

    my_range = {
        'sheetId': wks.id,
        'startRowIndex': 1,
        'endRowIndex': shape[0]+10,
        'startColumnIndex': col_idx-1,
        'endColumnIndex': col_idx,
    }
    requests = [{
        'addConditionalFormatRule': {
            'rule': {
                'ranges': [my_range],
                'booleanRule': {
                    'condition': {
                        'type': 'NUMBER_EQ',
                        'values': [{
                            'userEnteredValue':
                                '0'
                        }]
                    },
                    'format': {
                        'backgroundColor': {
                            'red': 244/255,
                            'green': 204/255,
                            'blue': 204/255
                        }
                    }
                }
            },
            'index': 0
        }
    },  {
        'addConditionalFormatRule': {
            'rule': {
                'ranges': [my_range],
                'booleanRule': {
                    'condition': {
                        'type': 'NUMBER_BETWEEN',
                        'values': [{
                            'userEnteredValue':
                                '1'
                        },{
                            'userEnteredValue':
                                '2'
                        }]
                    },
                    'format': {
                        'backgroundColor': {
                            'red': 255 / 255,
                            'green': 242 / 255,
                            'blue': 204 / 255
                        }
                    }
                }
            },
            'index': 0
        }
    },  {
        'addConditionalFormatRule': {
            'rule': {
                'ranges': [my_range],
                'booleanRule': {
                    'condition': {
                        'type': 'NUMBER_GREATER_THAN_EQ',
                        'values': [{
                            'userEnteredValue':
                                '3'
                        }]
                    },
                    'format': {
                        'backgroundColor': {
                            'red': 183 / 255,
                            'green': 225 / 255,
                            'blue': 205 / 255
                        }
                    }
                }
            },
            'index': 0
        }

    }]
    body = {
        'requests': requests
    }
    response = service.spreadsheets() \
        .batchUpdate(spreadsheetId=sh.id, body=body).execute()
    print('{0} cells updated.'.format(len(response.get('replies'))))

def format_status_col(sh, wks, shape, col_idx, stat_arr):
    # Col idx start at 1
    service = setup_service()

    my_range = {
        'sheetId': wks.id,
        'startRowIndex': 1,
        'endRowIndex': shape[0]+10,
        'startColumnIndex': col_idx-1,
        'endColumnIndex': col_idx,
    }
    requests = [
        { # - 0 RED: No
        'addConditionalFormatRule': {
            'rule': {
                'ranges': [my_range],
                'booleanRule': {
                    'condition': {
                        'type': 'TEXT_EQ',
                        'values': [{
                            'userEnteredValue':
                                stat_arr[0]
                        }]
                    },
                    'format': {
                        'backgroundColor': {
                            'red': 244/255,
                            'green': 204/255,
                            'blue': 204/255
                        }
                    }
                }
            },
            'index': 0
        }
    }, { # - 1 GREY: Sent for a different class
        'addConditionalFormatRule': {
            'rule': {
                'ranges': [my_range],
                'booleanRule': {
                    'condition': {
                        'type': 'TEXT_EQ',
                        'values': [{
                            'userEnteredValue':
                                stat_arr[1]
                        }]
                    },
                    'format': {
                        'backgroundColor': {
                            'red': 217 / 255,
                            'green': 217 / 255,
                            'blue': 217 / 255
                        }
                    }
                }
            },
            'index': 0
        }
    },  { # - 2 YELLOW: Couldn't find prof contact
        'addConditionalFormatRule': {
            'rule': {
                'ranges': [my_range],
                'booleanRule': {
                    'condition': {
                        'type': 'TEXT_EQ',
                        'values': [{
                            'userEnteredValue':
                                stat_arr[2]
                        }]
                    },
                    'format': {
                        'backgroundColor': {
                            'red': 255 / 255,
                            'green': 242 / 255,
                            'blue': 204 / 255
                        }
                    }
                }
            },
            'index': 0
        }
    },  {  #  - 3 BLUE :  Awaiting response
        'addConditionalFormatRule': {
            'rule': {
                'ranges': [my_range],
                'booleanRule': {
                    'condition': {
                        'type': 'TEXT_EQ',
                        'values': [{
                            'userEnteredValue':
                                stat_arr[3]
                        }]
                    },
                    'format': {
                        'backgroundColor': {
                            'red': 201 / 255,
                            'green': 218 / 255,
                            'blue': 248 / 255
                        }
                    }
                }
            },
            'index': 0
        }
    },  { # - 4 GREEN:  Yes
        'addConditionalFormatRule': {
            'rule': {
                'ranges': [my_range],
                'booleanRule': {
                    'condition': {
                        'type': 'TEXT_EQ',
                        'values': [{
                            'userEnteredValue':
                                stat_arr[4]
                        }]
                    },
                    'format': {
                        'backgroundColor': {
                            'red': 183 / 255,
                            'green': 225 / 255,
                            'blue': 205 / 255
                        }
                    }
                }
            },
            'index': 0
        }
    }]
    requests_old = [
        {  # - 0 RED: No
            'addConditionalFormatRule': {
                'rule': {
                    'ranges': [my_range],
                    'booleanRule': {
                        'condition': {
                            'type': 'NUMBER_EQ',
                            'values': [{
                                'userEnteredValue':
                                    '0'
                            }]
                        },
                        'format': {
                            'backgroundColor': {
                                'red': 244 / 255,
                                'green': 204 / 255,
                                'blue': 204 / 255
                            }
                        }
                    }
                },
                'index': 0
            }
        }, {  # - 1 GREY: Sent for a different class
            'addConditionalFormatRule': {
                'rule': {
                    'ranges': [my_range],
                    'booleanRule': {
                        'condition': {
                            'type': 'NUMBER_EQ',
                            'values': [{
                                'userEnteredValue':
                                    '1'
                            }]
                        },
                        'format': {
                            'backgroundColor': {
                                'red': 217 / 255,
                                'green': 217 / 255,
                                'blue': 217 / 255
                            }
                        }
                    }
                },
                'index': 0
            }
        }, {  # - 2 YELLOW: Couldn't find prof contact
            'addConditionalFormatRule': {
                'rule': {
                    'ranges': [my_range],
                    'booleanRule': {
                        'condition': {
                            'type': 'NUMBER_EQ',
                            'values': [{
                                'userEnteredValue':
                                    '2'
                            }]
                        },
                        'format': {
                            'backgroundColor': {
                                'red': 255 / 255,
                                'green': 242 / 255,
                                'blue': 204 / 255
                            }
                        }
                    }
                },
                'index': 0
            }
        }, {  # - 3 BLUE :  Awaiting response
            'addConditionalFormatRule': {
                'rule': {
                    'ranges': [my_range],
                    'booleanRule': {
                        'condition': {
                            'type': 'NUMBER_EQ',
                            'values': [{
                                'userEnteredValue':
                                    '3'
                            }]
                        },
                        'format': {
                            'backgroundColor': {
                                'red': 201 / 255,
                                'green': 218 / 255,
                                'blue': 248 / 255
                            }
                        }
                    }
                },
                'index': 0
            }
        }, {  # - 4 GREEN:  Yes
            'addConditionalFormatRule': {
                'rule': {
                    'ranges': [my_range],
                    'booleanRule': {
                        'condition': {
                            'type': 'NUMBER_EQ',
                            'values': [{
                                'userEnteredValue':
                                    '4'
                            }]
                        },
                        'format': {
                            'backgroundColor': {
                                'red': 183 / 255,
                                'green': 225 / 255,
                                'blue': 205 / 255
                            }
                        }
                    }
                },
                'index': 0
            }
        }]
    body = {
        'requests': requests
    }
    response = service.spreadsheets() \
        .batchUpdate(spreadsheetId=sh.id, body=body).execute()
    print('{0} cells updated.'.format(len(response.get('replies'))))