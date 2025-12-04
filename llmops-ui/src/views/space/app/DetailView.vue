<template>
  <div class="">
    <a-button @click="handleFetch">发起请求</a-button>
  </div>
</template>

<style lang="less"></style>

<script setup lang="ts">
import { post } from '@/utils/request';
import { } from 'vue'

const handleFetch = async () => {
  const resp = await post('/app/50d5ab41-7319-4c34-8a69-91ff77c3c7dd/debug', {
    body: {
      query: '你好，你是谁？'
    }
  })

  console.log(resp)
}
</script>
