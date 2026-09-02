from datetime import datetime, timedelta, timezone
from decimal import Decimal

try:
    import numpy as np  # type: ignore
except ModuleNotFoundError:
    np = None

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

### 验证代码题

# **题目：Agent 会话超时管理器**

# 实现 `SessionTimeoutManager` 类，管理多个 Agent 会话的过期时间。

# 要求：
# 1. `create_session(session_id, ttl_seconds)`：创建会话，记录创建时间，`ttl_seconds` 后过期
# 2. `is_expired(session_id)` -> bool：判断会话是否已过期（基于当前 UTC 时间）
# 3. `time_remaining(session_id)` -> float：返回剩余存活秒数，已过期返回 0
# 4. `extend_session(session_id, extra_seconds)`：延长会话存活时间

# **约束**：使用 `datetime.datetime`（带 `timezone.utc`），禁止使用 `time.time()`。

class SessionTimeoutManager:
    def __init__(self):
        self.sessions = {}  # 存储 session_id -> (创建时间, ttl_seconds)

    def create_session(self, session_id, ttl_seconds):
        now = datetime.now(timezone.utc)
        self.sessions[session_id] = (now, ttl_seconds)

    def is_expired(self, session_id):
        if session_id not in self.sessions:
            return True
        created_time, ttl = self.sessions[session_id]
        return datetime.now(timezone.utc) >= created_time + timedelta(seconds=ttl)

    def time_remaining(self, session_id):
        if session_id not in self.sessions:
            return 0
        created_time, ttl = self.sessions[session_id]
        remaining = (created_time + timedelta(seconds=ttl)) - datetime.now(timezone.utc)
        return max(0, remaining.total_seconds())

    def extend_session(self, session_id, extra_seconds):
        if session_id in self.sessions:
            created_time, ttl = self.sessions[session_id]
            new_ttl = ttl + extra_seconds
            self.sessions[session_id] = (created_time, new_ttl)

#**验证方式**：

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
print("SessionTimeoutManager 测试通过")