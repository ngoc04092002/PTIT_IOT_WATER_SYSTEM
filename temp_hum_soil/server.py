from flask import Flask, request
from flask_socketio import SocketIO, emit
import speech_recognition as sr
from flask_cors import CORS
from websockets.server import serve
import json
import onnxruntime as rt
import numpy as np
import typing
import numpy as np

from mltu.inferenceModel import OnnxInferenceModel
from mltu.preprocessors import WavReader
from mltu.utils.text_utils import ctc_decoder
from mltu.configs import BaseModelConfigs

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
CORS(app, resources={r'/*': {'origins': '*'}})
socketio = SocketIO(app, cors_allowed_origins="*")


def predictTemp(data) -> str:
    model_path = "G:\PTIT\IOT\html\\temp_hum_soil\model.onnx"
    session = rt.InferenceSession(model_path)

    # Xây dựng dữ liệu đầu vào theo định dạng phù hợp với model ONNX
    input_data = np.array(data, dtype=np.float32)
    # Gọi API và truyền dữ liệu đầu vào
    output = session.run(None, {'dense_input': input_data})

    # Xử lý kết quả nhận được
    output_data = np.array(output[0]).flatten()[0]
    output_data = round(output_data)
    return str(output_data)


class WavToTextModel(OnnxInferenceModel):
    def __init__(self, char_list: typing.Union[str, list], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.char_list = char_list

    def predict(self, data: np.ndarray):
        data_pred = np.expand_dims(data, axis=0)

        preds = self.model.run(None, {self.input_name: data_pred})[0]

        text = ctc_decoder(preds, self.char_list)[0]

        return text


@app.route('/recognize', methods=['POST'])
def recognize_speech():
    audio_data = request.files['audio_data']
    audio_path = 'data\\audio_48k\\tem.wav'
    audio_data.save(audio_path)

    configs = BaseModelConfigs.load(
        "temp_hum_soil\\202312171725\\configs.yaml")

    model = WavToTextModel(model_path=configs.model_path,
                           char_list=configs.vocab, force_cpu=False)
    spectrogram = WavReader.get_spectrogram(
        audio_path, frame_length=configs.frame_length, frame_step=configs.frame_step, fft_length=configs.fft_length)

    padded_spectrogram = np.pad(spectrogram, ((
        0, configs.max_spectrogram_length - spectrogram.shape[0]), (0, 0)), mode="constant", constant_values=0)

    text = model.predict(padded_spectrogram)
    print('text::', text)

    # Sử dụng thư viện SpeechRecognition để nhận dạng giọng nói
    r = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        audio = r.record(source)

    try:
        # Nhận dạng giọng nói từ dữ liệu audio
        text = r.recognize_google(audio)
        

        return json.dumps({'data': text})
    except sr.UnknownValueError:
        if (not text):
            text = 'off'
        return json.dumps({'data': text})
    except sr.RequestError:
        if (not text):
            text = 'off'
        return json.dumps({'data': text})


@socketio.on('auto')
def handle_auto_event(req):
    messageRecv = json.loads(req['data'])
    temp = [[float(messageRecv['soil']), float(
        messageRecv['temp']), float(messageRecv['hum'])]]
    response = predictTemp(temp)
    print(response)
    emit('response', response)


if __name__ == '__main__':
    socketio.run(app)
