"""Scoring worker - uses Claude to score lead fit and route decision."""

import json
import logging

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage

logger = logging.getLogger(__name__)

SCORING_PROMPT = """You are a sales lead qualification assistant. Score this lead 0-100.

Lead Information:
- Company: {company_name}
- Industry: {industry}

Enrichment Context:
{enrichment_text}

Score based on:
1. Industry alignment with our product (0-30 points)
2. Company size and budget potential (0-30 points)
3. Product relevance from enrichment (0-40 points)

Respond ONLY in JSON format:
{{"score": <0-100>, "reasoning": "<brief explanation>", "route": "<sales|nurture|disqualified>"}}

Route rules: score >= 70 → "sales", 40-69 → "nurture", < 40 → "disqualified"
"""


async def score_lead(
    company_name: str,
    industry: str | None = None,
    enrichment_text: str = "",
    **kwargs,
) -> dict:
    """Score a lead using Claude and determine routing."""
    logger.info(f"Scoring lead: {company_name}")

    prompt = SCORING_PROMPT.format(
        company_name=company_name,
        industry=industry or "Unknown",
        enrichment_text=enrichment_text or "No enrichment available",
    )

    try:
        llm = ChatAnthropic(model="claude-sonnet-4-20250514", temperature=0)
        response = await llm.ainvoke([HumanMessage(content=prompt)])
        content = response.content

        # Parse JSON response
        result = json.loads(content)
        score = result.get("score", 50)
        reasoning = result.get("reasoning", "No reasoning provided")
        route = result.get("route", "nurture")

        logger.info(f"Lead scored: {score}/100 → {route} ({reasoning})")

        return {
            "lead_score": score,
            "score_reasoning": reasoning,
            "route_decision": route,
        }

    except json.JSONDecodeError:
        logger.error(f"Failed to parse LLM scoring response: {content}")
        return {
            "lead_score": 50,
            "score_reasoning": "Scoring parse error — defaulting to human review",
            "route_decision": "nurture",
        }
    except Exception as e:
        logger.error(f"Scoring failed: {e}")
        return {
            "lead_score": 50,
            "score_reasoning": f"Scoring error: {e}",
            "route_decision": "nurture",
        }
