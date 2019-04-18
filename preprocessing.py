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
    default_file = 'Data\\train.csv'
    # default_file = 'test_checks.csv'

    def __init__(self, file_name=default_file):
        self.file_name = file_name
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

    def split_file(self, output_file_name):
        chunk_size = 10**6
        first_iteration = True
        buffer = None
        eq_number = 0

        for chunk in pd.read_csv(self.file_name, chunksize=chunk_size):
            if first_iteration:
                if not self._data_is_correct(chunk):
                    ppg.mock_error("Incorrect data format. Abort splitting.")
                    return
                else:
                    ppg.log_info("Data format correct.")
                    first_iteration = False
            if buffer is None:
                buffer = chunk.copy()
            else:
                before_eq, after_eq = self._split_on_eq(chunk)
                if after_eq is not None:
                    pd.concat(buffer, before_eq)
                    eq_number = self._save_eq(buffer, output_file_name, eq_number)
                    buffer = after_eq.copy()
                else:
                    if self._is_split_on_eq(buffer, chunk):



    def _save_eq(self, data, file_name, index):
        new_name = file_name + str(index) + EXPECTED_FILE_EXTENSION
        data.to_csv(new_name, index=True)
        next_index = index+1
        return next_index

    def _data_is_correct(self, data):
        is_correct = True

        if data is None:
            ppg.mock_warning("Caution data frame empty. Check loading sequence or file content.")
            is_correct = False
        elif type(data) is not pd.core.frame.DataFrame:
            ppg.mock_warning("Unexpected type. Data should be a pandas.DataFrame")
            is_correct = False
        elif data.ndim != DATA_DIMENSION:
            ppg.mock_warning("Number of dimensions incorrect. Is", data.ndim, "Expected:", DATA_DIMENSION)
            is_correct = False
        elif data.shape[-1] != len(COLUMN_NAME):
            ppg.mock_warning("Number of columns is incorrect. Is", data.shape[-1], "Expected", len(COLUMN_NAME))
            is_correct = False
        else:
            for names in zip(data.columns, COLUMN_NAME):
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
