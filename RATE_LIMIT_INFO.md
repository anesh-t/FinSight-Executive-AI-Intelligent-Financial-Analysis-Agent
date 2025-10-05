# ⚠️ OpenAI Rate Limit Information

## Current Issue

You're experiencing OpenAI API rate limits. This happens when:

1. **Too many requests** in a short time period
2. **Token usage** exceeds your tier limits
3. **Concurrent requests** from the same API key

## Error Messages You Might See

- `Rate limit reached for gpt-3.5-turbo`
- `You exceeded your current quota`
- `Output parsing error` (can be caused by rate limiting)

## Solutions

### **Immediate Fix: Wait**
- Wait 1-2 minutes between queries
- The rate limit resets automatically

### **Short-term Fix: Reduce Token Usage**
Already implemented:
- ✅ Shortened system prompts
- ✅ Reduced max iterations from 15 to 10
- ✅ Smaller data samples in prompts
- ✅ Removed visualization generation

### **Long-term Fixes**

1. **Upgrade OpenAI Tier**
   - Go to: https://platform.openai.com/account/billing
   - Add payment method
   - Higher tiers = higher rate limits

2. **Use Caching**
   - Cache common queries
   - Reuse results when possible

3. **Batch Queries**
   - Wait longer between requests
   - Process queries in batches

## Current Rate Limits (Free Tier)

- **Requests per minute:** 3
- **Tokens per minute:** 40,000
- **Requests per day:** 200

## Recommended Usage

- **Wait 20-30 seconds** between queries
- **Use simpler queries** to reduce token usage
- **Check your usage:** https://platform.openai.com/usage

## Testing Without Rate Limits

You can test the database connection directly:

```bash
python test_connection.py
```

This doesn't use the LLM, so no rate limits apply.
