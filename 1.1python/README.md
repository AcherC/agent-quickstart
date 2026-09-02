 总结《Python Cookbook》第三版（David Beazley & Brian K. Jones）前四章核心内容，结合 **Agent 全栈开发** 的实际场景进行提炼，每章末尾配有一道实战代码题。

---

## 第 1 章：Data Structures and Algorithms（数据结构与算法）

### 核心知识点

| 知识点 | Agent 开发场景 | 关键要点 |
|--------|---------------|---------|
| **解包与解压序列** | 从 LLM 返回的元组/列表中提取多字段结果 | `first, *rest = items`；用 `*` 捕获剩余元素 |
| **保留最近 N 个元素** | Agent 对话历史窗口、最近 N 条日志 | `collections.deque(maxlen=N)`，O(1) 两端操作 |
| **优先级队列** | Agent 任务调度（按优先级执行 Tool Call） | `heapq.heappush/pop`，底层是二叉堆，不是完全排序 |
| **字典多值映射** | 一个 Agent 对应多个 Tool/一个 Session 多条 Message | `collections.defaultdict(list)` |
| **有序字典/去重** | 保持 Tool 调用顺序且去重 | `dict.fromkeys()` 或 `collections.OrderedDict` |
| **字典推导与分组** | 按类型分组管理 Tools | `itertools.groupby` 需先排序；或用字典推导 |
| **切片命名** | 解析固定格式日志/协议头 | `slice(start, stop)` 赋值给变量提高可读性 |
| **Counter 统计** | Token 频次统计、Tool 使用频率分析 | `collections.Counter.most_common(n)` |

### 核心代码示例

```python
from collections import deque, defaultdict, Counter
import heapq

# 1. 对话历史窗口（自动丢弃最旧的）
chat_history = deque(maxlen=5)
for msg in messages:
    chat_history.append(msg)

# 2. 优先级任务队列（数字越小优先级越高）
tasks = []
heapq.heappush(tasks, (1, "call_search_tool"))
heapq.heappush(tasks, (0, "parse_user_intent"))
priority, task = heapq.heappop(tasks)  # -> (0, "parse_user_intent")

# 3. 一个 Agent 映射多个 Tools
agent_tools = defaultdict(list)
agent_tools["researcher"].append("web_search")
agent_tools["researcher"].append("arxiv_search")

# 4. 快速统计词频
words = ["tool", "agent", "tool", "llm", "agent", "tool"]
top3 = Counter(words).most_common(3)  # [('tool', 3), ('agent', 2), ('llm', 1)]
```

### 验证代码题

**题目：Agent 任务调度器**

实现一个 `AgentTaskScheduler` 类，支持以下功能：
1. `add_task(priority, task_id, payload)`：添加任务，`priority` 为整数（越小越优先）
2. `get_next_task()`：返回优先级最高的任务；若同优先级，按**先进先出**顺序返回
3. `peek_tasks(n)`：返回当前优先级最高的 N 个任务（不删除）

**要求**：使用 `heapq`，并处理同优先级时的 FIFO 问题（提示：引入自增计数器打破平局）。

**验证方式**：运行以下测试用例应全部通过：
```python
scheduler = AgentTaskScheduler()
scheduler.add_task(2, "t1", {"tool": "search"})
scheduler.add_task(1, "t2", {"tool": "parse"})
scheduler.add_task(1, "t3", {"tool": "summarize"})
assert scheduler.get_next_task() == (1, "t2", {"tool": "parse"})
assert scheduler.get_next_task() == (1, "t3", {"tool": "summarize"})
assert scheduler.peek_tasks(1) == [(2, "t1", {"tool": "search"})]
```

---

## 第 2 章：Strings and Text（字符串与文本）

### 核心知识点

| 知识点 | Agent 开发场景 | 关键要点 |
|--------|---------------|---------|
| **多行正则匹配** | 从 LLM 输出中提取代码块/JSON | `re.DOTALL` 让 `.` 匹配换行；`re.MULTILINE` 让 `^$` 匹配每行 |
| **非贪婪匹配** | 提取 `<think>...</think>` 标签内容 | `.*?` 非贪婪；`.*` 贪婪 |
| **字符串格式化** | 构造 Prompt 模板 | `str.format()` / f-string；`string.Template` 更安全 |
| **文本对齐与填充** | 格式化日志输出、表格化展示 Agent 状态 | `ljust/rjust/center`；`textwrap.fill` 控制行宽 |
| **Unicode 规范化** | 处理用户输入的多语言文本 | `unicodedata.normalize('NFC', text)` |
| **字节与字符串转换** | 网络协议收发、文件编码处理 | 明确 `encode('utf-8')` / `decode('utf-8')` |
| **Shell 通配符匹配** | 文件名/日志名过滤 | `fnmatch.fnmatch(filename, '*.log')` |

