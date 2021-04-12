""" Manejo de autenticación con Google

spreadsheets para manipulación de hojas de calculo
"""
from __future__ import print_function
import os
from googleapiclient.discovery import build
from google.oauth2 import service_account
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials


SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
]

credentials = service_account.Credentials.from_service_account_file('credentials.json', scopes=SCOPES)
spreadsheet_service = build('sheets', 'v4', credentials=credentials)
