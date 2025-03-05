# Rate Limiter Module Documentation

The  rate_limiter.py  module provides rate limiting functionality using the token bucket algorithm, particularly designed for managing API request rates to LLM services like Groq.

## Classes

### TokenBucket

Implements the token bucket algorithm for rate limiting API calls.

-   **__init__(capacity: int, refill_rate: float)**
    
    -   capacity: Maximum number of tokens the bucket can hold
    -   refill_rate: Rate at which tokens are refilled (tokens per second)
-   **async consume(tokens: int) -> bool**
    
    -   Consumes tokens from the bucket, waiting if necessary
    -   Parameters:
        -   tokens: Number of tokens to consume
    -   Returns:  `True`  when tokens have been successfully consumed
    -   Behavior:
        -   If enough tokens are available, consumes them immediately
        -   If not enough tokens, waits until sufficient tokens are available
        -   Thread-safe using asyncio locks

## Functions

### groq_token_estimator(text: str) -> int

Estimates the number of tokens in a text string for Groq API requests.

-   **Parameters**:
    -   text: The text to estimate tokens for
-   **Returns**: Estimated token count
-   **Implementation**: Uses an approximation of 3.5 characters per token

### async rate_limited_execute(model_call, *args, **kwargs)

A wrapper function to enforce rate limits before calling an LLM model API.

-   **Parameters**:
    -   model_call: The async function that makes the actual API call
    -   `*args`: Positional arguments to pass to the model call
    -   `**kwargs`: Keyword arguments to pass to the model call, expected to contain:
        -   `messages`: List of message objects with  content  attributes
        -   `max_tokens`: (Optional) Maximum number of tokens in the response
-   **Returns**: The result from the model call
-   **Behavior**:
    -   Calculates total tokens (input + expected output)
    -   Waits for rate limit if necessary
    -   Executes the model call after rate limiting

## Global Variables

-   **token_bucket**: A global TokenBucket instance configured for 6000 tokens per minute (100 tokens/sec)