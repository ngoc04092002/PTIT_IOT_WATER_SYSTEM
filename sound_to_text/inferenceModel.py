import typing
import numpy as np

from mltu.inferenceModel import OnnxInferenceModel
from mltu.preprocessors import WavReader
from mltu.utils.text_utils import ctc_decoder, get_cer, get_wer


class WavToTextModel(OnnxInferenceModel):
    def __init__(self, char_list: typing.Union[str, list], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.char_list = char_list

    def predict(self, data: np.ndarray):
        data_pred = np.expand_dims(data, axis=0)

        preds = self.model.run(None, {self.input_name: data_pred})[0]

        text = ctc_decoder(preds, self.char_list)[0]

        return text


if __name__ == "__main__":
    from mltu.configs import BaseModelConfigs

    configs = BaseModelConfigs.load(
        "G:\PTIT\IOT\html\\temp_hum_soil\\202312171725\configs.yaml")

    model = WavToTextModel(model_path=configs.model_path,
                           char_list=configs.vocab, force_cpu=False)
    spectrogram = WavReader.get_spectrogram('G:\\PTIT\\IOT\\html\\data\\audio_48k\\off\\_2fob9A.wav',
                                            frame_length=configs.frame_length, frame_step=configs.frame_step, fft_length=configs.fft_length)
    # WavReader.plot_raw_audio(wav_path, label)

    padded_spectrogram = np.pad(spectrogram, ((
        0, configs.max_spectrogram_length - spectrogram.shape[0]), (0, 0)), mode="constant", constant_values=0)

    # WavReader.plot_spectrogram(spectrogram, 'heys whatsup')
    text = model.predict(padded_spectrogram)
    print('---->', text, '|')