### 核心代码示例

```python
import re
from string import Template
import textwrap

# 1. 从 LLM 输出中提取 <think> 标签内容（非贪婪）
text = "<think>推理中...</think>最终答案是42"
match = re.search(r'<think>(.*?)</think>', text, re.DOTALL)
if match:
    reasoning = match.group(1)

# 2. Prompt 模板（适合从配置文件加载）
prompt_tmpl = Template("""
你是 $role，请使用 $tool 完成以下任务：
$task
""")
prompt = prompt_tmpl.substitute(role="ResearchAgent", tool="web_search", task="查天气")

# 3. 格式化 Agent 状态表格
status = [("Agent", "Status"), ("Planner", "running"), ("Executor", "idle")]
for name, state in status:
    print(f"{name:<10} | {state:>10}")

# 4. 控制输出宽度（适合日志）
log = "Agent completed the task with multiple steps and returned a very long result..."
print(textwrap.fill(log, width=50))
```

### 验证代码题

**题目：LLM 输出解析器**

实现 `LLMOutputParser` 类，解析包含 `<think>`、`<tool_call>`、`<output>` 标签的 LLM 输出字符串。

要求实现以下方法：
1. `extract_think(text)` -> 提取 `<think>...</think>` 内的内容（可能跨多行）
2. `extract_tool_calls(text)` -> 提取所有 `<tool_call>{"name":"xxx","args":{...}}</tool_call>`，返回字典列表
3. `sanitize_prompt(prompt)` -> 移除 prompt 中所有 XML 标签，只保留纯文本

**验证方式**：
```python
parser = LLMOutputParser()
text = """<think>
我需要搜索天气。
</think>
<tool_call>{"name":"search","args":{"q":"北京天气"}}</tool_call>
<output>晴天 25°C</output>"""

assert "我需要搜索天气" in parser.extract_think(text)
assert parser.extract_tool_calls(text)[0]["name"] == "search"
assert "<think>" not in parser.sanitize_prompt(text)
assert "晴天 25°C" in parser.sanitize_prompt(text)
```

---

## 第 3 章：Numbers, Dates, and Times（数字、日期与时间）

### 核心知识点

| 知识点 | Agent 开发场景 | 关键要点 |
|--------|---------------|---------|
| **Decimal 精确计算** | 金额计算、积分系统 | `Decimal('0.1') + Decimal('0.2') == Decimal('0.3')` |
| **大数与进制转换** | 生成唯一 ID、哈希缩短 | `hex()`, `bin()`, `int(x, base)` |
| **日期时间解析** | 解析用户输入的"明天下午三点" | `datetime.strptime()` / `dateutil.parser.parse()` |
| **时区处理** | 跨时区 Agent 日志对齐 | `pytz` 或 Python 3.9+ `zoneinfo` |
| **时间戳转换** | 记录事件时间、缓存过期判断 | `datetime.now(timezone.utc).timestamp()` |
| **日期范围迭代** | 批量生成日报/按天轮询数据 | `datetime.timedelta(days=1)` 循环累加 |
| **numpy 数值计算** | 向量相似度计算（Embedding 比较） | `np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))` |

### 核心代码示例

```python
from datetime import datetime, timedelta, timezone
from decimal import Decimal
import numpy as np

# 1. 精确金额计算（Agent 积分/计费）
price = Decimal('19.99')
discount = Decimal('0.15')
final = price * (Decimal('1') - discount)  # 16.9915

# 2. UTC 时间戳（统一日志时间）
now = datetime.now(timezone.utc)
ts = now.timestamp()  # 秒级时间戳
iso = now.isoformat()  # 2024-09-02T08:30:00+00:00

# 3. 解析用户时间输入
user_input = "2024-09-02 14:30:00"
dt = datetime.strptime(user_input, "%Y-%m-%d %H:%M:%S")

# 4. 生成最近 7 天的日期范围
dates = [datetime.now(timezone.utc) - timedelta(days=i) for i in range(7)]

# 5. 向量余弦相似度（RAG 检索排序）
def cosine_similarity(a, b):
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))
```

### 验证代码题

**题目：Agent 会话超时管理器**

实现 `SessionTimeoutManager` 类，管理多个 Agent 会话的过期时间。

要求：
1. `create_session(session_id, ttl_seconds)`：创建会话，记录创建时间，`ttl_seconds` 后过期
2. `is_expired(session_id)` -> bool：判断会话是否已过期（基于当前 UTC 时间）
3. `time_remaining(session_id)` -> float：返回剩余存活秒数，已过期返回 0
4. `extend_session(session_id, extra_seconds)`：延长会话存活时间

**约束**：使用 `datetime.datetime`（带 `timezone.utc`），禁止使用 `time.time()`。

