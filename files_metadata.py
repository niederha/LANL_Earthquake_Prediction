""" This file contains meta data and informations related to the train and test files from Kaggle"""
from enum import IntEnum, unique

# Where to fetch metadata
META_DATA_FILE = "Data\\eq_meta_data.csv"
DATA_TO_TRACK = ['size', 'max', 'min', 'mean', 'stdev', 'span']

EXPECTED_FILE_EXTENSION = '.csv'                            # Extension that is to be used by all data files.
DATA_DIMENSION = 2                                          # Number of dimensions of each data point.
COLUMN_NAME = ['acoustic_data', 'time_to_failure']          # Column name in the original raw file
SPLIT_FILE_COLUMN_NAME = ['original_index'] + COLUMN_NAME   # Column name after file splitting

default_read_file = 'Data\\train.csv'
default_output_file = 'Data\\train_eq'

# Position of DATA and Time to Failure (TTF) in original data frames.
@unique
class Column(IntEnum):
    DATA = 0
    TTF = 1


def read_metadata_file():
    pass
