<template>
  <div class="container">
    <input type="checkbox" id="btn" @click="checkt" ref="startBtn" />
    <label for="btn"></label>
    <p class="tim" id="timer" ref="timer">0</p>
  </div>
</template>

<script setup>
import { ref, defineEmits, inject } from 'vue';

const start = ref(false);
const interval = ref(null);
const startBtn = ref(null);
const timer = ref(null);
const time = ref(0);

const emit = defineEmits(['handleRecord']);

let gumStream; //stream from getUserMedia()
let rec; //Recorder.js object
let input; //MediaStreamAudioSourceNode we'll be recording

// shim for AudioContext when it's not avb.
const AudioContext = window.AudioContext || window.webkitAudioContext;
let audioContext; //audio context to help us record

function checkt() {
  // eslint-disable-next-line vue/no-mutating-props
  if (startBtn.value.checked == true) {
    startRecording();
    interval.value = setInterval(function () {
      if (parseInt(time.value) == 10) {
        document.getElementById('timer').style.color = '#000';
      }
      if (parseInt(time.value) == 20) {
        clearInterval(interval);
        document.getElementById('btn').checked = false;
        document.getElementById('timer').value = 0;
        document.getElementById('timer').style.color = '#fff';
      }
      time.value += 1 / 100;
      timer.value.innerHTML = time.value.toFixed(2);
    }, 10);
    start.value = !start.value;
  } else {
    emit('handleRecord', time.value);
    time.value = 0;
    stopRecording();
    clearInterval(interval.value);
    start.value = !start.value;
  }
}

const selectedMode = inject('SELECTEDMODE');
const client = inject('CLIENT');

function startRecording() {
  console.log('recordButton clicked');
  selectedMode.mode = '';
  client.value.publish('BTL_N26/switch', '0', { qos: 0, retain: false });

  const constraints = { audio: true, video: false };
  navigator.mediaDevices
    .getUserMedia(constraints)
    .then(function (stream) {
      console.log('getUserMedia() success, stream created, initializing Recorder.js ...');
      audioContext = new AudioContext();

      console.log('Sample rate mới: ' + audioContext.sampleRate);
      /*  assign to gumStream for later use  */
      gumStream = stream;
      /* use the stream */
      input = audioContext.createMediaStreamSource(stream);
      /*
            Create the Recorder object and configure to record mono sound (1 channel)
            Recording 2 channels  will double the file size
        */

      // eslint-disable-next-line no-undef
      rec = new Recorder(input, { numChannels: 1 });

      //start the recording process
      rec.record();

      console.log('Recording started');
    })
    .catch(function (err) {
      //enable the record button if getUserMedia() fails
      console.log('error start record::', err);
    });
}

function stopRecording() {
  console.log('stopButton clicked');

  //tell the recorder to stop the recording
  rec.stop();

  //stop microphone access
  gumStream.getAudioTracks()[0].stop();

  rec.exportWAV(requestToServer);
}

function requestToServer(blob) {
  const fd = new FormData();
  fd.append('audio_data', blob);
  //send http
  fetch('http://127.0.0.1:5000/recognize', {
    method: 'POST',
    body: fd
  })
    .then((response) => {
      return response.json();
    })
    .then((data) => {
      console.log(data);

      if (data.data.includes('on')) {
        client.value.publish('BTL_N26/switch', '1', { qos: 0, retain: false });
      } else {
        client.value.publish('BTL_N26/switch', '0', { qos: 0, retain: false });
      }
    })
    .catch((e) => {
      console.log(e);
    });
}
</script>

<style scoped>
body {
  overflow: hidden;
  background: #fff;
}
.container {
  position: relative;
  width: 170px;
  margin: 0 auto;
  height: 170px;
}
.container #btn {
  display: none;

  width: 60px;
  height: 60px;
  position: relative;
  left: 50px;
  /* top: 55px; */
}

.container #btn + label:before {
  position: absolute;
  left: 50%;
  top: 50%;
  width: 130px;
  height: 130px;
  margin: -65px -65px;
  content: '';
  -webkit-transform: translate(-6px, -6px);
  -ms-transform: translate(-6px, -6px);
  transform: translate(-6px, -6px);
  border-radius: 50%;
  border: 6px solid #000;
  cursor: pointer;
}
.container #btn + label:after {
  position: absolute;
  left: 50%;
  top: 50%;
  width: 100px;
  height: 100px;
  margin: -50px -50px;
  content: '';
  border-radius: 50px;
  background: #e80415;
  cursor: pointer;
}
.container #btn:checked + label:after {
  -webkit-animation: stop 0.5s infinite cubic-bezier(0.4, -0.9, 0.9, 1);
  -moz-animation: stop 0.5s infinite cubic-bezier(0.4, -0.9, 0.9, 1);
  -o-animation: stop 0.5s infinite cubic-bezier(0.4, -0.9, 0.9, 1);
  animation: stop 0.5s infinite cubic-bezier(0.4, -0.9, 0.9, 1);
  -webkit-animation-iteration-count: 1;
  animation-iteration-count: 1;
  -webkit-animation-fill-mode: forwards;
  animation-fill-mode: forwards;
}
@keyframes stop {
  70% {
    border-radius: 6px;
    position: absolute;
    left: 50%;
    top: 50%;
    width: 60px;
    height: 60px;
    margin: -30px -30px;
  }
  100% {
    border-radius: 6px;
    position: absolute;
    left: 50%;
    top: 50%;
    width: 64px;
    height: 64px;
    margin: -32px -32px;
  }
}

#timer {
  position: relative;
  top: 42%;
  bottom: 0;
  font-size: 20px;
  font-weight: bold;
  color: #fff;
  text-align: center;
  opacity: 0;
}

.container #btn:checked ~ label ~ .tim {
  opacity: 1;
}
</style>
