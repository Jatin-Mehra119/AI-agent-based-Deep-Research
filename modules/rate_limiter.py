import time
import asyncio

class TokenBucket:
    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity
        self.tokens = capacity
        self.refill_rate = refill_rate  # tokens per second
        self.last_update = time.time()
        self.lock = asyncio.Lock()

    async def consume(self, tokens: int):
        async with self.lock:
            current_time = time.time()
            elapsed = current_time - self.last_update
            self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
            self.last_update = current_time

            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            else:
                deficit = tokens - self.tokens
                wait_time = deficit / self.refill_rate
                await asyncio.sleep(wait_time)
                self.tokens = 0
                self.last_update = time.time()
                return True

def groq_token_estimator(text: str) -> int:
    """Approximate token count assuming ~3.5 characters per token."""
    return max(1, int(len(str(text)) / 3.5))

# Create a global token bucket instance (6000 tokens per minute, i.e. 100 tokens/sec)
token_bucket = TokenBucket(6000, 100)

async def rate_limited_execute(model_call, *args, **kwargs):
    """
    Wrapper to enforce rate limits before calling the model.
    Expects a list of messages in kwargs and optionally max_tokens.
    """
    input_tokens = sum(groq_token_estimator(msg.content) for msg in kwargs.get('messages', []))
    output_tokens = kwargs.get('max_tokens', 2000)
    total_tokens = input_tokens + output_tokens

    await token_bucket.consume(total_tokens)
    return await model_call(*args, **kwargs)