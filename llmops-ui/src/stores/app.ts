import { defineStore } from 'pinia';
import { ref } from 'vue';

export const useAppStore = defineStore('useAppStore', () => {
  const getDraftAppConfigFlag = ref(false)
  const setGetDraftAppConfigFlag = (newValue: boolean) => getDraftAppConfigFlag.value = newValue

  const getAppFlag = ref(false)
  const setGetAppFlag = (newValue: boolean) => getAppFlag.value = newValue

  return {
    getDraftAppConfigFlag,
    setGetDraftAppConfigFlag,
    getAppFlag,
    setGetAppFlag,
  }
})
