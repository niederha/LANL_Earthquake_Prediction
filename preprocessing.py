"""
This file includes all data pre-processing, parsing and splitting methods to be used
"""

import pandas as pd
import files_metadata as fmd
from papagei import papagei as ppg
import os

# Debug options
ppg.VERBOSE = ppg.VerboseLevel.FRIVOLOUS


class DataSplitting:

    default_file = 'Data\\train.csv'

    def __init__(self, file_name=default_file):
        self.file_name = file_name

    @property
    def file_name(self):
        return self._file_name

    @file_name.setter
    def file_name(self, new_file_name):
        """
        Checks if the file name provided is correct and, if so changes the reference file to look at.
            :param new_file_name: New file to be split later
        """
        if self._file_exists(new_file_name) and self._extension_is_correct(new_file_name):
            self._data = None
            self._data_validity = False
            self._file_name = new_file_name
        else:
            ppg.log_info("Registering default file_name", self.default_file)
            self._file_name = self.default_file

    def split_file(self, output_file_name):
        """
        Goes through the file designated by self.file_name. Identifies earthquakes and save them in separated files
        named "output_file_name+earthquake_number+.csv".
            :param output_file_name: prefix of the saved file containing one earthquake each.
        """

        chunk_size = 10**6  # Number of lines to be read from the raw file at once. Reduce to spare RAM
        buffer = None       # Stores earthquakes before they are completed
        eq_number = 0       # Earthquake identifier

        # Iteration variables
        first_iteration = True
        i = 0

        for chunk in pd.read_csv(self.file_name, chunksize=chunk_size):
            ppg.log_frivolity("Iteration", i)
            i += 1

            # Checks data format once
            if first_iteration:
                if not self._data_is_correct(chunk):
                    ppg.mock_error("Incorrect data format. Abort splitting.")
                    return
                else:
                    ppg.log_info("Data format correct.")
                    first_iteration = False

            # Checks if the earthquake occurred between previous and current chunk
            if buffer is not None and self._is_split_on_eq(buffer, chunk):
                eq_number = self._save_eq(buffer, output_file_name, eq_number)
                buffer = None

            # Complete the buffer
            before_eq, after_eq = self._split_on_eq(chunk)
            if buffer is None:
                buffer = before_eq.copy()
            else:
                buffer = pd.concat([buffer, before_eq])

            # Save the buffer if there have been an earthquake
            if after_eq is not None:
                eq_number = self._save_eq(buffer, output_file_name, eq_number)
                buffer = after_eq.copy()

    def _data_is_correct(self, data):
        """
        Checks if the data have the expected formatting.
            :param data: data-frame of which the format has to be checked
            :return: True if the format is correct, False if not.
        """
        is_correct = True

        # If frame empty
        if data is None:
            ppg.mock_warning("Caution data frame empty. Check loading sequence or file content.")
            is_correct = False

        # If type is wrong
        elif type(data) is not pd.core.frame.DataFrame:
            ppg.mock_warning("Unexpected type. Data should be a pandas.DataFrame")
            is_correct = False

        # If dimension is wrong
        elif data.ndim != fmd.DATA_DIMENSION:
            ppg.mock_warning("Number of dimensions incorrect. Is", data.ndim, "Expected:", fmd.DATA_DIMENSION)
            is_correct = False
        elif data.shape[-1] != len(fmd.COLUMN_NAME):
            ppg.mock_warning("Number of columns is incorrect. Is", data.shape[-1], "Expected", len(fmd.COLUMN_NAME))
            is_correct = False

        # If column names are wrong
        else:
            for names in zip(data.columns, fmd.COLUMN_NAME):
                if names[0] != names[1]:
                    ppg.mock_warning("Unexpected column name:", names[0], "Expected:", names[1])
                    is_correct = False
                    break

        if is_correct:
            ppg.log_debug("Correct data format.")
        return is_correct

    def _split_on_eq(self, data):
        """
        Checks the data to find earthquake by looking for positive slope between two consecutive time to failure (TTF)
            :param data: Data that has to be inspected to find earthquakes
            :return before_eq: Part of the data frame that occurs before the earthquake
            :return after_eq: Part of the data frame the occurs after the earthquake. Can be None it no earthquake is
                              detected.
        """
        prev_time = data.iloc[0, fmd.Column.TTF.value]
        for i, current_time in enumerate(data.iloc[1:, fmd.Column.TTF.value]):
            # If TTF increases then it is an earthquake.
            if current_time >= prev_time:
                ppg.log_debug("New earthquake @", data.iloc[i, :].name)
                if prev_time != 0:
                    ppg.log_debug("Time artifact. Earthquake is ", prev_time)
                return data.iloc[0:i, :], data.iloc[i+1:, :]  # TODO: Don't assume there won't be two earthquakes in one chunk
            else:
                prev_time = current_time
        else:
            return data, None  # No earthquake occurred

    def _save_eq(self, data, file_name, index):
        """
        Saves a data frame "data" as a csv file starting with "file_name" followed by index. Returns the nest index.
            :param data: Data frame to be saved
            :param file_name: First part of the name under which to save the data
            :param index: Number to add after file_name
            :return next_index: Following index to be used
        """
        ppg.log_debug("Saving data... (this might take a few seconds)")
        new_name = file_name + str(index) + fmd.EXPECTED_FILE_EXTENSION
        data.to_csv(new_name, index=True)
        next_index = index+1
        return next_index

    def _is_split_on_eq(self, buffer, chunk):
        """
        Checks if an earthquake occurred between buffer(dataframe) and chunk(dataframe)
        :param buffer: Data frame occurring first
        :param chunk: Data frame following directly buffer
        :return is_split_on_eq: True if there is an earthquake between buffer and chunk, false else
        """
        is_split_on_eq = False
        if buffer is not None and chunk is not None:
            if buffer.iloc[-1, fmd.Column.TTF.value] < chunk.iloc[0, fmd.Column.TTF.value]:
                is_split_on_eq = True
        return is_split_on_eq

    @staticmethod
    def _extension_is_correct(file_name):
        """ Checks if the extension of file_name corresponds to the expected extension for data files """
        is_correct = True
        if file_name[-len(fmd.EXPECTED_FILE_EXTENSION):] != fmd.EXPECTED_FILE_EXTENSION:
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
