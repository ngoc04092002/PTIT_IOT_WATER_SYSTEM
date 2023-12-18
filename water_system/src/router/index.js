import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import DefaultModeView from '../views/DefaultModeView.vue'
import AutoModeView from '../views/AutoModeView.vue'
import TimerModeView from '../views/TimerModeView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
      children: [
          {
            path: 'default',
            component: DefaultModeView,
          },
          {
            path: 'auto',
            component: AutoModeView,
          },
          {
            path: 'timer',
            component: TimerModeView,
          },
      ]
    },
  ]
})

export default router
