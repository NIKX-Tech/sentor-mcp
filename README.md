# Sentor MCP Server

Connect Sentor's entity-based sentiment analysis to Claude, Cursor, Windsurf, and any MCP-compatible AI assistant.

## What It Does

Once installed, your AI assistant gains four tools:

| Tool | What it does |
|------|-------------|
| `analyze_sentiment` | Score sentiment toward specific entities in any text |
| `cluster_documents` | Group 5+ documents by topic automatically (BERTopic) |
| `name_topic` | Generate a 3-5 word label for each cluster using LLM |
| `health_check` | Verify Sentor API is reachable |

**Example prompt after setup:** *"Analyze these 50 customer reviews for sentiment toward our checkout flow and shipping speed, then cluster them by topic."*

## Requirements

- Python 3.10+
- A Sentor API key → [Get one free at dashboard.sentor.app](https://dashboard.sentor.app/settings?tab=api-access)

## Installation

```bash
pip install sentor-mcp
```

## Claude Desktop Setup

Add to your `claude_desktop_config.json`:

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`  
**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "sentor": {
      "command": "sentor-mcp",
      "env": {
        "SENTOR_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

Restart Claude Desktop. You'll see the Sentor tools available in the tool selector.

## Cursor / Windsurf Setup

Add to your MCP config file (`.cursor/mcp.json` or equivalent):

```json
{
  "mcpServers": {
    "sentor": {
      "command": "sentor-mcp",
      "env": {
        "SENTOR_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

## Usage Examples

Once connected, use natural language:

**Sentiment analysis:**
> "Use Sentor to analyze the sentiment of these reviews toward Apple and iPhone: [paste reviews]"

**Clustering:**
> "I have 200 customer support tickets. Use Sentor to cluster them by topic and name each cluster."

**Full pipeline:**
> "Analyze sentiment in these 100 reviews for 'delivery' and 'packaging' entities, then cluster them and name each cluster."

## Tool Reference

### `analyze_sentiment(docs, language="en")`

```python
docs = [
    {
        "doc_id": "review_1",
        "doc": "The delivery was fast but the packaging was terrible.",
        "entities": ["delivery", "packaging"]
    }
]
# Returns: predicted_label, probabilities, per-sentence details
```

### `cluster_documents(documents, language="en")`

```python
documents = [
    {"doc_id": "r1", "text": "Great product quality", "entities": ["product"]},
    # ... at least 5 documents required
]
# Returns: clusters with cluster_id, documents, top_words
```

### `name_topic(cluster_id, documents, top_words, entities, language="en")`

```python
# Pass the cluster data from cluster_documents response:
name_topic(
    cluster_id=0,
    documents=cluster["documents"],
    top_words=cluster["top_words"],
    entities=["BrandName"]  # exclude your brand from the topic label
)
# Returns: topic_name (e.g. "Shipping Delay Complaints")
```

### `health_check()`

```python
# Returns: { "status": "healthy", "version": "...", "llm_status": "available" }
```

## Rate Limits

| Plan | Per Minute | Per Month |
|------|-----------|-----------|
| Free | 3 | 300 |
| Starter | 60 | 3,000 |
| Growth | 200 | 15,000 |
| Business | 500 | 60,000 |
| Enterprise | 10,000 | Unlimited |

## Remote Deployment (HTTP/SSE)

To run as a hosted server:

```bash
docker build -t sentor-mcp .
docker run -e SENTOR_API_KEY=your_key -p 8080:8080 sentor-mcp
```

The server exposes SSE at `http://localhost:8080/sse` and can be connected to AI tools that support remote MCP servers.

## Links

- [Sentor Dashboard](https://dashboard.sentor.app)
- [API Documentation](https://sentor.app/docs)
- [MCP Integration Guide](https://sentor.app/docs/integrations/mcp)
- [Support](mailto:sentor@nikx.one)
