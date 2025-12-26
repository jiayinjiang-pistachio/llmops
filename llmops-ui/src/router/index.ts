import { createRouter, createWebHistory } from 'vue-router'
import BlankLayout from '@/views/layouts/BlankLayout.vue'
import DefaultLaout from '@/views/layouts/DefaultLaout.vue'
import { isLogin } from '@/utils/auth'
// import HomeView from '@/views/HomeView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      component: () => DefaultLaout,
      children: [
        {
          path: '',
          redirect: 'home',
        },
        {
          path: 'home',
          name: 'pages-home',
          component: () => import('@/views/pages/HomeView.vue'),
        },
        // 应用列表页
        {
          path: 'space/apps',
          name: 'space-apps-list',
          component: () => import('@/views/space/apps/ListView.vue'),
        },
        // 自定义API插件列表页
        {
          path: 'space/tools',
          name: 'space-tools-list',
          component: () => import('@/views/space/tools/ListView.vue'),
        },
        // 应用广场页
        {
          path: 'store/apps',
          name: 'stores-apps-list',
          component: () => import('@/views/store/apps/ListView.vue'),
        },
        // 内置插件列表页
        {
          path: 'store/tools',
          name: 'stores-tools-list',
          component: () => import('@/views/store/tools/ListView.vue'),
        },
        // 开放API页
        {
          path: 'open',
          name: 'open-index',
          component: () => import('@/views/open/IndexView.vue'),
        }
      ],
    },
    {
      path: '/',
      component: BlankLayout,
      children: [
        {
          path: 'auth/login',
          name: 'auth-login',
          component: () => import('@/views/auth/LoginView.vue'),
        },
        {
          path: 'space/apps/:app_id',
          name: 'space-apps-detail',
          component: () => import('@/views/space/apps/DetailView.vue'),
        },
      ],
    },
  ],
})

router.beforeEach(async (to) => {
  if (!isLogin() && to.name !== 'auth-login') {
    return {
      path: '/auth/login',
    }
  }
})

export default router
