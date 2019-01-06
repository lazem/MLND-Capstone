import numpy as np
import json
from keras import Sequential, Model
from keras.layers import LSTM, Dense, Dropout, Embedding, \
    Concatenate, Flatten, TimeDistributed, Input
from sklearn.model_selection import train_test_split
import keras

NB_LSTM_CELLS = 256
NB_DENSE_CELLS = 256
EMBEDDING_SIZE = 100


class DuplicateFilter:
    def __init__(self):
        self.load_config()
        self.model = self.make_lstm_model_mod()
        self.model.load_weights("body_conv-weights.h5")

    def load_config(self):
        with open('bo_config.json') as infile:
            self.config = json.load(infile)

    def make_lstm_model_mod(self):
        #     first_model = Sequential()
        url_a = Input(shape=(self.config['max_url_seq_length'],))
        url_b = Input(shape=(self.config['max_url_seq_length'],))

        first_model = Sequential()
        first_model.add(
            Embedding(input_dim=self.config['num_input_tokens'], input_length=self.config['max_url_seq_length'],
                      output_dim=EMBEDDING_SIZE))  # input_length=config['max_url_seq_length'],

        first_model.add(LSTM(NB_LSTM_CELLS, return_sequences=True, dropout=0.2))
        first_model.add(TimeDistributed(Dense(NB_LSTM_CELLS)))

        encoded_a = first_model(url_a)
        encoded_b = first_model(url_b)

        merged_vector = keras.layers.concatenate([encoded_a, encoded_b], axis=-1)
        merged_vector = Dense(NB_DENSE_CELLS, activation='relu')(merged_vector)

        merged_vector = Dropout(0.3)(merged_vector)
        merged_vector = Flatten()(merged_vector)

        predictions = Dense(2, activation='softmax')(merged_vector)

        model = Model(inputs=[url_a, url_b], outputs=predictions)

        model.compile(optimizer='adam',
                      loss='categorical_crossentropy',
                      metrics=['accuracy'])

        return model

    def model_predict(self, url1, url2):
        data_size = 1
        X1val = np.zeros(shape=(data_size, self.config['max_url_seq_length']))
        X2val = np.zeros(shape=(data_size, self.config['max_url_seq_length']))
        for idx, c in enumerate(url1):
            if c in self.config['char2idx']:
                X1val[0, idx] = self.config['char2idx'][c]
        for idx, c in enumerate(url2):
            if c in self.config['char2idx']:
                X2val[0, idx] = self.config['char2idx'][c]
        predicted = self.model.predict([X1val, X2val])[0]

        predicted_label = np.argmax(predicted)

        return predicted_label
