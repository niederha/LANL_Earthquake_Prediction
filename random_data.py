""" Module that allows to generate random data files formatted the same way as the test and training sets from
Kaggle."""

import pandas as pd
import numpy as np
import files_metadata as fmd
from papagei import papagei as ppg

# Parameters for the acoustic data
max_acoustic = 1.
min_acoustic = -1.

def generate_random_training(file_name, nb_points):
    """
    Generates a file containing dummy data formatted like the train sets from Kaggle
        :param file_name: Name under which to save the dummy data. Has to be a .csv file or it will be reformatted
        :param nb_points: Number of points to include in the dummy data
        :return: Saves a file in CSV format
    """
    file_name = _format_file_extension(file_name)
    acoustic_data = _generate_random_acoustic(nb_points)
    acoustic_data = np.concatenate((acoustic_data, np.ones((nb_points, 1))), axis=1)
    data = pd.DataFrame(acoustic_data, columns=fmd.COLUMN_NAME)
    data.to_csv(file_name, index=True)


def generate_random_testing(file_name, nb_points):
    """
    Generates a file containing dummy data formatted like the test sets from Kaggle
        :param file_name: Name under which to save the dummy data. Has to be a .csv file or it will be reformatted
        :param nb_points: Number of points to include in the dummy data
        :return: Saves a file in CSV format
    """
    file_name = _format_file_extension(file_name)
    acoustic_data = _generate_random_acoustic(nb_points)
    data = pd.DataFrame(acoustic_data, columns=[fmd.COLUMN_NAME[0]])
    data.to_csv(file_name, index=True)


def _format_file_extension(file_name):
    """
    Takes a file_name and if the extension is not the expected one reformats it to get the right extension.
        :param file_name: file name to be checked/reformatted
        :return: reformatted file name
    """
    if file_name[-len(fmd.EXPECTED_FILE_EXTENSION):] != fmd.EXPECTED_FILE_EXTENSION:
        ppg.mock_warning("Unexpected file extension.")
        file_name = file_name.replace(".", "dot")
        file_name += fmd.EXPECTED_FILE_EXTENSION
    return file_name


def _generate_random_acoustic(nb_points):
    """
    Generates an array [nb_points X DATA_DIMENSION-1] and fills it with random numbers from min_acoustic to max_acoustis.
        :param nb_points: number of points to include in the array
        :return: an array filled with random points.
    """
    mean_acoustic = (max_acoustic + min_acoustic) / 2.
    span_acoustic = abs(max_acoustic - mean_acoustic)
    acoustic_data = np.random.rand((nb_points, fmd.DATA_DIMENSION - 1))
    acoustic_data *= span_acoustic
    acoustic_data += mean_acoustic
    return acoustic_data
