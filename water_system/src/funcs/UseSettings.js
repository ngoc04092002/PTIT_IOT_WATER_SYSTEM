import {reactive} from 'vue';

export function UseSettings(){
    const settings = reactive({show:false});

    return settings;
}
