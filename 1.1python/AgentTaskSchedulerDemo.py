from collections import deque, defaultdict, Counter
import heapq
# AgentTaskScheduler 示例、实现与测试
# -----------------------------
# 前置示例（示范用法）
# -----------------------------

# 1. 对话历史窗口（自动丢弃最旧的）
chat_history = deque(maxlen=5)
messages = [
    "Hello, how can I assist you today?",
    "I need help with my research.",
    "Sure, what topic are you researching?",
    "I'm looking into the effects of climate change."]
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

# 题目：Agent 任务调度器
# 实现一个 AgentTaskScheduler 类，支持以下功能：
# add_task(priority, task_id, payload)：添加任务，priority 为整数（越小越优先）
# get_next_task()：返回优先级最高的任务；若同优先级，按先进先出顺序返回
# peek_tasks(n)：返回当前优先级最高的 N 个任务（不删除）
# 要求：使用 heapq，并处理同优先级时的 FIFO 问题（提示：引入自增计数器打破平局）。

# -----------------------------
# 实现：AgentTaskScheduler
# -----------------------------
class AgentTaskScheduler:
    def __init__(self):
        self.task_queue = []
        self.counter = 0  # 自增计数器，用于处理同优先级的 FIFO 问题

    def add_task(self, priority, task_id, payload):
        # 使用负数优先级，因为 heapq 是最小堆
        heapq.heappush(self.task_queue, (priority, self.counter, task_id, payload))
        self.counter += 1

    def get_next_task(self):
        if not self.task_queue:
            return None
        priority, count, task_id, payload = heapq.heappop(self.task_queue)
        return (priority, task_id, payload)

    def peek_tasks(self, n):
        # 获取当前优先级最高的 N 个任务（不删除），返回 (priority, task_id, payload)
        top = sorted(self.task_queue)[:n]
        return [(priority, task_id, payload) for (priority, _, task_id, payload) in top]


#验证方式：运行以下测试用例应全部通过：
scheduler = AgentTaskScheduler()
scheduler.add_task(2, "t1", {"tool": "search"})
scheduler.add_task(1, "t2", {"tool": "parse"})
scheduler.add_task(1, "t3", {"tool": "summarize"})
assert scheduler.get_next_task() == (1, "t2", {"tool": "parse"})
assert scheduler.get_next_task() == (1, "t3", {"tool": "summarize"})
assert scheduler.peek_tasks(1) == [(2, "t1", {"tool": "search"})]