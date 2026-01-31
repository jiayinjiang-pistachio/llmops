// api接口前缀
export const apiPrefix = 'http://127.0.0.1:5000'

// 业务状态码
export const httpCode = {
  success: 'success',
  fail: 'fail',
  notFound: 'not_found',
  unauthorized: 'unauthorized',
  forbidden: 'forbidden',
  validateError: 'validate_error',
}

// 类型字符串与中文映射
export const typeMap: Record<string, string> = {
  int: '整型',
  float: '浮点型',
  str: '字符串',
  bool: '布尔值',
}

// 智能体事件类型
export const QueueEvent = {
  longTermMemoryRecall: 'long_term_memory_recall',
  agentThought: 'agent_thought',
  agentMessage: 'agent_message',
  agentAction: 'agent_action',
  datasetRetrieval: 'dataset_retrieval',
  agentEnd: 'agent_end',
  stop: 'stop',
  error: 'error',
  timeout: 'timeout',
  ping: 'ping',
}

export const NODE_DATA_MAP: Record<string, any> = {
  start: {
    title: '开始节点',
    description: '工作流的起始节点，支持定义工作流的起点输入等信息。',
    inputs: [],
  },
  llm: {
    title: '大语言模型',
    description: '调用大语言模型，根据输入参数和提示词生成回复。',
    prompt: '',
    model_config: {},
    inputs: [],
    outputs: [{ name: 'output', type: 'string', vlaue: { type: 'generated', content: '' } }],
  },
  tool: {
    title: '扩展插件',
    description: '调用插件广场内或自定义API插件，支持能力扩展和复用。',
    tool_type: '',
    provider_id: '',
    tool_id: '',
    params: {},
    inputs: [],
    outputs: [{ name: 'text', type: 'string', value: { type: 'generated', content: '' } }],
  },
  dataset_retrieval: {
    title: '知识库检索',
    description: '根据输入的参数，在选定的知识库中检索相关片段并召回，返回切片列表。',
    dataset_ids: [],
    retrieval_config: {
      retrieval_strategy: 'semantic',
      k: 4,
      score: 0,
    },
    inputs: [{ name: 'query', type: 'string', value: { type: 'literal', content: '' } }],
    outputs: [
      { name: 'combine_documents', type: 'string', value: { type: 'generated', content: '' } },
    ],
  },
  template_transform: {
    title: '模板转换',
    description: '对多个字符串变量的格式进行处理。',
    template: '',
    inputs: [],
    outputs: [{ name: 'output', type: 'string', value: { type: 'generated', content: '' } }],
  },
  http_request: {
    title: 'HTTP请求',
    description: '配置外部API服务，并发起请求。',
    method: 'get',
    url: '',
    headers: {},
    body: '',
    inputs: [],
    outputs: [
      { name: 'status_code', type: 'int', value: { type: 'generated', content: 0 } },
      { name: 'text', type: 'string', value: { type: 'generated', content: '' } },
    ],
  },
  code: {
    title: 'Python代码执行',
    description: '编写代码，处理输入输出变量来生成返回值。',
    code: '',
    inputs: [],
    outputs: [],
  },
  end: {
    title: '结束节点',
    description: '工作流的结束节点，支持定义工作流最终输出的变量等信息。',
    outputs: [],
  },
}
