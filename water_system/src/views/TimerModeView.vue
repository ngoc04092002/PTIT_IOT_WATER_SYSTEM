<template>
  <div class="container_timer_mode">
    <div class="container_timer_mode-header">
      <h3>Thiết lập hẹn giờ</h3>
      <span @click="handleAdd">+</span>
    </div>
    <div class="time_dates-scheduled">
      <TimerModeItem
        v-for="(timer, index) in timers"
        :index="index"
        :timer="timer"
        :key="timer.date"
        @handle-delete="handleDelete"
      />
    </div>
    <div class="time_date">
      <div>
        <label for="time"> Bắt đầu: </label>
        <input type="time" id="time" v-model="timer.startTime" />
      </div>
      <div>
        <label for="time"> Kết thúc: </label>
        <input type="time" id="time" v-model="timer.endTime" />
      </div>
      <div>
        <label for="date"> Ngày: </label>
        <input type="date" id="date" v-model="timer.date" />
      </div>
    </div>
  </div>
</template>

<script setup>
import TimerModeItem from '../components/TimerModeItem.vue';
import { inject, ref, watch } from 'vue';
import { UseFormatDate } from '../funcs/UseFormatDate';

const timer = ref({
  startTime: '',
  endTime: '',
  date: ''
});
const timers = ref(JSON.parse(localStorage.getItem('timers')) || []);
const changed = inject('CHANGED');

watch(changed, (newV, oldV) => {
  console.log('change timer==>',newV);
  timers.value = JSON.parse(localStorage.getItem('timers')) || [];
});

function handleAdd() {
  const [currentDate, time] = UseFormatDate(new Date()).split(' ');
  timers.value = timers.value.filter((timer) => timer.date >= currentDate && timer.startTime >= time);
  if (
    timer.value.startTime <= time ||
    timer.value.startTime >= timer.value.endTime ||
    timer.value.date < currentDate
  ) {
    alert('Thời gian không hợp lệ!!');
    return;
  }
  const lastTimer = timers.value.at(-1);
  if (!timer.value.startTime || !timer.value.endTime || !timer.value.date) return;
  const data = {
    id: (lastTimer?.id || 0) + 1,
    email: sessionStorage.getItem('email'),
    startTime: timer.value.startTime,
    endTime: timer.value.endTime,
    date: timer.value.date
  };
  timers.value.push(data);

  fetch('http://127.0.0.1:5000/insert-schedule', {
    method: 'POST',
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data)
  })
    .then((response) => {
      return response.json();
    }).then(data=>{
      console.log(data);
    })

  timer.value = {
    startTime: '',
    endTime: '',
    date: ''
  };
  localStorage.setItem('timers', JSON.stringify(timers.value));
  changed.value += 1;
}

function handleDelete(id) {
  timers.value = JSON.parse(localStorage.getItem('timers'));
  timers.value = timers.value.filter((timer) => timer.id !== id);
  localStorage.setItem('timers', JSON.stringify(timers.value));
  changed.value += 1;
}
</script>

<style scoped>
.container_timer_mode {
  height: 360px;
  display: flex;
  flex-direction: column;
  padding: 12px;
}

.container_timer_mode-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.container_timer_mode-header span {
  cursor: pointer;
  padding: 12px;
  font-size: 32px;
}

.time_date {
  display: flex;
  align-items: center;
  justify-content: space-around;
}
.time_dates-scheduled {
  margin: 12px 0 20px;
  overflow-y: scroll;
  height: 100%;
}

::-webkit-scrollbar {
  width: 12px;
}

/* Track */
::-webkit-scrollbar-track {
  box-shadow: inset 0 0 5px grey;
  border-radius: 4px;
}

/* Handle */
::-webkit-scrollbar-thumb {
  background: hsl(190deg, 30%, 15%);
  border-radius: 4px;
}
</style>
