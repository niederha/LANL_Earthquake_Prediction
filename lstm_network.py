
import tensorflow as tf
from tensorflow.python.keras.models import Sequential
from tensorflow.python.keras.layers import Dense, Dropout, CuDNNLSTM, LSTM

from papagei import papagei as ppg


class NetworkLSTM:
    def __init__(self, nb_lstm_layers, lstm_layers_size, dropout_rate, learning_rate):
        # TODO: write accessors
        if len(lstm_layers_size) != nb_lstm_layers:
            ppg.mock_warning("The number of lstm_layer_size does not corresponds to the nb_lstm_layers. The layer size "
                             "will be", lstm_layers_size[0], "for all layers")
            lstm_layers_size = [lstm_layers_size[0]]*nb_lstm_layers

        # TODO: make a separate method for building and compiling
        # Model building
        model = Sequential()

        # Initial layer
        model.add(CuDNNLSTM(lstm_layers_size[0], input_size=1, return_sequences=True))  # TODO: Sort the input shape thingy and chek the return sequence thingy
        model.add(Dropout(dropout_rate))

        for layer_size in lstm_layers_size[1:]:
            model.add(CuDNNLSTM(layer_size))
            model.add(Dropout(dropout_rate))

        model.add(Dense(32, activation='relu'))
        model.add(Dropout(dropout_rate))
        model.add(Dense(10, activation='softmax'))

        opt = tf.keras.optimizers.Adam(lr=learning_rate)

        model.compile(  # TODO: CHECK mtrics and loss
            loss='sparse_categorical_crossentropy',
            optimizer=opt,
            metrics=['accuracy'],
        )

        """model.fit(x_train,
                  y_train,
                  epochs=3,
                  validation_data=(x_test, y_test))"""