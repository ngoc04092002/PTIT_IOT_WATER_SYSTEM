import tensorflow as tf
import pandas as pd
from tqdm import tqdm

from keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
from mltu.preprocessors import WavReader

from mltu.tensorflow.dataProvider import DataProvider
from mltu.transformers import LabelIndexer, LabelPadding, SpectrogramPadding
from mltu.tensorflow.losses import CTCloss
from mltu.tensorflow.callbacks import Model2onnx, TrainLogger
from mltu.tensorflow.metrics import CERMetric, WERMetric

from model import train_model
from configs import ModelConfigs

dataset_path = "G:\PTIT\IOT\html\Datasets\LJSpeech-1.1"
metadata_path = dataset_path + "\metadata.csv"

metadata_df = pd.read_csv(metadata_path, sep="|", header=None, quoting=3)
metadata_df.columns = ["file_name",
                       "transcription", "normalized_transcription"]
metadata_df = metadata_df[["file_name", "normalized_transcription"]]

dataset = [[f"G:\PTIT\IOT\html\Datasets\LJSpeech-1.1\wavs\{file}.wav", label.lower(
)] for file, label in metadata_df.values.tolist()]

configs = ModelConfigs()

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
    activation='leaky_relu',
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
# model.summary(line_length=110)

# Define callbacks
# earlystopper = EarlyStopping(
#     monitor="val_CER", patience=20, verbose=1, mode="min")
checkpoint = ModelCheckpoint(f"{configs.model_path}\model.h5",
                             monitor="val_CER", verbose=1, save_best_only=True, mode="min")
# trainLogger = TrainLogger(configs.model_path)
# reduceLROnPlat = ReduceLROnPlateau(
#     monitor="val_CER", factor=0.8, min_delta=1e-10, patience=5, verbose=1, mode="auto")
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

# train_data_provider.to_csv(os.path.join(configs.model_path, "train.csv"))
# val_data_provider.to_csv(os.path.join(configs.model_path, "val.csv"))
