<template>
  <div class="">
    <!-- 顶部标题 -->
    <div class="text-gray-900 font-bold text-2xl leading-8">ZenSnack</div>
    <p class="text-base leading-6 text-gray-600">像“吃零食”一样轻松、快捷地构建你的Agent应用</p>
    <!-- 错误提示占位符 -->
    <div class="h-8 text-red-700 leading-8 line-clamp-1">{{ errorMessage }}</div>
    <!-- 登录表单 -->
    <a-form
      :model="loginForm"
      layout="vertical"
      size="large"
      class="flex flex-col w-full"
      @submit="handleSubmit"
    >
      <a-form-item
        field="email"
        :rules="[{ type: 'email', required: true, message: '登录账号必须是合法的邮箱' }]"
        :validate-trigger="['change', 'blur']"
        hide-label
      >
        <a-input v-model="loginForm.email" size="large" placeholder="登录账号">
          <template #prefix>
            <icon-user />
          </template>
        </a-input>
      </a-form-item>
      <a-form-item
        field="password"
        :rules="[{ required: true, message: '账号密码不能为空' }]"
        :validate-trigger="['change', 'blur']"
        hide-label
      >
        <a-input-password v-model="loginForm.password" size="large" placeholder="账号密码">
          <template #prefix>
            <icon-lock />
          </template>
        </a-input-password>
      </a-form-item>
      <a-space :size="16" direction="vertical">
        <div class="flex justify-between">
          <!-- <a-checkbox>记住密码</a-checkbox> -->
          <a-link @click="forgetPassword">忘记密码？</a-link>
        </div>
        <a-button :loading="passwordLoading" size="large" type="primary" html-type="submit" long>
          登录
        </a-button>
        <a-divider>第三方授权</a-divider>
        <a-button :loading="githubLoading" size="large" type="dashed" long @click="githubLogin">
          <template #icon>
            <icon-github />
          </template>
          Github
        </a-button>
      </a-space>
    </a-form>
  </div>
</template>

<script setup lang="ts">
import { passwordLogin } from '@/services/auth'
import { provider } from '@/services/oauth'
import { useCredentialStore } from '@/stores/credential'
import { Message } from '@arco-design/web-vue'
import type { ValidatedError } from '@arco-design/web-vue/es/form/interface'
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
const errorMessage = ref('')
const passwordLoading = ref(false)
const githubLoading = ref(false)
const loginForm = reactive({ email: '', password: '' })
const credentialStore = useCredentialStore()
const router = useRouter()

// 定义忘记密码点击事件
const forgetPassword = () => Message.error('忘记密码请联系管理员')

// 定义github第三方授权认证登录
const githubLogin = async () => {
  try {
    githubLoading.value = true
    const resp = await provider('github')
    window.location.href = resp.data.redirect_url
  } finally {
    githubLoading.value = false
  }
}

// 账号密码登录
const handleSubmit = async ({ errors }: { errors: Record<string, ValidatedError> | undefined }) => {
  if (errors) {
    return
  }

  try {
    passwordLoading.value = true
    const resp = await passwordLogin(loginForm.email, loginForm.password)
    Message.success('登录成功')
    credentialStore.update(resp.data)
    await router.replace({
      path: '/home',
    })
  } catch (error: any) {
    errorMessage.value = error.message
  } finally {
    passwordLoading.value = false
  }
}
</script>
