import tensorflow as tf
from tqdm import tqdm

from keras.callbacks import ModelCheckpoint
from mltu.preprocessors import WavReader

from mltu.tensorflow.dataProvider import DataProvider
from mltu.transformers import LabelIndexer, LabelPadding, SpectrogramPadding
from mltu.tensorflow.losses import CTCloss
from mltu.tensorflow.callbacks import Model2onnx
from mltu.tensorflow.metrics import CERMetric, WERMetric

from model import train_model
from configs import ModelConfigs
import os
import librosa

labels = [
    'on', 'off',
]
train_audio_path = 'data/audio_48k'
dataset = []

for label in tqdm(labels):
    waves = [f for f in os.listdir(train_audio_path + '/'+ label) if f.endswith('.wav')]
    for wav in waves:
        file = train_audio_path + '/' + label + '/' + wav
        samples, sample_rate = librosa.load(file, sr = 48000)
        dataset.append([file, label])
           

configs = ModelConfigs()

print(len(dataset))

max_text_length, max_spectrogram_length = 0, 0
for file_path, label in tqdm(dataset):
    spectrogram = WavReader.get_spectrogram(
        file_path, frame_length=configs.frame_length, frame_step=configs.frame_step, fft_length=configs.fft_length)
    valid_label = [c for c in label if c in configs.vocab]
    max_text_length = max(max_text_length, len(valid_label))
    max_spectrogram_length = max(max_spectrogram_length, spectrogram.shape[0])
    configs.input_shape = [max_spectrogram_length, spectrogram.shape[1]]


configs.max_spectrogram_length = max_spectrogram_length
configs.max_text_length = max_text_length
configs.save()

data_provider = DataProvider(
    dataset=dataset,
    skip_validation=True,
    batch_size=configs.batch_size,
    data_preprocessors=[
        WavReader(frame_length=configs.frame_length,
                  frame_step=configs.frame_step, fft_length=configs.fft_length),
    ],
    transformers=[
        SpectrogramPadding(
            max_spectrogram_length=configs.max_spectrogram_length, padding_value=0),
        LabelIndexer(configs.vocab),
        LabelPadding(max_word_length=configs.max_text_length,
                     padding_value=len(configs.vocab)),
    ],
)

train_data_provider, val_data_provider = data_provider.split(split=0.8)

model = train_model(
    input_dim=configs.input_shape,
    output_dim=len(configs.vocab),
    activation='relu', #leaky_relu
    dropout=0.1
)

# Compile the model and print summary
model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=configs.learning_rate),
    loss=CTCloss(),
    metrics=[
        CERMetric(vocabulary=configs.vocab),
        WERMetric(vocabulary=configs.vocab),
    ],
    run_eagerly=False,
)

checkpoint = ModelCheckpoint(f"{configs.model_path}\model.h5",
                             monitor="val_CER", verbose=1, save_best_only=True, mode="min")
model2onnx = Model2onnx(f"{configs.model_path}\model.h5")

# Train the model
model.fit(
    train_data_provider,
    validation_data=val_data_provider,
    epochs=configs.train_epochs,
    callbacks=[checkpoint,
                model2onnx],
    workers=configs.train_workers
)
