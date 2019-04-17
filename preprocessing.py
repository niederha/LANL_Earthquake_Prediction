"""
This file includes all data pre-processing methods used
"""

import pandas as pd
from papagei import papagei as ppg
import os

EXPECTED_FILE_EXTENSION = '.csv'
DATA_DIMENSION = 2
COLUMN_NAME = ['acoustic_data', 'time_to_failure']
ppg.VERBOSE = ppg.VerboseLevel.FRIVOLOUS


class DataPreprocessor:
    # default_file = 'Data\\test\\seg_00a37e.csv'
    default_file = 'test_checks.csv'

    def __init__(self, file_name=default_file):
        self.file_name = file_name
        self._data = None
        self._data_validity = False

    @property
    def file_name(self):
        return self._file_name

    @file_name.setter
    def file_name(self, new_file_name):
        if self._file_exists(new_file_name) and self._extension_is_correct(new_file_name):
            self._data = None
            self._data_validity = False
            self._file_name = new_file_name
        else:
            ppg.log_info("Registering default file_name", self.default_file)
            self._file_name = self.default_file

    def load_file(self):
        if self._data_validity:
            ppg.log_info("Data already checked and loaded.")
        else:
            self._open_raw_train_file()

    def split_file(self, output_file_name):
        if not self._data_validity:
            self._open_raw_train_file()
        self._split_earthquakes(output_file_name)

    def _open_raw_train_file(self):
        ppg.log_frivolity("Loading ...")
        self._data = pd.read_csv(self.file_name)
        ppg.log_frivolity("Loading complete.")
        ppg.log_frivolity("Checking data format...")
        if self._data_is_correct():
            self._data_validity = True
        else:
            self._data_validity = False
        ppg.log_frivolity("Data format checked.")

    def _data_is_correct(self):
        is_correct = True

        if self._data is None:
            ppg.mock_warning("Caution data frame empty. Check loading sequence or file content.")
            is_correct = False
        elif type(self._data) is not pd.core.frame.DataFrame:
            ppg.mock_warning("Unexpected type. Data should be a pandas.DataFrame")
            is_correct = False
        elif self._data.ndim != DATA_DIMENSION:
            ppg.mock_warning("Number of dimensions incorrect. Is", self._data.ndim, "Expected:", DATA_DIMENSION)
            is_correct = False
        elif self._data.shape[-1] != len(COLUMN_NAME):
            ppg.mock_warning("Number of columns is incorrect. Is", self._data.shape[-1], "Expected", len(COLUMN_NAME))
            is_correct = False
        else:
            for names in zip(self._data.columns, COLUMN_NAME):
                if names[0] != names[1]:
                    ppg.mock_warning("Unexpected column name:", names[0], "Expected:", names[1])
                    is_correct = False
                    break
        if is_correct:
            ppg.log_debug("Correct data format.")
        return is_correct

    def _split_earthquakes(self, file_name):
        """The identification and splitting is done at once in a attempt to save RAM"""
        previous_eq = 0
        eq_number = 0
        if not self._data_validity or self._data is None:
            ppg.mock_warning("Cannot look for earthquake. Data not valid")
        else:
            prev_time = self._data.loc[0, COLUMN_NAME[1]]
            for i, current_time in enumerate(self._data.loc[1:, COLUMN_NAME[1]]):

                # Earthquake detected
                if current_time >= prev_time:

                    # Display infos
                    ppg.log_debug("New earthquake @ index ", i)
                    if prev_time != 0:
                        ppg.log_debug("Time artifact. Earthquake is ", prev_time)

                    # Save file
                    new_name = file_name + str(eq_number) + EXPECTED_FILE_EXTENSION
                    buffer = self._data.loc[previous_eq:i, :]
                    self._data.drop(list(range(previous_eq+1, i)))
                    buffer.to_csv(new_name, index=True)

                    # Update indices
                    eq_number += 1
                    buffer = None
                    previous_eq = i+1

                prev_time = current_time

    @staticmethod
    def _extension_is_correct(file_name):
        """ Checks if the extension of file_name corresponds to the expected extension for data files """
        is_correct = True
        if file_name[-len(EXPECTED_FILE_EXTENSION):] != EXPECTED_FILE_EXTENSION:
            ppg.mock_warning("Unexpected file extension.")
            is_correct = False
        return is_correct

    @staticmethod
    def _file_exists(file_name):
        """ Checks if a file with file_name exists"""
        exists = os.path.isfile(file_name)
        if not exists:
            ppg.mock_warning("File", file_name, "not found")
        return exists
