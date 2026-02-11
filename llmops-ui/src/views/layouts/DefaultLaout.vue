<template>
  <a-layout has-sider class="h-full">
    <!-- 侧边栏 -->
    <a-layout-sider :width="240" class="min-h-screen bg-gray-50 p-2 shadow-none">
      <div class="bg-white h-full rounded-lg px-2 py-4 flex flex-col justify-between">
        <!-- 上半部分 -->
        <div class="">
          <!-- 顶部logo -->
          <router-link
            to="/home"
            class="block mb-5 transition-all rounded-lg text-3xl font-bold text-gray-900 text-center"
          >
            ZenSnack
          </router-link>
          <!-- 创建AI应用按钮 -->
          <router-link :to="{name: 'space-apps-list', query: {'create_type': 'app'}}">
            <a-button type="primary" long class="rounded-lg mb-4">
              <template #icon>
                <icon-plus />
              </template>
              创建 AI 应用
            </a-button>
          </router-link>
          <!-- 侧边栏布局 -->
          <left-siderbar />
        </div>
        <!-- 账号设置 -->
        <a-dropdown position="tl">
          <div
            class="flex items-center p-2 gap-2 transition-all cursor-pointer rounded-lg hover:bg-gray-100"
          >
            <!-- 头像 -->
            <a-avatar
              :size="32"
              class="text-sm bg-blue-700"
              :image-url="accountStore.account.avatar"
            >
              {{ accountStore.account.name[0] }}
            </a-avatar>
            <!-- 个人信息 -->
            <div class="flex flex-col">
              <div class="text-sm text-gray-900">{{ accountStore.account.name }}</div>
              <div class="text-xs text-gray-500">{{ accountStore.account.email }}</div>
            </div>
          </div>
          <template #content>
            <a-doption @click="settingModalVisible = true">
              <icon-settings />
              账号设置
            </a-doption>
            <a-doption @click="handleLogout">
              <icon-poweroff />
              退出登录
            </a-doption>
          </template>
        </a-dropdown>
      </div>
    </a-layout-sider>
    <!-- 右侧内容 -->
    <a-layout-content>
      <router-view />
    </a-layout-content>
  </a-layout>
  <!-- 设置模态窗 -->
  <setting-modal v-model:visible="settingModalVisible" />
</template>

<script setup lang="ts">
import LeftSiderbar from './components/LeftSiderbar.vue'
import SettingModal from '@/views/layouts/components/SettingModal.vue'

import { useRouter } from 'vue-router'
import { onMounted, ref } from 'vue'
import { useCredentialStore } from '@/stores/credential'
import { useAccountStore } from '@/stores/account'
import { logout } from '@/services/auth'
import { getCurrentUser } from '@/services/account'
import { Message, Modal } from '@arco-design/web-vue'

const router = useRouter()
const credentialStore = useCredentialStore()
const accountStore = useAccountStore()

const settingModalVisible = ref(false)

// 退出登录
const handleLogout = () => {
  Modal.info({
    content: '确定退出当前账号吗？',
    hideCancel: false,
    onOk: async () => {
      // 清空授权凭证+账号信息
      credentialStore.clear()
      accountStore.clear()

      // 发起请求退出登录
      await logout()

      // 跳转授权认证页面
      await router.replace({ name: 'auth-login' })

      Message.info('你已退出登录')
    },
  })
}

onMounted(async () => {
  const resp = await getCurrentUser()

  accountStore.update(resp.data)
})
</script>
