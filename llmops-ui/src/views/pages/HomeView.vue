<template>
  <div class="">
    homeview
    <div>{{ accountStore.account.name }}</div>
    <div>{{ accountStore.account.email }}</div>
    <a-button type="primary" @click="update">修改信息</a-button>
    <a-button type="primary" @click="reset">重置</a-button>
  </div>
</template>

<style lang="less">

</style>

<script setup lang="ts">
import {} from 'vue'
import { useAccountStore } from '@/stores/account';

const accountStore = useAccountStore()

const update = () => {
  accountStore.update({
    name: '小小课'
  })
}
const reset = () => {
  accountStore.clear()
}
</script>


