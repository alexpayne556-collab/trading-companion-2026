# Scaling AI Systems

From single-session tools to production-grade AI infrastructure.

---

## Scaling Dimensions

AI systems scale across multiple dimensions simultaneously:

| Dimension | Small Scale | Production Scale |
|-----------|-------------|------------------|
| Sessions | Single | Thousands concurrent |
| Users | Individual | Organization/Public |
| Context | Session-local | Persistent/Shared |
| Reliability | Best-effort | SLA-bound |
| Cost | Ad-hoc | Optimized/Budgeted |

---

## Architecture Patterns

### Pattern 1: Stateless Request-Response

Simplest pattern, limited capability:

```
User Request → AI Processing → Response
     │
     └── No state preserved between requests
```

**Pros:** Simple, horizontally scalable
**Cons:** No continuity, no learning

### Pattern 2: Session-Stateful

Maintain state within sessions:

```
┌──────────────────────────────────────┐
│           SESSION BOUNDARY           │
│                                      │
│  Request 1 → Processing → Response   │
│       │          ↓                   │
│       └────→ Session State           │
│                  ↓                   │
│  Request 2 → Processing → Response   │
│                                      │
└──────────────────────────────────────┘
```

**Pros:** Contextual responses, coherent sessions
**Cons:** State management overhead, session affinity

### Pattern 3: User-Persistent

State persists across sessions for a user:

```
┌──────────────────────────────────────────────┐
│              USER STATE STORE                │
│  ┌────────────────────────────────────────┐  │
│  │ Preferences, History, Learnings        │  │
│  └────────────────────────────────────────┘  │
└──────────────────────────────────────────────┘
                     ↑↓
┌──────────────────────────────────────────────┐
│              SESSION LAYER                   │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐     │
│  │Session 1│  │Session 2│  │Session N│     │
│  └─────────┘  └─────────┘  └─────────┘     │
└──────────────────────────────────────────────┘
```

**Pros:** Personalization, long-term learning
**Cons:** Storage costs, privacy complexity

### Pattern 4: Multi-Agent Mesh

Multiple specialized agents coordinating:

```
                    ┌─────────────┐
                    │ COORDINATOR │
                    └──────┬──────┘
           ┌───────────────┼───────────────┐
           ▼               ▼               ▼
    ┌────────────┐  ┌────────────┐  ┌────────────┐
    │ Research   │  │  Builder   │  │ Validator  │
    │   Agent    │  │   Agent    │  │   Agent    │
    └────────────┘  └────────────┘  └────────────┘
           │               │               │
           └───────────────┼───────────────┘
                           ▼
                    ┌─────────────┐
                    │SHARED STATE │
                    └─────────────┘
```

**Pros:** Specialized capabilities, parallel processing
**Cons:** Coordination overhead, consistency challenges

---

## State Management at Scale

### Tiered State Architecture

```python
class ScalableStateManager:
    """
    Manage state across multiple tiers for scale and performance.
    
    Tiers:
    - L1: In-memory (fastest, ephemeral)
    - L2: Session store (fast, session-scoped)
    - L3: User store (persistent, user-scoped)
    - L4: Global store (shared knowledge)
    """
    
    def __init__(self, config: dict):
        self.l1_cache = {}  # In-memory
        self.l2_store = SessionStore(config['session_store'])
        self.l3_store = UserStore(config['user_store'])
        self.l4_store = GlobalStore(config['global_store'])
    
    def get(self, key: str, scope: str) -> any:
        """
        Get value from appropriate tier.
        Falls through: L1 → L2 → L3 → L4
        """
        # Check L1 first
        if key in self.l1_cache:
            return self.l1_cache[key]
        
        # Check appropriate scope
        if scope == 'session':
            value = self.l2_store.get(key)
        elif scope == 'user':
            value = self.l3_store.get(key)
        elif scope == 'global':
            value = self.l4_store.get(key)
        
        # Populate L1 cache
        if value is not None:
            self.l1_cache[key] = value
        
        return value
    
    def set(self, key: str, value: any, scope: str, ttl: int = None):
        """Set value at appropriate tier"""
        self.l1_cache[key] = value
        
        if scope == 'session':
            self.l2_store.set(key, value, ttl or 3600)
        elif scope == 'user':
            self.l3_store.set(key, value)
        elif scope == 'global':
            self.l4_store.set(key, value)
```

### State Partitioning

