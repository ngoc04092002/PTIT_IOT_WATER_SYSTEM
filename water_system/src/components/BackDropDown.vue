<template>
  <div @click.self="closeSettings" v-if="props.settings.show" class="backdrop_container">
    <div class="backdrop_form">
      <div class="backdrop_setting-header">
        <h1>Cài đặt</h1>
        <p @click="closeSettings">x</p>
      </div>
      <div style="padding: 12px; margin-top: 10px">
        <label class="select" for="modes"
          ><select id="modes" required="required" v-model="selected">
            <option value="" disabled="disabled" selected="selected">Các chế độ:</option>
            <option value="default">Mặc định</option>
            <option value="auto">Tự động</option>
            <option value="timer">Hẹn giờ</option></select
          ><svg>
            <use xlink:href="#select-arrow-down"></use></svg></label
        ><!-- SVG Sprites--><svg class="sprites">
          <symbol id="select-arrow-down" viewbox="0 0 10 6">
            <polyline points="1 1 5 5 9 1"></polyline>
          </symbol>
        </svg>
      </div>
      <router-view></router-view>
      <button-setting :selected="selected" @handle-save="handleSave" />
    </div>
  </div>
</template>

<script setup>
import { defineProps, inject, onBeforeMount, provide, ref, watch } from 'vue';
import { useRouter } from 'vue-router';
import ButtonSetting from '../components/ButtonSetting.vue';

const selected = ref('');
const props = defineProps(['settings']);
const router = useRouter();
const mode = inject('MODE');
const checkbox = inject('CHECKBOX');
const client = inject('CLIENT');
const indexs = inject('INDEXS');
const measure = inject('MEASURE');
const checkboxModeAuto = inject('CHECKBOXMODEAUTO');
const checkboxUI = ref(false);

provide('CHECKBOXUI', checkboxUI);

onBeforeMount(()=>{
  selected.value = router.currentRoute.value.path.substring(1);
})

function closeSettings() {
  // eslint-disable-next-line vue/no-mutating-props
  props.settings.show = false;
}

// check mode default
watch(measure, (newValue, oldValue) => {
  if (
    parseFloat(indexs.temp) < parseFloat(newValue.temp) ||
    parseFloat(indexs.hum) < parseFloat(newValue.hum) ||
    parseFloat(indexs.soil) < parseFloat(newValue.soil)
  ) {
    console.log(1);
    checkbox.value = false;
    client.value.publish('BTL_N26/switch', '0', { qos: 0, retain: false });
  }
});

function handleSave() {
  console.log('save');

  if (mode.mode === 'auto' && selected.value !== 'auto') {
    checkboxModeAuto.value = false;
    checkboxUI.value = false;
    console.log(2);
    client.value.publish('BTL_N26/switch', '0', { qos: 0, retain: false });
  }

  if(mode.mode === 'timer' && selected.value !== 'timer'){
    client.value.publish('BTL_N26/switch', '0', { qos: 0, retain: false });
  }

  mode.mode = selected.value;
  if (!['default', ''].includes(mode.mode)) {
    checkbox.value = false;
    console.log(3);
    client.value.publish('BTL_N26/switch', '0', { qos: 0, retain: false });
  }

  if (selected.value === 'auto') {
    checkboxModeAuto.value = checkboxUI.value;
  }

  closeSettings();
}

// eslint-disable-next-line no-unused-vars
watch(selected, (newSelected, _) => {
  console.log(mode);
  router.push({ path: newSelected });
});
</script>

<style scoped>
.select {
  position: relative;
  min-width: 200px;
}
.select svg {
  position: absolute;
  right: 12px;
  top: calc(50% - 3px);
  width: 10px;
  height: 6px;
  stroke-width: 2px;
  stroke: #9098a9;
  fill: none;
  stroke-linecap: round;
  stroke-linejoin: round;
  pointer-events: none;
}

.select select {
  -webkit-appearance: none;
  padding: 7px 40px 7px 12px;
  width: 100%;
  border: 1px solid #e8eaed;
  border-radius: 5px;
  background: white;
  box-shadow: 0 1px 3px -2px #9098a9;
  cursor: pointer;
  font-family: inherit;
  font-size: 16px;
  transition: all 150ms ease;
}
.select select:required:invalid {
  color: #5a667f;
}
.select select option {
  color: #223254;
}
.select select[value=''][disabled] {
  display: none;
}

.select select:focus {
  outline: none;
  border-color: #0077ff;
  box-shadow: 0 0 0 2px rgba(#0077ff, 0.2);
}

.select select:hover + svg {
  stroke: #0077ff;
}
.sprites {
  position: absolute;
  width: 0;
  height: 0;
  pointer-events: none;
  user-select: none;
}
.backdrop_container {
  left: -8px;
  top: -8px;
  height: 100vh;
  width: 100vw;
  position: absolute;
  z-index: 2;
  background-color: rgb(141 137 137 / 57%);
}
.backdrop_setting-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
}
.backdrop_setting-header p {
  font-size: 35px;
  cursor: pointer;
  padding: 16px;
  margin: 0;
}
.backdrop_container .backdrop_form {
  width: 50%;
  height: 100%;
  background-color: white;
}
</style>
