import csv
import sys

import numpy as np
from sklearn.model_selection import train_test_split
from tensorflow.keras import layers, models

# 定数
OUTPUTS = {'dahai': 34, 'richi': 2, 'ankan': 2, 'pon': 2, 'chi': 4}

for file_name in sys.argv[1:]:
    # 変数
    n_output = OUTPUTS[file_name]
    epoch = 25
    batch_size = 256

    model = models.Sequential([
        layers.Conv2D(32, (5, 2), activation='relu', padding='same'),
        layers.Dropout(0.2),
        layers.Conv2D(64, (5, 2), activation='relu', padding='same'),
        layers.Dropout(0.2),
        layers.Conv2D(128, (5, 2), activation='relu', padding='same'),
        layers.Dropout(0.2),
        layers.Flatten(),
        layers.Dense(128, activation='relu'),
        layers.Dropout(0.2),
        layers.Dense(n_output, activation='softmax'),
    ])

    model.compile(optimizer='adam',
                  loss='sparse_categorical_crossentropy',
                  metrics=['accuracy'])

    # データ準備
    x = []
    t = []
    with open('./datasets/' + file_name + '.csv') as f:
        reader = csv.reader(f, delimiter=",")
        for row in reader:
            row = list(map(int, row))
            tt, row = row[0], row[1:]
            xx = [[[0] * (len(row) // 34) for _ in range(4)] for _ in range(34)]
            for c in range(len(row) // 34):
                for w in range(4):
                    for h in range(34):
                        if row[c * 34 + h] >= w:
                            xx[h][w][c] = 1

            x.append(xx)
            t.append(tt)

    x = np.array(x, np.float32)
    t = np.array(t, np.int32)

    x_train, x_test, t_train, t_test = train_test_split(x, t, test_size=0.2, shuffle=True)

    model.fit(x_train, t_train, epochs=epoch, validation_data=(x_test, t_test))
    model.save('{}.h5'.format(file_name))
