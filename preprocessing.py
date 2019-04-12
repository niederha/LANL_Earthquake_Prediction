import pandas as pd
from warnings import warn

"""
This file includes all data pre-processing methods used
"""

EXPECTED_FILE_EXTENSION = ".csv"
DATA_DIMENSION = 2
COLUMN_NAME = ['acoustic_data', 'time_to_failure']




class DataPreprocessor:
    # default_file = 'Data\\test\\seg_00a37e.csv'
    default_file = 'Data\\train.csv'

    def __init__(self, file_name=default_file):
        self.file_name = file_name
        self._data = None
        self._data_validity = False

    @property
    def file_name(self):
        return self._file_name

    @file_name.setter
    def file_name(self, new_file_name):
        if self._extension_is_correct(new_file_name):
            self._data = None
            self._file_name = new_file_name
            self._data_validity = False
        else:
            print("Registering default file_name ", self.default_file)
            self._file_name = self.default_file

    def load_file(self):
        if self._data_validity:
            print("Data already loaded and checked")
        else:
            self._open_raw_train_file()

    def split_file(self, output_file_name):
        self._open_raw_train_file()
        self._split_earthquakes(output_file_name)

    def _open_raw_train_file(self):
        print("Loading ...")
        self._data = pd.read_csv(self.file_name)
        print("Loading Complete")
        print("Checking data format...")
        if self._data_is_correct():
            self._data_validity = True
        else:
            self._data_validity = False
        print("Data format checked")

    def _data_is_correct(self):
        is_correct = True

        if self._data is None:
            warn(Warning("Caution data frame empty. Check loading sequence."))
            is_correct = False

        elif type(self._data) is not pd.core.frame.DataFrame:
            warn(Warning(" Unexpected type. Data should be a pandas.DataFrame"))
            is_correct = False

        elif self._data.ndim != DATA_DIMENSION:
            warn(Warning("Number of dimensions incorrect. Is " + str(self._data.ndim) + " Expected: "
                         + str(DATA_DIMENSION)))
            is_correct = False

        elif self._data.shape[-1] is not len(COLUMN_NAME):
            warn(Warning("Number of columns is incorrect. Is " + str(self._data.shape[-1]) + "Expected "
                         + str(len(COLUMN_NAME))))
            is_correct = False

        else:
            for names in zip(self._data.columns, COLUMN_NAME):
                if names[0] is not names[1]:
                    warn(Warning("Unexpected columns Name: " + names[0] + " Expected: " + names[1]))
                    is_correct = False
                    break

        return True  # TODO: Fix checks

    def _split_earthquakes(self, file_name):
        """The identification and splitting is done at once in a attemps to save RAM"""
        previous_eq = 0
        eq_number = 0
        if not self._data_validity or self._data is None:
            print("Cannot look for earthquake. Data not valid")
        else:
            prev_time = self._data.loc[0, COLUMN_NAME[1]]
            for i, current_time in enumerate(self._data.loc[1:, COLUMN_NAME[1]]):

                # Earthquake detected
                if current_time >= prev_time:

                    # Display infos
                    print("New earthquake @ index ", i)
                    if prev_time is not 0:
                        print("Time artifact. Earthquake is ", prev_time)

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

        is_correct = True
        if file_name[-len(EXPECTED_FILE_EXTENSION):] is not EXPECTED_FILE_EXTENSION:
            warn(Warning("Unexpected file extension."))
            is_correct = False
        return is_correct