```python
class StatePartitioner:
    """Partition state for horizontal scaling"""
    
    def __init__(self, num_partitions: int):
        self.num_partitions = num_partitions
        self.partition_stores = [
            PartitionStore(i) for i in range(num_partitions)
        ]
    
    def get_partition(self, key: str) -> int:
        """Consistent hashing for partition assignment"""
        return hash(key) % self.num_partitions
    
    def route(self, key: str) -> PartitionStore:
        """Route to correct partition store"""
        partition = self.get_partition(key)
        return self.partition_stores[partition]
```

---

## Load Management

### Request Queuing

```python
class RequestQueue:
    """Manage request load with queuing"""
    
    def __init__(self, max_concurrent: int, queue_size: int):
        self.max_concurrent = max_concurrent
        self.queue = asyncio.Queue(maxsize=queue_size)
        self.active = 0
    
    async def submit(self, request: dict) -> dict:
        """Submit request, queue if at capacity"""
        if self.active >= self.max_concurrent:
            await self.queue.put(request)
            return await self._wait_for_result(request['id'])
        
        self.active += 1
        try:
            return await self._process(request)
        finally:
            self.active -= 1
            self._process_next_queued()
    
    async def _process_next_queued(self):
        """Process next queued request if any"""
        if not self.queue.empty():
            request = await self.queue.get()
            await self.submit(request)
```

### Rate Limiting

```python
class RateLimiter:
    """Token bucket rate limiter"""
    
    def __init__(self, tokens_per_second: float, max_tokens: int):
        self.rate = tokens_per_second
        self.max_tokens = max_tokens
        self.tokens = max_tokens
        self.last_update = time.time()
    
    def acquire(self, tokens: int = 1) -> bool:
        """Attempt to acquire tokens"""
        self._refill()
        
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False
    
    def _refill(self):
        """Refill tokens based on elapsed time"""
        now = time.time()
        elapsed = now - self.last_update
        self.tokens = min(
            self.max_tokens,
            self.tokens + elapsed * self.rate
        )
        self.last_update = now
```

### Cost Management

```python
class CostManager:
    """Track and manage AI compute costs"""
    
    def __init__(self, budget: float, period_days: int = 30):
        self.budget = budget
        self.period = timedelta(days=period_days)
        self.spending = []
    
    def record_cost(self, amount: float, metadata: dict):
        """Record a cost event"""
        self.spending.append({
            'timestamp': datetime.now(),
            'amount': amount,
            'metadata': metadata
        })
        self._prune_old()
    
    def get_remaining_budget(self) -> float:
        """Get remaining budget for current period"""
        period_spending = sum(s['amount'] for s in self.spending)
        return self.budget - period_spending
    
    def can_afford(self, estimated_cost: float) -> bool:
        """Check if we can afford a request"""
        return self.get_remaining_budget() >= estimated_cost
    
    def get_cost_breakdown(self) -> dict:
        """Breakdown of spending by category"""
        breakdown = {}
        for s in self.spending:
            category = s['metadata'].get('category', 'other')
            breakdown[category] = breakdown.get(category, 0) + s['amount']
        return breakdown
```

---

## Reliability Patterns

### Circuit Breaker

```python
class CircuitBreaker:
    """
    Circuit breaker for AI service calls.
    
    States:
    - CLOSED: Normal operation
    - OPEN: Failing fast, not calling service
    - HALF_OPEN: Testing if service recovered
    """
    
    CLOSED = 'closed'
    OPEN = 'open'
    HALF_OPEN = 'half_open'
    
    def __init__(self, failure_threshold: int, recovery_timeout: int):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.state = self.CLOSED
        self.failures = 0
        self.last_failure = None
    
    def call(self, func, *args, **kwargs):
        """Execute function through circuit breaker"""
        if self.state == self.OPEN:
            if self._should_attempt_recovery():
                self.state = self.HALF_OPEN
            else:
                raise CircuitOpenError()
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise
    
    def _on_success(self):
        """Handle successful call"""
        self.failures = 0
        self.state = self.CLOSED
    
    def _on_failure(self):
        """Handle failed call"""
        self.failures += 1
        self.last_failure = datetime.now()
        
        if self.failures >= self.failure_threshold:
            self.state = self.OPEN
    
    def _should_attempt_recovery(self) -> bool:
        """Check if recovery timeout has elapsed"""
        if self.last_failure is None:
            return True
        elapsed = datetime.now() - self.last_failure
        return elapsed.seconds >= self.recovery_timeout
```