**验证方式**：
```python
import time
manager = SessionTimeoutManager()
manager.create_session("sess_001", ttl_seconds=2)
assert not manager.is_expired("sess_001")
assert manager.time_remaining("sess_001") > 1.0
time.sleep(2.5)
assert manager.is_expired("sess_001")
assert manager.time_remaining("sess_001") == 0

manager.create_session("sess_002", ttl_seconds=5)
manager.extend_session("sess_002", 3)
assert manager.time_remaining("sess_002") > 7.0
```

---

## 第 4 章：Iterators and Generators（迭代器与生成器）

### 核心知识点

| 知识点 | Agent 开发场景 | 关键要点 |
|--------|---------------|---------|
| **手动迭代协议** | 逐行流式读取大日志文件 | `iter(obj)` 获取迭代器；`next(it, default)` 避免 StopIteration |
| **yield 生成器函数** | 流式输出 LLM Token、分页拉取数据 | 函数含 `yield` 即变为生成器；惰性求值省内存 |
| **yield from 委托** | 多级 Agent 嵌套调用，逐层传递输出 | `yield from sub_generator()` 等价于循环 `yield` |
| **迭代器切片** | 跳过历史消息前 N 条，取最近 M 条 | `itertools.islice(iterable, start, stop)` |
| **dropwhile/takewhile** | 跳过日志头部注释，读取有效数据 | `itertools.dropwhile(predicate, iterable)` |
| **排列组合迭代** | 生成所有可能的 Tool 参数组合进行测试 | `itertools.product`、`permutations`、`combinations` |
| **chain 连接迭代器** | 合并多个数据源（多个 Agent 输出流） | `itertools.chain(a, b, c)` 比 `a + b + c` 省内存 |
| **数据处理管道** | 构建日志分析流水线：找文件→解压→过滤→统计 | 生成器函数串联：`gen_find → gen_opener → gen_concatenate → gen_grep` |

### 核心代码示例

```python
import itertools
import os
import fnmatch

# 1. 流式读取大文件（处理超大规模日志）
def stream_lines(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            yield line.strip()

# 2. 跳过历史消息前 10 条，取接下来 5 条
history = iter(messages)
recent = list(itertools.islice(history, 10, 15))

# 3. 多级 Agent 输出委托
def agent_orchestrator(query):
    yield from intent_classifier(query)   # 子生成器
    yield from tool_selector(query)       # 子生成器
    yield from executor(query)            # 子生成器

# 4. 合并多个 Tool 返回的结果流
def merge_results(*result_streams):
    yield from itertools.chain(*result_streams)

# 5. 数据处理管道：查找所有 .log 文件并产出路径
def gen_find(filepat, top):
    for path, _, filelist in os.walk(top):
        for name in fnmatch.filter(filelist, filepat):
            yield os.path.join(path, name)
```

### 验证代码题

**题目：Agent 流式响应处理器**

实现一个 `StreamingResponseHandler` 类，模拟处理 LLM 的流式输出（逐字/逐句返回）。

要求：
1. `simulate_stream(text, chunk_size=5)`：**生成器函数**，每次产出 `chunk_size` 个字符，模拟流式输出
2. `filter_thinking(stream)`：**生成器函数**，接收上面的流，实时过滤掉 `<think>...</think>` 标签内的内容（假设标签可能跨多个 chunk），只产出非思考内容
3. `count_tokens(stream)`：**生成器函数**，接收流，在产出每个 chunk 的同时，累计已输出的字符数，产出 `(chunk, total_count)` 元组

**验证方式**：
```python
handler = StreamingResponseHandler()
text = "Hello <think>这是内部思考</think> World!"

# 测试 1：流式分块
chunks = list(handler.simulate_stream(text, chunk_size=5))
assert "".join(chunks) == text

# 测试 2：过滤思考内容
filtered = "".join(handler.filter_thinking(handler.simulate_stream(text, chunk_size=3)))
assert "Hello " in filtered
assert "World!" in filtered
assert "内部思考" not in filtered

# 测试 3：计数
result = list(handler.count_tokens(handler.simulate_stream("ABC", chunk_size=1)))
assert result[-1] == ("C", 3)
```

---

## 学习验证建议

除了完成上述 4 道代码题，我还建议你按以下方式自测：

| 验证方式 | 具体操作 |
|---------|---------|
| **代码题自测** | 将每章题目保存为独立 `.py` 文件，用 `pytest` 运行验证用例 |
| **手写速查表** | 不看资料，手写每章 5 个最常用的函数/类及其签名 |
| **场景联想** | 给自己出题："如果我要实现一个 Agent 的 X 功能，应该用第几章的哪个技术？" |
| **源码阅读** | 找 1 个开源 Agent 框架（如 `langchain`、`autogen`），定位它使用 `deque`、`heapq`、`itertools` 的地方 |
