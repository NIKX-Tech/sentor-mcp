"""Sentor MCP Server — exposes sentiment analysis, clustering, and topic naming as MCP tools."""

import os
import httpx
from mcp.server.fastmcp import FastMCP

SENTOR_BASE_URL = os.getenv("SENTOR_BASE_URL", "https://sentor.app/api")
SENTOR_API_KEY = os.getenv("SENTOR_API_KEY", "")

mcp = FastMCP(
    "Sentor AI",
    instructions=(
        "You have access to Sentor's entity-based sentiment analysis API. "
        "Use analyze_sentiment to score sentiment toward specific entities in text. "
        "Use cluster_documents to group documents by topic (min 5 docs). "
        "Use name_topic after clustering to label each cluster with a descriptive name. "
        "Use health_check to verify the service is available. "
        "All tools require a valid SENTOR_API_KEY set in the environment."
    ),
)


def _headers() -> dict:
    if not SENTOR_API_KEY:
        raise ValueError(
            "SENTOR_API_KEY environment variable is not set. "
            "Get your key at https://dashboard.sentor.app/settings?tab=api-access"
        )
    return {"x-api-key": SENTOR_API_KEY, "Content-Type": "application/json"}


@mcp.tool()
def analyze_sentiment(
    docs: list[dict],
    language: str = "en",
) -> dict:
    """Analyze entity-based sentiment in one or more documents.

    Each item in docs must be:
      { "doc_id": "unique-id", "doc": "text to analyze", "entities": ["entity1", "entity2"] }

    Entities are the specific subjects you want sentiment scored for (e.g. a brand, product,
    feature, or person). The model returns per-document sentiment (negative/neutral/positive)
    plus per-sentence breakdowns.

    Args:
        docs: List of document objects with doc_id, doc, and entities fields.
        language: Language code — "en" (English) or "nl" (Dutch). Defaults to "en".

    Returns:
        Dict with "results" list. Each result has doc_id, predicted_label, probabilities,
        and sentence-level details.
    """
    with httpx.Client(timeout=30) as client:
        response = client.post(
            f"{SENTOR_BASE_URL}/predicts",
            params={"language": language},
            json={"docs": docs},
            headers=_headers(),
        )
        response.raise_for_status()
        return response.json()


@mcp.tool()
def cluster_documents(
    documents: list[dict],
    language: str = "en",
) -> dict:
    """Group documents into thematic clusters using BERTopic + HDBSCAN.

    Requires at least 5 documents. The algorithm automatically discovers the natural
    number of clusters — you do not need to specify how many. Cluster -1 contains outliers
    that did not fit any topic.

    Each item in documents must be:
      { "doc_id": "unique-id", "text": "document text", "entities": ["optional", "entities"] }

    After clustering, pass each cluster's top_words and documents to name_topic to get
    a human-readable label.

    Args:
        documents: List of document objects with doc_id, text, and optional entities fields.
        language: Language code — "en" or "nl". Defaults to "en".

    Returns:
        Dict with "clusters" list (each with cluster_id, document_count, documents, top_words),
        total_documents, total_clusters, and outliers_count.
    """
    if len(documents) < 5:
        return {
            "error": f"Clustering requires at least 5 documents, got {len(documents)}.",
            "hint": "Add more documents or use analyze_sentiment for smaller sets.",
        }

    with httpx.Client(timeout=120) as client:
        response = client.post(
            f"{SENTOR_BASE_URL}/predicts/cluster",
            params={"language": language},
            json={"documents": documents},
            headers=_headers(),
        )
        response.raise_for_status()
        return response.json()


@mcp.tool()
def name_topic(
    cluster_id: int,
    documents: list[dict],
    top_words: list[str] | None = None,
    entities: list[str] | None = None,
    language: str = "en",
) -> dict:
    """Generate a short descriptive name for a document cluster using an LLM.

    Call this after cluster_documents. Pass the cluster's documents and top_words
    from the clustering response for best results. The model produces a 3-5 word
    label (e.g. "Shipping Delay Complaints", "Product Quality Praise").

    Args:
        cluster_id: The cluster ID from the clustering response (e.g. 0, 1, 2).
        documents: The documents list from that cluster's clustering response entry.
        top_words: The top_words list from that cluster's clustering response entry (recommended).
        entities: Entity names to exclude from the topic label (e.g. your brand name).
        language: Language code — "en" or "nl". Defaults to "en".

    Returns:
        Dict with cluster_id, topic_name (the generated label), document_count,
        and generation_method ("LLM" or "Fallback").
    """
    with httpx.Client(timeout=30) as client:
        response = client.post(
            f"{SENTOR_BASE_URL}/predicts/topic-name",
            json={
                "cluster_id": cluster_id,
                "documents": documents,
                "top_words": top_words or [],
                "entities": entities or [],
                "language": language,
            },
            headers=_headers(),
        )
        response.raise_for_status()
        return response.json()


@mcp.tool()
def health_check() -> dict:
    """Check Sentor API availability and model status.

    Returns the API status, version, and whether the LLM provider (used for
    topic naming and report generation) is reachable.

    Returns:
        Dict with status ("healthy" or "degraded"), version, llm_provider, and llm_status.
    """
    with httpx.Client(timeout=10) as client:
        response = client.get(
            f"{SENTOR_BASE_URL}/predicts/health",
            headers=_headers(),
        )
        response.raise_for_status()
        return response.json()


def main() -> None:
    """Entry point for stdio transport (Claude Desktop, Cursor, Windsurf)."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
