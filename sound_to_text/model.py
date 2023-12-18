import tensorflow as tf
from keras import layers
from keras.models import Model


def train_model(input_dim, output_dim, activation="relu", dropout=0.5):
    inputs = layers.Input(shape=input_dim, name="input", dtype=tf.float32)

    # Expand dims to add channel dimension
    input_expanded = layers.Reshape((input_dim[0], input_dim[1], 1))(inputs)

    # Convolution layer 1
    x = layers.Conv2D(filters=16, kernel_size=[11, 21], strides=[2, 2], padding="same", use_bias=False)(input_expanded)
    x = layers.BatchNormalization()(x)
    x = layers.Activation(activation)(x)
    # Convolution layer 1
    x = layers.Conv2D(filters=32, kernel_size=[11, 41], strides=[2, 2], padding="same", use_bias=False)(input_expanded)
    x = layers.BatchNormalization()(x)
    x = layers.Activation(activation)(x)

    # Convolution layer 2
    x = layers.Conv2D(filters=32, kernel_size=[11, 41], strides=[1, 2], padding="same", use_bias=False)(x)
    x = layers.BatchNormalization()(x)
    x = layers.Activation(activation)(x)

    # Reshape the resulted volume to feed the RNN layers
    x = layers.Reshape((-1, x.shape[-2] * x.shape[-1]))(x)

    # RNN layers
    for _ in range(3):
        x = layers.Bidirectional(layers.LSTM(64, return_sequences=True))(x)
    x = layers.Bidirectional(layers.LSTM(64, return_sequences=True))(x)

    # Dense layer
    x = layers.TimeDistributed(layers.Dense(128))(x)
    x = layers.Activation(activation)(x)
    x = layers.Dropout(dropout)(x)

    # Classification layer
    output = layers.Dense(output_dim + 1, activation="softmax", dtype=tf.float32)(x)

    model = Model(inputs=inputs, outputs=output)
    return model