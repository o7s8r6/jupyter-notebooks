# %%
import numpy as np

import keras
from keras.models import Sequential, Model
from keras.layers import LSTM


# Activation Functions and Derivatives
def sigmoid(x):
    return 1 / (1 + np.exp(-x))


x = np.array([
    [[1.4, 1.5, 1.2],
     [1.9, 1.1, 1.2],
     [1.7, 1.4, 1.2],
     [1.5, 1.3, 1.2]],
])  # (None, 4, 3)
y = np.array([[1, 1]])  # (None, 2)

model = Sequential()
model.add(LSTM(2, input_shape=(4, 3)))

model.compile(loss='mse',
              optimizer='SGD',
              metrics=['accuracy'])
model.summary()

# %%
model.fit(x, y, epochs=1)

# %% Print weights.
names = [weight.name for layer in model.layers for weight in layer.weights]
weights = model.get_weights()

# suppress scientific notation
np.set_printoptions(suppress=True)
for name, weight in zip(names, weights):
    print(name, weight.shape)
    print(weight)

    layer_type = name.split('/')[1]
    if layer_type == 'kernel:0':
        kernel_0 = weight
    if layer_type == 'recurrent_kernel:0':
        recurrent_kernel_0 = weight
    elif layer_type == 'bias:0':
        bias_0 = weight

    print()

# remove unnecessary variables for scientific debugging.
del layer_type, weight, weights, name, names

# %%
n = 1
units = 2  # LSTM layers

# (3, 8) Embedding dim, LSTM layers * 4
Wi = kernel_0[:, 0:units]
Wf = kernel_0[:, units:2 * units]
Wc = kernel_0[:, 2 * units:3 * units]
Wo = kernel_0[:, 3 * units:]

# (2, 8) LSTM layers, LSTM layers * 4
Ui = recurrent_kernel_0[:, 0:units]
Uf = recurrent_kernel_0[:, units:2 * units]
Uc = recurrent_kernel_0[:, 2 * units:3 * units]
Uo = recurrent_kernel_0[:, 3 * units:]

# (8,) LSTM layers * 4
bi = bias_0[0:units]
bf = bias_0[units:2 * units]
bc = bias_0[2 * units:3 * units]
bo = bias_0[3 * units:]

ht_1 = np.zeros(n * units).reshape(n, units)
Ct_1 = np.zeros(n * units).reshape(n, units)

# --
for t in range(0, len(x[0, :])):
    xt = np.array(x[0, t])

    it = sigmoid(np.dot(xt, Wi) + np.dot(ht_1, Ui) + bi)  # input gate
    ft = sigmoid(np.dot(xt, Wf) + np.dot(ht_1, Uf) + bf)  # forget gate
    Ct = ft * Ct_1 + it * np.tanh(np.dot(xt, Wc) + np.dot(ht_1, Uc) + bc)
    ot = sigmoid(np.dot(xt, Wo) + np.dot(ht_1, Uo) + bo)  # output gate

    ht = ot * np.tanh(Ct)

    ht_1 = ht  # memory state
    Ct_1 = Ct  # carry state

    print(t, ht)

# remove unnecessary variables for scientific debugging.
del Ct, Ct_1, ft, ht, ht_1, it, ot, xt

# The expected value is a little bit different from the actual value.
# but the implementation is the **SAME with Keras**.
intermediate_layer_model = Model(inputs=model.input,
                                 outputs=model.output)
output = intermediate_layer_model.predict(x[:1])
print()
print("actual:", output)