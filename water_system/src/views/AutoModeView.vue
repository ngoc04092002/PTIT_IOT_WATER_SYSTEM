<template>
  <div class="container_auto_mode">
    <h3>Thiết lập tự động</h3>
    <switch-toggle :checkbox="checkbox" @toggle-switch="toggleCheckbox" title="" type="auto" />
  </div>
</template>

<script setup>
import SwitchToggle from '../components/SwitchToggle.vue';

import { inject } from 'vue';

const checkbox = inject('CHECKBOXUI');

function toggleCheckbox() {
  checkbox.value = !checkbox.value;
}
</script>

<style scoped>
.container_auto_mode {
  height: 360px;
  display: flex;
  flex-direction: column;
  padding: 12px;
}
</style>
