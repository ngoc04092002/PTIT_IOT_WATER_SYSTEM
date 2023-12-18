<template>
  <div class="time_dates-schedule--item">
    <div class="time_date-item">
      <div style="margin-right: 40px">
        <span> Bắt đầu: </span>
        <span>{{ props.timer.startTime }}</span>
      </div>
      <div style="margin-right: 40px">
        <span> Kết thúc: </span>
        <span>{{ props.timer.endTime }}</span>
      </div>
      <div>
        <span> Ngày: </span>
        <span>{{ props.timer.date }}</span>
      </div>
    </div>
    <span
      style="cursor: pointer; font-size: 32px; padding: 12px"
      @click="$emit('handleDelete', props.timer.id)"
      >x</span
    >
  </div>
</template>

<script setup>
const props = defineProps(['timer']);
</script>

<style scoped>
.time_dates-schedule--item,
.time_date-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
</style>
