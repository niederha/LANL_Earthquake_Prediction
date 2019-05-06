"""
This file includes all data pre-processing, parsing and splitting methods to be used.
"""

import pandas as pd
import os
from math import inf

import files_metadata as fmd
from papagei import papagei as ppg


# Debug options
ppg.VERBOSE = ppg.VerboseLevel.FRIVOLOUS


class DataSplitting:

    def __init__(self, read_file_name=fmd.default_read_file, output_file_name=fmd.default_output_file):

        pd.options.mode.use_inf_as_na = True  # Data shouldn't be inf
        self._file_name = None

        self.file_name = read_file_name
        self.output_file_name = output_file_name
        self._nb_earthquake = 0  # Number of earthquakes detected over the whole file.
        self._files_size = []  # Number of samples for each earthquake.
        self._metadata = pd.DataFrame([0, -inf, inf, 0, 0, 0], columns=fmd.DATA_TO_TRACK)  # Earthquake metadata

    @property
    def read_file_name(self):
        """
        File to read the data from and to split.
        """
        return self._file_name

    @read_file_name.setter
    def read_file_name(self, new_file_name):
        """
        Checks if the file name provided is correct and, if so changes the reference file to look at.
            :param new_file_name: New file to be split later.
        """
        if self._file_exists(new_file_name) and self._extension_is_correct(new_file_name):
            self._file_name = new_file_name
        else:
            ppg.log_info("Registering default file_name", fmd.default_read_file)
            self._file_name = fmd.default_read_file

    @property
    def output_file_name(self):
        return self._output_file_name

    @output_file_name.setter
    def output_file_name(self, new_output_file_name):
        self._output_file_name = new_output_file_name.replace(".", "_")

    def split_file(self):
        """
        Goes through the file designated by self.file_name. Identifies earthquakes and save them in separated files
        named "self.output_file_name+earthquake_number+.csv".
        """

        chunk_size = 10**6  # Number of lines to be read from the raw file at once. Reduce to spare RAM
        buffer = None       # Stores earthquakes before they are completed

        # Iteration variables
        self._nb_earthquake = 0
        first_iteration = True
        i = 0

        self._metadata[:, 'sum_of_sq'] = None  # Extra column used to compute global stdev

        for chunk in pd.read_csv(self.file_name, chunksize=chunk_size):
            ppg.log_frivolity("Iteration", i)
            i += 1
            chunk.dropna(inplace=True)
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
                self._save_eq(buffer)
                buffer = None

            # Complete the buffer
            before_eq, after_eq = self._split_on_eq(chunk)
            if buffer is None:
                buffer = before_eq.copy()
            else:
                buffer = pd.concat([buffer, before_eq])

            # Save the buffer if there have been an earthquake
            if after_eq is not None:
                self._save_eq(buffer)
                buffer = after_eq.copy()

    def _split_on_eq(self, data):
        """
        Checks the data to find earthquake by looking for positive slope between two consecutive time to failure (TTF).
            :param data: Data that has to be inspected to find earthquakes.
            :return before_eq: Part of the data frame that occurs before the earthquake.
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

    def _save_eq(self, data):
        """
        Saves a data frame "data" as a csv file starting with "file_name" followed by index. Returns the nest index.
            :param data: Data frame to be saved.
            :return next_index: Following index to be used.
        """
        ppg.log_debug("Saving data... (this might take a few seconds)")
        new_name = self.output_file_name + str(self._nb_earthquake) + fmd.EXPECTED_FILE_EXTENSION
        data.to_csv(new_name, index=False)
        self.update_eq_metadata(data)

    def update_global_metadata(self):
        """

        :return:
        """
        ppg.log_info("Computing global metadata.")

        self._metadata.loc['global', 'size'] = self._metadata.loc[:, 'size'].sum()
        self._metadata.loc['global', 'max'] = self._metadata.loc[:, 'max'].max()
        self._metadata.loc['global', 'min'] = self._metadata.loc[:, 'min'].min()

        # Trick to save ram while computing mean
        weighted_sum_means = self._metadata.loc[:, 'size'] * self._metadata.loc[:, 'mean']
        self._metadata.loc['global', 'mean'] = weighted_sum_means.sum()/self._metadata.loc['global', 'size']

        # Trick to save ram while computing global variance
        self._metadata.loc['global', 'stdev'] = self._metadata.loc[:, 'sum_of_sq']/self._metadata.loc['global', 'size']\
                                                - self._metadata.loc['global', 'mean'].pow(2)
        self._metadata.loc['global', 'stdev'] = self._metadata.loc['global', 'stdev'].pow(1/2)

        # Get rid of column for intermediary result
        self._metadata.drop(columns='sum_of_sq', inplace=True)

    def update_eq_metadata(self, data):
        """

        :param data:
        :return:
        """
        ppg.log_info("Computing earthquake metadata")
        self._metadata.loc[self._nb_earthquake, 'size'] = len(data)
        self._metadata.loc[self._nb_earthquake, 'max'] = data.iloc[:, fmd.Column.DATA.value].max()
        self._metadata.loc[self._nb_earthquake, 'min'] = data.iloc[:, fmd.Column.DATA.value].min()
        self._metadata.loc[self._nb_earthquake, 'mean'] = data.iloc[:, fmd.Column.DATA.value].mean()
        self._metadata.loc[self._nb_earthquake, 'stdev'] = data.iloc[:, fmd.Column.DATA.value].std()
        self._metadata.loc[self._nb_earthquake, 'sum_of_sq'] = data.iloc[:, fmd.Column.DATA.value].pow(2).sum()
        self._nb_earthquake += 1

    @staticmethod
    def _is_split_on_eq(buffer, chunk):
        """
        Checks if an earthquake occurred between buffer(dataframe) and chunk(dataframe).
            :param buffer: Data frame occurring first.
            :param chunk: Data frame following directly buffer.
            :return is_split_on_eq: True if there is an earthquake between buffer and chunk, false else.
        """
        is_split_on_eq = False
        if buffer is not None and chunk is not None:
            if buffer.iloc[-1, fmd.Column.TTF.value] < chunk.iloc[0, fmd.Column.TTF.value]:
                is_split_on_eq = True
        return is_split_on_eq

    @staticmethod
    def _data_is_correct(data):
        """
        Checks if the data have the expected formatting.
            :param data: data-frame of which the format has to be checked.
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

    @staticmethod
    def _extension_is_correct(file_name):
        """
        Checks if the extension of file_name corresponds to the expected extension for data files.
            :param file_name: File of which the extension has tobe checked.
            :return: True if the extension is correct, False else.
        """
        is_correct = True
        if file_name[-len(fmd.EXPECTED_FILE_EXTENSION):] != fmd.EXPECTED_FILE_EXTENSION:
            ppg.mock_warning("Unexpected file extension.")
            is_correct = False
        return is_correct

    @staticmethod
    def _file_exists(file_name):
        """
        Checks if a file with file_name exists.
            :param file_name: File of which the existence has to be checked.
            :return: True if file_name exists, False else.
        """
        exists = os.path.isfile(file_name)
        if not exists:
            ppg.mock_warning("File", file_name, "not found")
        return exists
