<template>
  <!-- 召回测试模态窗 -->
  <!-- todo -->
  <a-modal
    :width="1000"
    :visible="visible"
    hide-title
    :footer="false"
    modal-class="rounded-xl h-3/4 overflow-auto scrollbar-w-none"
  >
    <!-- 顶部标题 -->
    <div class="flex items-center justify-between">
      <div class="text-lg font-bold text-gray-700">召回测试</div>
      <a-button type="text" class="!text-gray-700" size="small">
        <template #icon>
          <icon-close />
        </template>
      </a-button>
    </div>
    <!-- 副标题 -->
    <div class="text-gray-500">基于给定的查询文本测试知识库的召回效果</div>
    <!-- 中间内容区 -->
    <div class="pt-6">
      <div class="w-full flex justify-between gap-2">
        <!-- 左侧输入框以及最近查询 -->
        <div class="flex flex-col w-1/2">
          <!-- 顶部输入框 -->
          <div class="border border-blue-700 bg-blue-100 rounded-lg flex flex-col mb-6">
            <!-- 输入框标题 -->
            <div class="flex items-center justify-between px-4 py-1.5">
              <div class="font-bold text-gray-900">源文本</div>
              <!-- todo -->
              <a-button size="small" class="rounded-lg px-2">
                <template #icon>
                  <icon-language />
                </template>
                <div>混合检索</div>
              </a-button>
            </div>
            <!-- 输入框容器 -->
            <div class="bg-white rounded-lg p-2">
              <!-- 输入框 -->
              <!-- todo -->
              <a-textarea
                placeholder="请输入文本，建议使用简短的陈述句"
                :max-length="200"
                :auto-size="{ minRows: 6, maxRows: 6 }"
                class="!bg-white !border-0 mb-1"
              />
              <!-- 字符限制以及召回按钮 -->
              <div class="flex items-center justify-between">
                <a-tag size="small" class="rounded text-gray-700"> 0/200 </a-tag>
                <!-- todo -->
                <a-button type="primary" size="small" class="rounded-lg"> 召回测试 </a-button>
              </div>
            </div>
          </div>
          <!-- 底部最近查询 -->
          <div class="">
            <div class="text-gray-700 font-bold mb-4">最近查询</div>
            <!-- todo -->
            <a-table :pagination="false" size="small" :bordered="{ wrapper: false }">
              <template #columns>
                <a-table-column
                  title="数据源"
                  data-index="source"
                  header-cell-class="text-gray-500 bg-transparent border-b font-bold"
                  cell-class="text-gray-500"
                  :width="110"
                />
                <a-table-column
                  title="文本"
                  data-index="query"
                  header-cell-class="text-gray-500 bg-transparent border-b font-bold"
                  cell-class="text-gray-500"
                >
                  <template #cell="{ record }">
                    <div class="line-clamp-1">{{ record.query }}</div>
                  </template>
                </a-table-column>
                <a-table-column
                  title="时间"
                  data-index="created_at"
                  header-cell-class="text-gray-500 bg-transparent border-b font-bold"
                  cell-class="text-gray-500"
                  :width="160"
                >
                  <template #cell="{ record }">
                    <div class="">
                      {{ moment(record.created_at * 1000).format('YYYY-MM-DD HH:mm') }}
                    </div>
                  </template>
                </a-table-column>
              </template>
            </a-table>
          </div>
        </div>
        <a-divider direction="vertical" />
        <!-- 右侧召回列表 -->
        <div class="w-1/2">
          <!-- todo -->
          <a-spin class="w-full">
            <!-- 有数据状态 -->
            <a-row :gutter="[16, 16]">
              <a-col :span="12">
                <div class="p-4 bg-gray-50 rounded-lg cursor-pointer">
                  <!-- 顶部得分部分 -->
                  <!-- todo -->
                  <div class="flex items-center gap-2 mb-1.5">
                    <icon-pushpin />
                    <a-progress :stroke-width="6" :show-text="false" :percent="0.1" />
                    <div class="text-gray-700 text-xs">0.1</div>
                  </div>
                  <!-- 中间内容部分 -->
                  <div class="text-gray-500 line-clamp-4 h-[88px] break-all">片段内容</div>
                  <!-- 文档归属信息 -->
                  <a-divider class="my-2" />
                  <div class="flex items-center gap-2 text-gray-500 text-xs">
                    <icon-file class="flex-shrink-0" />
                    <div class="line-clamp-1">片段文档名称</div>
                  </div>
                </div>
              </a-col>
            </a-row>
            <a-empty />
          </a-spin>
        </div>
      </div>
    </div>
  </a-modal>
  <!-- 检索设置模态窗 -->
  <a-modal
    :visible="retrievalSettingModalVisible"
    hide-title
    :footer="false"
    modal-class="rounded-xl"
  >
    <!-- 顶部标题 -->
    <div class="flex items-center justify-between">
      <div class="text-lg font-bold text-gray-700">检索设置</div>
      <!-- todo -->
      <a-button type="text" class="!text-gray-700" size="small">
        <template #icon>
          <icon-close />
        </template>
      </a-button>
    </div>
    <!-- 中间表单内容 -->
    <a-form class="pt-6">
      <a-form-item field="retrieval_strategy" label="检索策略" label-align="left">
        <a-radio-group
          default-value="semantic"
          :options="[
            { label: '混合策略', value: 'hybrid' },
            { label: '全文检索', value: 'full_text' },
            { label: '相似性检索', value: 'semantic' },
          ]"
        />
      </a-form-item>
      <a-form-item field="k" label="最大召回数量">
        <div class="flex items-center gap-4 w-full pl-3">
          <a-slider :step="1" :min="1" :max="10" />
          <a-input-number class="w-[80px]" :default-value="4" />
        </div>
      </a-form-item>
      <a-form-item field="score" label="最小匹配度">
        <div class="flex items-center gap-4 w-full pl-3">
          <a-slider :step="1" :min="0" :max="0.99" />
          <a-input-number class="w-[80px]" :min="0" :max="0.99" :step="0.01" :percision="2" :default-value="0.5" />
        </div>
      </a-form-item>
      <!-- 底部按钮 -->
       <div class="flex items-center justify-between">
        <div></div>
        <a-space :size="16">
          <a-button class="rounded-lg">取消</a-button>
          <a-button type="primary" html-type="submit" class="rounded-lg">保存</a-button>
        </a-space>
       </div>
    </a-form>
  </a-modal>
</template>

<script setup lang="ts">
import moment from 'moment'
import { ref } from 'vue'

const props = defineProps({
  visible: {
    type: Boolean,
    required: true,
  },
})

const retrievalSettingModalVisible = ref(true)
</script>