### Retry with Backoff

```python
class RetryPolicy:
    """Retry failed operations with exponential backoff"""
    
    def __init__(self, max_retries: int = 3, base_delay: float = 1.0):
        self.max_retries = max_retries
        self.base_delay = base_delay
    
    async def execute(self, func, *args, **kwargs):
        """Execute with retries"""
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                
                if attempt < self.max_retries:
                    delay = self._calculate_delay(attempt)
                    await asyncio.sleep(delay)
        
        raise last_exception
    
    def _calculate_delay(self, attempt: int) -> float:
        """Exponential backoff with jitter"""
        delay = self.base_delay * (2 ** attempt)
        jitter = random.uniform(0, delay * 0.1)
        return delay + jitter
```

---

## Observability

### Metrics Collection

```python
class MetricsCollector:
    """Collect and report system metrics"""
    
    def __init__(self):
        self.metrics = defaultdict(list)
    
    def record(self, name: str, value: float, tags: dict = None):
        """Record a metric value"""
        self.metrics[name].append({
            'timestamp': datetime.now(),
            'value': value,
            'tags': tags or {}
        })
    
    def get_summary(self, name: str, window_minutes: int = 5) -> dict:
        """Get metric summary for recent window"""
        cutoff = datetime.now() - timedelta(minutes=window_minutes)
        values = [
            m['value'] for m in self.metrics[name]
            if m['timestamp'] > cutoff
        ]
        
        if not values:
            return {'count': 0}
        
        return {
            'count': len(values),
            'min': min(values),
            'max': max(values),
            'mean': sum(values) / len(values),
            'p50': sorted(values)[len(values) // 2],
            'p99': sorted(values)[int(len(values) * 0.99)]
        }

# Key metrics to track
METRICS = [
    'request_latency_ms',
    'tokens_used',
    'cost_usd',
    'error_rate',
    'queue_depth',
    'active_sessions',
    'cache_hit_rate'
]
```

### Distributed Tracing

```python
class Tracer:
    """Simple distributed tracing"""
    
    def __init__(self):
        self.traces = {}
    
    def start_trace(self, trace_id: str = None) -> str:
        """Start a new trace"""
        trace_id = trace_id or str(uuid.uuid4())
        self.traces[trace_id] = {
            'id': trace_id,
            'start': datetime.now(),
            'spans': []
        }
        return trace_id
    
    def add_span(self, trace_id: str, name: str, metadata: dict = None):
        """Add a span to a trace"""
        span = {
            'name': name,
            'timestamp': datetime.now(),
            'metadata': metadata or {}
        }
        self.traces[trace_id]['spans'].append(span)
    
    def end_trace(self, trace_id: str) -> dict:
        """End trace and return full trace data"""
        trace = self.traces.pop(trace_id, None)
        if trace:
            trace['end'] = datetime.now()
            trace['duration_ms'] = (trace['end'] - trace['start']).total_seconds() * 1000
        return trace
```

---

## Deployment Patterns

### Blue-Green Deployment

```
┌─────────────────────────────────────────┐
│              LOAD BALANCER              │
└────────────────────┬────────────────────┘
                     │
         ┌───────────┴───────────┐
         │                       │
    ┌────▼────┐            ┌────▼────┐
    │  BLUE   │            │  GREEN  │
    │ (live)  │            │ (staged)│
    └─────────┘            └─────────┘
         │                       │
         └───────────┬───────────┘
                     │
              ┌──────▼──────┐
              │SHARED STATE │
              └─────────────┘
```

Switch traffic between blue and green deployments for zero-downtime updates.

### Canary Releases

```
Traffic: 100%
         │
    ┌────┴────────────────────┐
    │ 95%                5%   │
    ▼                    ▼
┌───────┐          ┌───────┐
│STABLE │          │CANARY │
│  v1   │          │  v2   │
└───────┘          └───────┘
```

Route small percentage of traffic to new version, monitor, then expand.

---

## Conclusion

Scaling AI systems requires attention to:

1. **State management** — Tiered storage, partitioning
2. **Load handling** — Queuing, rate limiting, cost control
3. **Reliability** — Circuit breakers, retries, fallbacks
4. **Observability** — Metrics, tracing, alerting
5. **Deployment** — Zero-downtime updates, canary releases

The patterns here provide building blocks for production-grade AI infrastructure.
