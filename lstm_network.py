
import tensorflow as tf
from tensorflow.python.keras.models import Sequential
from tensorflow.python.keras.layers import Dense, Dropout, CuDNNLSTM, BatchNormalization
from math import log2


from papagei import papagei as ppg


class NetworkLSTM:

    default_dropout_rate = 0.1

    def __init__(self, lstm_layers, learning_rate, dropout_rate=default_dropout_rate):
        self._lstm_layers = None
        self._learning_rate = None
        self._dropout_rate = None

        self.lstm_layers = lstm_layers
        self.learning_rate = learning_rate
        self.dropout_rate = dropout_rate
        self.model = None

        """model.fit(x_train,
                  y_train,
                  epochs=3,
                  validation_data=(x_test, y_test))"""

    @property
    def lstm_layers(self):
        return self._lstm_layers

    @lstm_layers.setter
    def lstm_layers(self, new_lstm_layers):
        for layer in new_lstm_layers:
            if log2(layer)-int(log2(layer)) != 0:
                ppg.log_debug("It is good practice to have layers that are powers of 2. One layer was", layer)

    @property
    def learning_rate(self):
        return self._learning_rate

    @learning_rate.setter
    def learning_rate(self, new_learning_rate):
        self._learning_rate = new_learning_rate

    @property
    def dropout_rate(self):
        return self._dropout_rate

    @dropout_rate.setter
    def dropout_rate(self, new_dropout_rate):
        if new_dropout_rate > 1 or new_dropout_rate < 0:
            ppg.mock_warning("Invalid dropout_rate. Has to be [0,1] but was", new_dropout_rate,
                             "Switching to default_dropout_rate=", self.default_dropout_rate)
            self._dropout_rate = self.default_dropout_rate
        else:
            if new_dropout_rate > 0.5:
                ppg.log_debug("Caution: high dropout_rate", new_dropout_rate, "might impair learning")
            self._dropout_rate = new_dropout_rate

    def build_model(self):
        # Model building
        self.model = Sequential()

        # LSTM layers
        for layer_size in self.lstm_layers[:-1]:
            self.model.add(CuDNNLSTM(layer_size, input_size=1, return_sequences=True))  # TODO: Sort the input shape thingy and check the return sequence thingy
            self.model.add(Dropout(self.dropout_rate))
            self.model.add(BatchNormalization())

        # Last LSTM layer
        self.model.add(CuDNNLSTM(self.lstm_layers[-1]))
        self.model.add(Dropout(self.dropout_rate))
        self.model.add(BatchNormalization())

        # Dense output layers
        self.model.add(Dense(32, activation='relu'))
        self.model.add(Dropout(self.dropout_rate))
        self.model.add(Dense(10, activation='relu'))

        opt = tf.keras.optimizers.Adam(lr=self.learning_rate)

        self.model.compile(  # TODO: CHECK metrics and loss
            loss='sparse_categorical_crossentropy',
            optimizer=opt,
            metrics=['accuracy'],
        )