
# 为什么需要维护hitTestingForm和retrievalSettingForm两个变量，为什么不能用一个呢
## 召回测试编辑弹窗流程
用户点击"检索设置"按钮：
1. retrievalSettingForm = hitTestingForm 的副本 ← 复制当前设置
2. 用户在模态窗中修改 retrievalSettingForm
3. 用户点击"取消"：
   - retrievalSettingForm = hitTestingForm ← 恢复原始值
   - 模态窗关闭
4. 用户点击"保存"：
   - hitTestingForm = retrievalSettingForm ← 应用新设置
   - 模态窗关闭
   - 使用新设置重新进行检索
