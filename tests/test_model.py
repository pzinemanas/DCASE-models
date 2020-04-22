import sys
import os
import glob
import numpy as np
from librosa.core import power_to_db
import matplotlib.pyplot as plt

sys.path.append('../')
from dcase_models.utils.files import load_json
from dcase_models.data.data_generator import *
from dcase_models.model.container import *
from dcase_models.data.scaler import Scaler

os.environ["CUDA_VISIBLE_DEVICES"] = "1"

dataset = 'UrbanSound8k'

params = load_json('parameters.json')
params_dataset = params["datasets"][dataset]

# get model class
try:
    data_generator_class = globals()[dataset]
except:
    print('Warning: using default ModelContainer')
    data_generator_class = DataGenerator()

print(data_generator_class)
data_generator = data_generator_class(params_dataset['audio_folder'], params_dataset['feature_folder'], 'mel_spectrograms',
                                      params_dataset['folds'], params_dataset['label_list'])

data_generator.load_data()

model = 'SB_CNN'
params_model = params["models"][model]
# get model class
try:
    model_class = globals()[model]
except:
    print('Warning: using default ModelContainer')
    model_class = ModelContainer()

print(model_class)
model_container = model_class(model=None, folder=None, n_classes=10, n_frames_cnn=64, 
            n_freq_cnn=128, **params_model['model_arguments'])

model_container.model.summary()

fold_test = 'fold1'
X_train, Y_train, X_val, Y_val = data_generator.get_data_for_training(fold_test)
scaler = Scaler(normalizer='minmax')
scaler.fit(X_train)
X_train = scaler.transform(X_train)
X_val = scaler.transform(X_val)

kwargs = params["train"]
train_arguments = params_model['train_arguments']
model_container.train(X_train, Y_train, X_val, Y_val, weights_path= './',  log_path= './', **train_arguments, **kwargs)