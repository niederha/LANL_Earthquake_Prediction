""" This file contains meta data and informations related to the train and test files from Kaggle"""
from enum import IntEnum, unique


EXPECTED_FILE_EXTENSION = '.csv'
DATA_DIMENSION = 2
COLUMN_NAME = ['acoustic_data', 'time_to_failure']


@unique
class Column(IntEnum):
    DATA = 0
    TTF = 1
