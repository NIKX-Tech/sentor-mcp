<!-- markdownlint-disable MD033 -->
# Sentor MCP Server

<img src="https://raw.githubusercontent.com/NIKX-Tech/sentor-mcp/prod/logo.png" width="70" alt="Sentor Logo">

**Entity-based sentiment analysis for Claude, Cursor, Windsurf, and any MCP-compatible AI assistant.**

[![PyPI](https://img.shields.io/pypi/v/sentor-mcp?style=flat-square&logo=python&logoColor=white&label=pypi)](https://pypi.org/project/sentor-mcp/)
[![Python](https://img.shields.io/pypi/pyversions/sentor-mcp?style=flat-square)](https://pypi.org/project/sentor-mcp/)
[![License](https://img.shields.io/github/license/NIKX-Tech/sentor-mcp?style=flat-square&color=blue)](https://opensource.org/licenses/MIT)
[![GitHub Stars](https://img.shields.io/github/stars/NIKX-Tech/sentor-mcp?style=flat-square&color=yellow)](https://github.com/NIKX-Tech/sentor-mcp/stargazers)
<br>
[![Website](https://img.shields.io/badge/website-sentor.app-5546FA?style=flat-square&logo=google-chrome&logoColor=white)](https://sentor.app)
[![Dashboard](https://img.shields.io/badge/get%20api%20key-dashboard.sentor.app-5546FA?style=flat-square)](https://dashboard.sentor.app/settings?tab=api-access)
[![Docs](https://img.shields.io/badge/docs-sentor.app%2Fdocs-5546FA?style=flat-square)](https://sentor.app/docs/integrations/mcp)

Sentor is an entity-based sentiment analysis platform powered by fine-tuned BERT models. This MCP server exposes Sentor's ML APIs as tools your AI assistant can call directly — score sentiment toward specific entities in text, cluster documents by topic, and generate topic labels, all from a single natural-language prompt.

---

## Table of Contents

- [What It Does](#-what-it-does)
- [Requirements](#-requirements)
- [Quick Start](#-quick-start)
  - [Claude Desktop](#claude-desktop)
  - [Cursor / Windsurf](#cursor--windsurf)
  - [Claude.ai Web (Remote MCP)](#claudeai-web-remote-mcp)
- [Tools Reference](#-tools-reference)
- [Usage Examples](#-usage-examples)
- [Rate Limits](#-rate-limits)
- [Remote Deployment](#-remote-deployment)
- [Links](#-links)

---

## 🎯 What It Does

Once connected, your AI assistant gains four tools:

| Tool | What it does |
|------|-------------|
| `analyze_sentiment` | Score sentiment toward named entities (brands, products, features, people) in one or more documents. Returns per-document and per-sentence breakdowns. |
| `cluster_documents` | Group 5+ documents into thematic clusters using BERTopic + HDBSCAN. Automatically discovers the number of clusters. |
| `name_topic` | Generate a 3–5 word descriptive label for each cluster using an LLM (e.g. "Shipping Delay Complaints"). |
| `health_check` | Verify the Sentor API is reachable and ML models are loaded. |

**Example prompt after setup:**
> *"Analyse these 50 customer reviews for sentiment toward our checkout flow and delivery speed. Then cluster them by topic and name each cluster."*

---

## 📋 Requirements

- Python 3.10+
- A Sentor API key — [get one free at dashboard.sentor.app](https://dashboard.sentor.app/settings?tab=api-access)

---

## 🚀 Quick Start

### Claude Desktop

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "sentor": {
      "command": "uvx",
      "args": ["sentor-mcp"],
      "env": {
        "SENTOR_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

Restart Claude Desktop. A hammer icon appears in the tool selector — Sentor is ready.

> **No `uvx`?** Install it with `pip install uv`, or use `sentor-mcp` directly after `pip install sentor-mcp`.

---

### Cursor / Windsurf

Add to `.cursor/mcp.json` (project-level) or `~/.cursor/mcp.json` (global):

```json
{
  "mcpServers": {
    "sentor": {
      "command": "uvx",
      "args": ["sentor-mcp"],
      "env": {
        "SENTOR_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

---

### Claude.ai Web (Remote MCP)

Run the HTTP server and connect by URL:

```bash
docker run -e SENTOR_API_KEY=your_api_key -p 8080:8080 ghcr.io/nikx-tech/sentor-mcp:latest
```

Then in Claude.ai → Settings → Integrations → Add MCP Server:
```
http://your-server:8080/sse
```

---

## 🔧 Tools Reference

### `analyze_sentiment(docs, language="en")`

Analyse entity-level sentiment in one or more documents.

```python
docs = [
    {
        "doc_id": "review-1",
        "doc": "The delivery was fast but the packaging was completely crushed.",
        "entities": ["delivery", "packaging"]
    }
]
# Returns: predicted_label, probabilities, per-sentence details
```

**Supported languages:** `en` (English), `nl` (Dutch)

---

### `cluster_documents(documents, language="en")`

Group documents into thematic clusters. Requires at least 5 documents.

```python
documents = [
    {"doc_id": "r1", "text": "Great product quality, very happy.", "entities": ["product"]},
    # ... at least 5 documents
]
# Returns: clusters with cluster_id, document_count, documents, top_words
# Cluster -1 = outliers that did not fit any topic
```

---

### `name_topic(cluster_id, documents, top_words, entities, language="en")`

Generate a short label for a cluster. Pass data directly from `cluster_documents` output.

```python
name_topic(
    cluster_id=0,
    documents=cluster["documents"],
    top_words=cluster["top_words"],
    entities=["BrandName"],  # exclude your brand from the label
    language="en"
)
# Returns: { "topic_name": "Shipping Delay Complaints", "generation_method": "LLM" }
```

---

### `health_check()`

```python
# Returns: { "status": "healthy", "version": "1.0.0", "llm_status": "available" }
```

---

## 💬 Usage Examples

**Single document:**
> *"Use Sentor to analyse the sentiment of this review toward Apple and iPhone: [paste text]"*

**Batch analysis:**
> *"I have 100 customer reviews. Use Sentor to score sentiment toward 'delivery' and 'support' in each one, then tell me the ratio of positive to negative."*

**Full pipeline:**
> *"Use Sentor to: 1) analyse sentiment in these 200 reviews for 'product quality' and 'price', 2) cluster them by topic, 3) name each cluster, 4) summarise the findings."*

**Competitive analysis:**
> *"Analyse these tweets for sentiment toward Apple, Samsung, and Google separately using Sentor, then compare the results."*

---

## 📊 Rate Limits

| Plan | Per Minute | Per Day | Per Month |
|------|:---------:|:-------:|:---------:|
| **Free** | 3 | 30 | 300 |
| **Starter** | 60 | 500 | 3,000 |
| **Growth** | 200 | 2,000 | 15,000 |
| **Business** | 500 | 5,000 | 60,000 |
| **Enterprise** | Unlimited | Unlimited | Unlimited |

[View full pricing →](https://sentor.app/pricing)

---

## 🐳 Remote Deployment

Run as a hosted HTTP/SSE server for AI tools that support remote MCP endpoints.

**Docker:**

```bash
docker build -t sentor-mcp .
docker run \
  -e SENTOR_API_KEY=your_key \
  -p 8080:8080 \
  sentor-mcp
```

The server exposes:
- `GET /sse` — SSE stream (MCP transport)
- `POST /messages` — message endpoint

**Environment variables:**

| Variable | Default | Description |
|----------|---------|-------------|
| `SENTOR_API_KEY` | — | **Required.** Your Sentor API key. |
| `SENTOR_BASE_URL` | `https://sentor.app/api` | Override to point at a self-hosted Sentor instance. |
| `PORT` | `8080` | HTTP server port. |

---

## 🔗 Links

- [Sentor Dashboard](https://dashboard.sentor.app) — manage API keys, projects, and usage
- [API Documentation](https://sentor.app/docs) — full REST API reference
- [MCP Integration Guide](https://sentor.app/docs/integrations/mcp) — step-by-step setup
- [PyPI Package](https://pypi.org/project/sentor-mcp/) — `pip install sentor-mcp`
- [Support](mailto:sentor@nikx.one)

---

<!-- mcp-name: io.github.NIKX-Tech/sentor-mcp -->

<p align="center">
  Built by <a href="https://nikx.one">NIKX Technologies B.V.</a>
</p>
