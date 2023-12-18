<!-- eslint-disable no-unused-vars -->
<script setup>
import { ref, defineProps, provide, onMounted, reactive, inject, onBeforeMount, watch } from 'vue';
import SwitchToggle from '../components/SwitchToggle.vue';
import ButtonRecord from '../components/ButtonRecord.vue';
import BackDropDown from '../components/BackDropDown.vue';
import { UseSettings } from '../funcs/UseSettings';
import { useRoute } from 'vue-router';

import { io } from 'socket.io-client';

const props = defineProps(['measure']);
const checkbox = ref(false);
const settings = UseSettings();
const loading = ref(false);
const SocketServer = ref(null);
const selectedMode = inject('SELECTEDMODE');
const route = useRoute();
const indexs = reactive({
  temp: '100',
  hum: '100',
  soil: '100'
});
const checkboxModeAuto = ref(false);

provide('CHECKBOXMODEAUTO', checkboxModeAuto);
provide('INDEXS', indexs);
provide('SocketServer', SocketServer);
provide('MODE', selectedMode);
provide('CHECKBOX', checkbox);

const client = inject('CLIENT');

onBeforeMount(() => {
  selectedMode.mode = route.path.substring(1);
});

function showSettings() {
  settings.show = true;
}

watch([props.measure, selectedMode, checkboxModeAuto], ([newMeasure, newMode, newMo]) => {
  if (newMo && newMode.mode === 'auto') {
    //send socket to server
    SocketServer.value.emit('auto', { data: JSON.stringify(newMeasure) });
  }
});

function toggleCheckbox() {
  if (['default', ''].includes(selectedMode.mode)) {
    checkbox.value = !checkbox.value;
    console.log(6);
    client.value.publish('BTL_N26/switch', checkbox.value ? '1' : '0', { qos: 0, retain: false });
  } else {
    console.log(7);
    checkbox.value = false;
    client.value.publish('BTL_N26/switch', '0', { qos: 0, retain: false });
  }
}

function handleRecord(text) {
  console.log(text);
}

onMounted(() => {
  SocketServer.value = io('http://localhost:5000');

  SocketServer.value.on('connect_error', () => {
    console.log('error');
  });

  // client-side
  SocketServer.value.on('connect', () => {
    console.log('Connected socket');
    SocketServer.value.emit('schedule_init', 'start send email');

    const engine = SocketServer.value.io.engine;
    SocketServer.value.on('response', (response) => {

      // called for each packet received
      console.log('response-auto', response);

      if (selectedMode.mode === 'auto') {
        if (response === '1') {
          client.value.publish('BTL_N26/switch', '1', { qos: 0, retain: false });
        } else {
          client.value.publish('BTL_N26/switch', '0', { qos: 0, retain: false });
        }
      }
    });

    console.log(SocketServer.value.id); // x8WIv7-mJelg7on_ALbx
  });

  SocketServer.value.on('disconnect', () => {
    console.log('Disconnected socket');
    console.log(SocketServer.value.id); // undefined
  });

  // initServer();
});
</script>

<template>
  <div class="manage">
    <div class="head">
      <img @click="showSettings" class="manage-img" src="../assets/setting.png" alt="settings" />
      <div style="display: flex; width: 100%">
        <h1 class="manage-title">Quản lý hệ thống</h1>
        <span
          style="
            padding: 10px;
            line-height: 2;
            text-transform: capitalize;
            background-color: chartreuse;
            font-family: sans-serif;
            font-size: 14px;
            font-weight: bold;
          "
          class="box"
          >Chế độ: {{ selectedMode.mode || 'MODE' }}</span
        >
      </div>
    </div>
    <div class="indexs">
      <div class="box">
        <p style="color: red">
          Nhiệt độ <img class="img_temp" src="../assets/temperature.png" alt="temperature" />
        </p>
        <span>{{ props.measure.temp }}ºC</span>
      </div>
      <div class="box">
        <p style="color: blue">
          Độ ẩm <img class="img_temp" src="../assets/humidity.png" alt="humidity" />
        </p>
        <span>{{ props.measure.hum }}%</span>
      </div>
      <div class="box">
        <p style="color: brown">
          Độ ẩm đất <img class="img_temp" src="../assets/measurement.png" alt="measurement" />
        </p>
        <span>{{ props.measure.soil }}%</span>
      </div>
    </div>
  </div>
  <div class="btns-control">
    <switch-toggle :checkbox="checkbox" @toggle-switch="toggleCheckbox" title="Công tắc" />
    <div>
      <h3>Nhận diện giọng nói</h3>
      <button-record @handle-record="handleRecord" :checkbox="checkbox" />
    </div>
  </div>
  <BackDropDown :settings="settings" />
</template>

<style scoped>
.btns-control {
  margin-top: 90px;
  display: flex;
  align-items: center;
  justify-content: space-around;
}
.head {
  display: flex;
  align-items: center;
}
.img_temp {
  width: 20px;
  height: 20px;
  object-fit: cover;
  object-position: center;
}

.indexs {
  font-size: 30px;
  font-weight: bold;
  margin-top: 20px;
  display: flex;
  align-items: center;
  justify-content: space-around;
}

.box {
  background-color: white;
  text-align: center;
  padding: 40px;
  border-radius: 8px;
  box-shadow: 0 0 10px 3px;
}
.box > p {
  margin-top: 0;
  font-family: monospace;
}

.indexs span {
  margin: 0 30px;
}
.manage-img {
  cursor: pointer;
  margin: 20px;
  width: 32px;
  height: 32x;
  object-fit: cover;
  object-position: center;
}
.manage-title {
  margin: 0 auto;
  text-transform: uppercase;
  font-weight: bold;
  font-size: 40px;
}
</style>
