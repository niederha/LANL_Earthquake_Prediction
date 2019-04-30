""" This file contains all tools to visualise data. """

from matplotlib import pyplot as plt
import pandas as pd
import files_metadata as fmd


def plot_train_file(file_name):
    """
    Opens a .csv train file and plots the columns. The csv has to be the correct format in order for the plot to work.
        :param file_name: file to open.
    """
    df = pd.read_csv(file_name)
    plot_train_dataframe(df, file_name[:-len(fmd.EXPECTED_FILE_EXTENSION)])
    plt.show()


def plot_all_train_data(file_name):
    """
    Plots a huge traine file by chunk over different graphs.
        :param file_name:  file to plot.
    """

    chunk_size = 0.5*10**8
    title = "chunk "
    i = 0

    for chunk in pd.read_csv(file_name, chunksize=chunk_size):
        plot_train_dataframe(chunk, title+str(i))
        i += 1
    plt.show()


def plot_train_dataframe(df, title):
    """
    Plots a data frame containing training data.
        :param df: dataframe to plot.
        :param title: title to show.
    """
    # Color parameters
    color1 = "red"
    color2 = "blue"

    # Plot first set
    fig, ax1 = plt.subplots()
    ax1.set_xlabel("# point")
    ax1.set_ylabel(" Acoustic intensity", color=color1)
    ax1.tick_params(axis='y', labelcolor=color1)
    df.acoustic_data.plot(color=color1)

    # Plot second set
    ax2 = ax1.twinx()
    ax2.set_ylabel("Time to failure [s]", color=color2)
    ax2.tick_params(axis='y', labelcolor=color2)
    df.time_to_failure.plot(color=color2)

    plt.grid()
    plt.title(title)
