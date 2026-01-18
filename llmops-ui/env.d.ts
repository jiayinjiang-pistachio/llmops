/// <reference types="vite/client" />
declare module 'vue-virtual-scroller' {
  import { ComponentOptions, Plugin } from 'vue'
  const VueVirtualScroller: Plugin
  export const RecycleScroller: ComponentOptions
  export const DynamicScroller: ComponentOptions
  export const DynamicScrollerItem: ComponentOptions
  export default VueVirtualScroller
}
