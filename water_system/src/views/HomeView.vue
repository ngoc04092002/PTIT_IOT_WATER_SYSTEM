<script setup>
import { onBeforeMount, onMounted, provide, reactive, ref, watch } from 'vue';
import ManageView from './ManageView.vue';
import { UseFormatDate } from '../funcs/UseFormatDate';

function validationIp(ipAddress) {
  const splitIpAddress = ipAddress.value.split('.');

  if (splitIpAddress.length !== 4) return false;

  for (let ip of splitIpAddress) {
    if (!ip.length || isNaN(+ip) || +ip > 255 || +ip < 0) {
      return false;
    }
  }

  return true;
}

const ipAddress = ref('');
const checkIp = ref(false);
const isConnected = ref(false);
const loading = ref(false);
const measure = reactive({ temp: '0', hum: '0', soil: '0' });
const client = ref(null);
const eventChanged = ref(1);
const selectedMode = reactive({ mode: '' });

provide('SELECTEDMODE', selectedMode);
provide('CLIENT', client);
provide('CHANGED', eventChanged);
provide('MEASURE', measure);

onBeforeMount(() => {
  console.log(sessionStorage.getItem('ip'));
  if (sessionStorage.getItem('ip')) {
    isConnected.value = true;
  }
});

console.log(checkIp.value);

function handleClickConnect() {
  if (validationIp(ipAddress)) {
    loading.value = true;
    isConnected.value = true; // need tp be removed
    sessionStorage.setItem('ip', ipAddress.value);
  } else {
    checkIp.value = true;
  }
}

onMounted(() => {
  const clientId = 'mqttjs_' + Math.random().toString(16).substr(2, 8);
  const host = 'ws://broker.hivemq.com:8000/mqtt';
  const options = {
    keepalive: 60,
    clientId: clientId,
    username: 'BTL_IOT',
    password: 'Btliot123',
    protocolId: 'MQTT',
    protocolVersion: 4,
    clean: true,
    reconnectPeriod: 1000,
    connectTimeout: 30 * 1000,
    will: {
      topic: 'WillMsg',
      payload: 'Connection Closed abnormally..!',
      qos: 0,
      retain: false
    }
  };
  console.log('Connecting mqtt client');
  // eslint-disable-next-line no-undef
  client.value = mqtt.connect(host, options);

  client.value.on('error', (err) => {
    console.log('Connection error: ', err);
    loading.value = false;
    client.value.end();
  });
  client.value.on('reconnect', () => {
    console.log('Reconnecting...');
  });
  client.value.on('connect', () => {
    console.log(`Client connected: ${clientId}`);
    isConnected.value = true;
    loading.value = false;
    client.value.subscribe('BTL_N26/temp', { qos: 2 });
    client.value.subscribe('BTL_N26/hum', { qos: 2 });
    // client.value.subscribe('BTL_N26/switch', { qos: 2 });
    client.value.subscribe('BTL_N26/soil', { qos: 2 });
  });

  client.value.on('message', (topic, message, packet) => {
    switch (topic) {
      case 'BTL_N26/temp':
        measure.temp = message.toString();
        break;
      case 'BTL_N26/hum':
        measure.hum = message.toString();
        break;
      case 'BTL_N26/soil':
        measure.soil = message.toString();
        break;
      // case 'BTL_N26/switch':
      //   measure.switch = message.toString();
      //   break;
    }
  });
});

let intervalId = null;

watch([eventChanged, selectedMode], (newV, newV2) => {
  clearInterval(intervalId);

  if (selectedMode.mode !== 'timer') {
    return;
  }

  const [currentDate] = UseFormatDate(new Date()).split(' ');

  let timers = JSON.parse(localStorage.getItem('timers'));
  let checkWateringDate = timers.find((time) => time.date === currentDate);
  let id = checkWateringDate?.id;

  if (id) {
    let lock = false;
    intervalId = setInterval(() => {
      console.log(lock);
      const [, time] = UseFormatDate(new Date()).split(' ');
      if (!lock && time >= checkWateringDate.startTime && time <= checkWateringDate.endTime) {
        console.log(4);
        client.value.publish('BTL_N26/switch', '1', { qos: 0, retain: false });
        lock = true;
      }

      if (time > checkWateringDate.endTime && lock) {
        client.value.publish('BTL_N26/switch', '0', { qos: 0, retain: false });

        console.log('id==>', id);
        console.log('timers==>', timers);
        const newTimers = timers.filter((time) => parseInt(time.id) !== parseInt(id));
        timers = newTimers;
        console.log('newTimers==>', newTimers);

        localStorage.setItem('timers', JSON.stringify(newTimers));
        checkWateringDate = newTimers.find((time) => time.date === currentDate);

        if (checkWateringDate?.id) {
          id = parseInt(checkWateringDate?.id);
          lock = false;
        }
        eventChanged.value += 1;
      }
    }, 1000);
  }
});
</script>

<template>
  <div class="home-container" v-if="!isConnected">
    <h1 class="title">Hệ thống tưới cây</h1>
    <div class="home-wrapper">
      <input
        :class="{ 'has-error': checkIp }"
        type="text"
        placeholder="Ex: 192.168.0.1"
        v-model.trim="ipAddress"
      />
      <button class="btn-connect" @click="handleClickConnect" :disabled="loading">
        {{ loading ? 'Đang kết nối' : 'Kết nối' }}
      </button>
    </div>
    <div class="text-danger" :class="{}" v-if="checkIp">
      <span>Địa chỉ chưa chính xác!</span>
    </div>
  </div>
  <div v-else-if="isConnected">
    <manage-view :measure="measure" />
  </div>
</template>

<style scoped>
.home-container {
  margin-top: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
}
.title {
  text-transform: uppercase;
  font-weight: bold;
  font-size: 40px;
}
.has-error {
  color: #cc0202;
  border: 2px solid #cc0202;
}
.text-danger {
  display: flex;
  justify-content: center;
}
.text-danger span {
  font-weight: bold;
  color: #cc0202;
}
.home-wrapper {
  margin-top: 130px;
}

input {
  border-radius: 5px;
  outline: none;
  border: none;
  padding: 12px;
  width: 260px;
}

.btn-connect {
  padding: 12px;
  cursor: pointer;
  outline: none;
  border: none;
  border-radius: 5px;
  background-color: #cad3d3;
  font-weight: bold;
}
.btn-connect:hover {
  background-color: #cad3d3d6;
}
</style>
