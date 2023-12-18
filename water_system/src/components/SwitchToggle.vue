<template>
  <div class="switch_toggle">
    <div class="panel panel-default">
      <div class="panel-heading">
        <h3 class="panel-title">{{ title }}</h3>
      </div>
      <div class="panel-body">
        <!--Only code you need is this label-->
        <label class="switch">
          <input :disabled="!['default', ''].includes(mode.mode) && type!='auto'" :checked="checkbox" type="checkbox" @click="$emit('toggleSwitch')" />
          <div class="slider round"></div>
        </label>
        <p>{{ checkbox ? 'Bật' : 'Tắt' }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { defineProps, inject } from 'vue';
const { checkbox, title, type } = defineProps(['checkbox', 'title', 'type']);
const mode = inject('MODE');
</script>

<style scoped>
.switch_toggle {
  display: flex;
  justify-content: center;
}
.panel-body {
  display: flex;
  align-items: center;
  flex-direction: column;
}
.switch {
  position: relative;
  display: inline-block;
  width: 60px;
  height: 34px;
}

.switch input {
  display: none;
}

.slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #ccc;
  -webkit-transition: 0.4s;
  transition: 0.4s;
}

.slider:before {
  position: absolute;
  content: '';
  height: 26px;
  width: 26px;
  left: 4px;
  bottom: 4px;
  background-color: white;
  -webkit-transition: 0.4s;
  transition: 0.4s;
}

input:checked + .slider {
  background-color: #101010;
}

input:focus + .slider {
  box-shadow: 0 0 1px #101010;
}

input:checked + .slider:before {
  -webkit-transform: translateX(26px);
  -ms-transform: translateX(26px);
  transform: translateX(26px);
}

.slider.round {
  border-radius: 34px;
}

.slider.round:before {
  border-radius: 50%;
}
</style>
