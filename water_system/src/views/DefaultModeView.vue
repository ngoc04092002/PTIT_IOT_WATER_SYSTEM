<template>
  <div class="container_default_mode">
    <h3>Thiết lập giới hạn</h3>
    <div class="container_default_mode-value">
      <label for="temp">Nhiệt độ:</label
      ><input id="temp" type="number" placeholder="37ºC" v-model="indexs.temp" />
    </div>
    <div class="container_default_mode-value">
      <label for="hum">Độ ẩm:</label
      ><input id="hum" type="number" placeholder="32%" v-model="indexs.hum" />
    </div>
    <div class="container_default_mode-value">
      <label for="soil">Độ ẩm đất:</label
      ><input id="soil" type="number" placeholder="30%" v-model="indexs.soil" />
    </div>
  </div>
</template>

<script setup>
import { inject } from 'vue';

const indexs = inject('INDEXS');
</script>

<style scoped>
.container_default_mode {
  height: 360px;
  display: flex;
  flex-direction: column;
  padding: 12px;
}
.container_default_mode-value {
  margin-top: 20px;
}

.container_default_mode-value label {
  margin-right: 20px;
}

.container_default_mode-value input {
  padding: 6px 12px;
}
</style>
