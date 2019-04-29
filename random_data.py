
import pandas as pd
import numpy as np
import files_metadata as fmd


max_acoustic = 1.
min_acoustic = -1.


def generate_random_training(file_name, nb_points):
    acoustic_data = generate_random_acoustic(nb_points)
    acoustic_data = np.concatenate()


def generate_random_testing(file_name, nb_points):
    acoustic_data = generate_random_acoustic(nb_points)
    data = pd.DataFrame(acoustic_data, columns=fmd.COLUMN_NAME)
    data.to_csv(file_name, index=True)


def generate_random_acoustic(nb_points):
    mean_acoustic = (max_acoustic + min_acoustic) / 2.
    span_acoustic = abs(max_acoustic - mean_acoustic)
    acoustic_data = np.random.rand((nb_points, fmd.DATA_DIMENSION - 1))
    acoustic_data *= span_acoustic
    acoustic_data += mean_acoustic
    return acoustic_data
