"""Demo mode for SalesFlow Agent - simulates LLM responses without API calls."""

import json
import logging
from typing import Any

logger = logging.getLogger(__name__)


class DemoAgent:
    """Simulates agent responses by calling tools directly and formatting results."""
    
    def __init__(self, tools):
        self.tools = {tool.name: tool for tool in tools}
        logger.info("Demo mode enabled - using simulated LLM responses")
    
    async def query(self, message: str) -> dict[str, Any]:
        """Simulate agent reasoning and tool calling based on the query."""
        message_lower = message.lower()
        
        # Pattern matching for different query types
        if "top" in message_lower and ("deal" in message_lower or "opportunity" in message_lower):
            return await self._handle_top_deals(message)
        
        elif "forecast" in message_lower or ("q" in message_lower and any(q in message_lower for q in ["q1", "q2", "q3", "q4"])):
            return await self._handle_forecast(message)
        
        elif "pipeline" in message_lower and "summary" in message_lower:
            return await self._handle_pipeline_summary(message)
        
        elif "search" in message_lower or "find" in message_lower or "account" in message_lower or "company" in message_lower or "companies" in message_lower:
            return await self._handle_account_search(message)
        
        elif "contact" in message_lower:
            return await self._handle_contacts(message)
        
        else:
            return await self._handle_general(message)
    
    async def _handle_top_deals(self, message: str) -> dict[str, Any]:
        """Handle top deals query."""
        # Extract limit if mentioned
        limit = 5
        for word in message.split():
            if word.isdigit():
                limit = int(word)
                break
        
        # Call the actual MCP tool
        tool = self.tools.get("list_top_deals")
        if tool:
            result = await tool.ainvoke({"limit": limit})
            
            # Extract data from MCP result
            deals = self._extract_data(result)
            
            if not deals:
                return {
                    "answer": "Unable to retrieve deals data.",
                    "tools_used": ["list_top_deals"]
                }
            
            # Format a natural response
            answer = f"Here are your top {limit} deals by value:\n\n"
            for i, deal in enumerate(deals, 1):
                answer += f"{i}. **{deal['name']}** - ${deal['amount']:,} ({deal['stage']})\n"
            
            answer += f"\nTotal value: ${sum(d['amount'] for d in deals):,}"
            
            return {
                "answer": answer,
                "tools_used": ["list_top_deals"]
            }
        
        return {"answer": "Unable to retrieve deals data.", "tools_used": []}
    
    def _extract_data(self, result: Any) -> Any:
        """Extract data from MCP tool result."""
        # Check if it's a CallToolResult object with data attribute
        if hasattr(result, 'data') and result.data is not None:
            return result.data
        
        # Check if it has structured_content
        if hasattr(result, 'structured_content') and result.structured_content:
            sc = result.structured_content
            if isinstance(sc, dict) and 'result' in sc:
                return sc['result']
            return sc
        
        # Try to extract from content list (MCP CallToolResult format)
        if hasattr(result, 'content') and result.content:
            for item in result.content:
                if hasattr(item, 'text') and item.text:
                    try:
                        # Parse the JSON string from text content
                        return json.loads(item.text)
                    except (json.JSONDecodeError, AttributeError) as e:
                        logger.debug(f"Could not parse content text as JSON: {e}")
                        continue
        
        # If it's a plain string, try to parse it
        if isinstance(result, str):
            try:
                return json.loads(result)
            except json.JSONDecodeError:
                logger.debug(f"String is not JSON: {result[:50]}")
                return None
        
        # If it's already a list or dict, return as-is
        if isinstance(result, (list, dict)):
            return result
        
        logger.warning(f"Could not extract data from result type: {type(result).__name__}")
        return None
    
    async def _handle_forecast(self, message: str) -> dict[str, Any]:
        """Handle forecast query."""
        # Extract quarter
        quarter = "Q4"
        for word in message.upper().split():
            if word.startswith("Q") and len(word) == 2 and word[1].isdigit():
                quarter = word
                break
        
        tool = self.tools.get("get_forecast")
        if tool:
            result = await tool.ainvoke({"quarter": quarter})
            data = self._extract_data(result)
            
            if not data:
                return {
                    "answer": "Unable to retrieve forecast data.",
                    "tools_used": ["get_forecast"]
                }
            
            answer = f"📊 **{quarter} Sales Forecast**\n\n"
            answer += f"• **Pipeline**: ${data['pipeline']:,}\n"
            answer += f"• **Commit**: ${data['commit']:,}\n"
            answer += f"• **Best Case**: ${data['best_case']:,}\n"
            answer += f"• **Closed Won**: ${data['closed']:,}\n\n"
            
            attainment = (data['closed'] / data['commit'] * 100) if data['commit'] > 0 else 0
            answer += f"Current attainment: **{attainment:.1f}%** of commit"
            
            return {
                "answer": answer,
                "tools_used": ["get_forecast"]
            }
        
        return {"answer": "Unable to retrieve forecast data.", "tools_used": []}
    
    async def _handle_pipeline_summary(self, message: str) -> dict[str, Any]:
        """Handle pipeline summary query."""
        tool = self.tools.get("get_pipeline_summary")
        if tool:
            result = await tool.ainvoke({})
            stages = self._extract_data(result)
            
            if not stages:
                return {
                    "answer": "Unable to retrieve pipeline data.",
                    "tools_used": ["get_pipeline_summary"]
                }
            
            answer = "🎯 **Pipeline Summary by Stage**\n\n"
            total = sum(s['count'] for s in stages)
            total_value = sum(s['total_amount'] for s in stages)
            
            for stage in stages:
                pct = (stage['count'] / total * 100) if total > 0 else 0
                answer += f"• **{stage['stage']}**: {stage['count']} deals (${stage['total_amount']:,}) - {pct:.0f}%\n"
            
            answer += f"\n**Total**: {total} deals worth ${total_value:,}"
            
            return {
                "answer": answer,
                "tools_used": ["get_pipeline_summary"]
            }
        
        return {"answer": "Unable to retrieve pipeline data.", "tools_used": []}
    
    async def _handle_account_search(self, message: str) -> dict[str, Any]:
        """Handle account search query."""
        # Extract search term
        search_term = ""
        keywords = ["technology", "tech", "software", "retail", "healthcare", "finance", "enterprise"]
        for keyword in keywords:
            if keyword in message.lower():
                search_term = keyword
                break
        
        if not search_term:
            # Extract company name if quoted or after "find"
            words = message.lower().replace(",", "").split()
            if "find" in words:
                idx = words.index("find")
                if idx + 1 < len(words):
                    search_term = words[idx + 1]
        
        tool = self.tools.get("search_accounts")
        if tool:
            result = await tool.ainvoke({"query": search_term or "tech"})
            accounts = self._extract_data(result)
            
            if not accounts:
                return {
                    "answer": "Unable to search accounts.",
                    "tools_used": ["search_accounts"]
                }
            
            answer = f"🔍 Found {len(accounts)} account(s)"
            if search_term:
                answer += f" matching '{search_term}'"
            answer += ":\n\n"
            
            for acc in accounts:
                answer += f"• **{acc['name']}** - {acc['industry']}\n"
                answer += f"  Annual Revenue: ${acc['annual_revenue']:,}\n"
            
            return {
                "answer": answer,
                "tools_used": ["search_accounts"]
            }
        
        return {"answer": "Unable to search accounts.", "tools_used": []}
    
    async def _handle_contacts(self, message: str) -> dict[str, Any]:
        """Handle contacts query."""
        # Try to extract account name
        account_name = "TechCorp Solutions"  # Default
        
        tool = self.tools.get("get_contacts")
        if tool:
            result = await tool.ainvoke({"account_name": account_name})
            contacts = self._extract_data(result)
            
            if not contacts:
                return {
                    "answer": "Unable to retrieve contacts.",
                    "tools_used": ["get_contacts"]
                }
            
            answer = f"📇 **Contacts at {account_name}**\n\n"
            
            for contact in contacts:
                answer += f"• **{contact['name']}** - {contact['title']}\n"
                answer += f"  📧 {contact['email']} | 📱 {contact['phone']}\n\n"
            
            return {
                "answer": answer,
                "tools_used": ["get_contacts"]
            }
        
        return {"answer": "Unable to retrieve contacts.", "tools_used": []}
    
    async def _handle_general(self, message: str) -> dict[str, Any]:
        """Handle general queries with helpful response."""
        answer = """I can help you with:

📊 **Pipeline Analysis**
- "What are my top 5 deals?"
- "Show me my pipeline summary"

📈 **Forecasting**
- "What is the Q4 forecast?"
- "Show me Q1 projections"

🔍 **Account & Contact Lookup**
- "Find technology companies"
- "Search for retail accounts"
- "Get contacts for [account name]"

Try asking one of these questions!"""
        
        return {
            "answer": answer,
            "tools_used": []
        }
