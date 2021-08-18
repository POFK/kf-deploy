import tensorflow as tf
from tensorflow.keras.utils import multi_gpu_model

tf.debugging.set_log_device_placement(True)
mirrored_strategy = tf.distribute.MirroredStrategy(devices=["/gpu:0","/gpu:1"])

import numpy as np
def load_data(path):
    with np.load(path, allow_pickle=True) as f:
        x_train, y_train = f['x_train'], f['y_train']
        x_test, y_test = f['x_test'], f['y_test']

        return (x_train, y_train), (x_test, y_test)
    
(x_train, y_train),(x_test, y_test) = load_data(path='datasets/mnist.npz')

x_train, x_test = x_train / 255.0, x_test / 255.0

with mirrored_strategy.scope():
    model = tf.keras.models.Sequential([
      tf.keras.layers.Flatten(input_shape=(28, 28)),
      tf.keras.layers.Dense(128, activation='relu'),
      tf.keras.layers.BatchNormalization(renorm=False),
      tf.keras.layers.Dropout(0.2),
      tf.keras.layers.Dense(10)
    ])

    loss_fn = tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True)
    

    model.compile(optimizer='adam',
              loss=loss_fn,
              metrics=['accuracy'])

model.fit(x_train, y_train, epochs=5)
              
model.evaluate(x_test,  y_test, verbose=2)