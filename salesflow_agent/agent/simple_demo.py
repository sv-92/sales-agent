"""Simple demo mode - provides hardcoded responses that look realistic."""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class SimpleDemoAgent:
    """Provides hardcoded realistic responses for demo purposes."""
    
    def __init__(self, tools):
        self.tools = tools
        logger.info("🎭 Simple demo mode enabled - using hardcoded responses")
    
    async def query(self, message: str) -> dict[str, Any]:
        """Return realistic responses based on query patterns."""
        message_lower = message.lower()
        
        # Top deals query
        if "top" in message_lower and ("deal" in message_lower or "opportunity" in message_lower):
            return {
                "answer": """Here are your top 5 deals by value:

1. **FinanceForward AI Suite** - $1,200,000 (Qualification)
2. **CloudManufact IoT Platform** - $850,000 (Negotiation)
3. **CloudManufact Data Lake** - $620,000 (Qualification)
4. **TechVault Cloud Migration** - $500,000 (Negotiation)
5. **FinanceForward Compliance Tool** - $340,000 (Prospecting)

Total value: $3,510,000""",
                "tools_used": ["list_top_deals"]
            }
        
        # Forecast query
        elif "forecast" in message_lower or any(q in message_lower for q in ["q1", "q2", "q3", "q4"]):
            quarter = "Q4"
            for word in message.upper().split():
                if word.startswith("Q") and len(word) == 2 and word[1].isdigit():
                    quarter = word
                    break
            
            return {
                "answer": f"""📊 **{quarter} Sales Forecast**

• **Pipeline**: $18,500,000
• **Commit**: $12,000,000
• **Best Case**: $15,500,000
• **Closed Won**: $8,200,000

Current attainment: **68.3%** of commit""",
                "tools_used": ["get_forecast"]
            }
        
        # Pipeline summary
        elif "pipeline" in message_lower and "summary" in message_lower:
            return {
                "answer": """🎯 **Pipeline Summary by Stage**

• **Prospecting**: 12 deals ($4,200,000) - 29%
• **Qualification**: 10 deals ($6,800,000) - 24%
• **Negotiation**: 8 deals ($5,500,000) - 19%
• **Closed Won**: 11 deals ($8,200,000) - 26%

**Total**: 41 deals worth $24,700,000""",
                "tools_used": ["get_pipeline_summary"]
            }
        
        # Account search
        elif "search" in message_lower or "find" in message_lower or "account" in message_lower or "compan" in message_lower:
            return {
                "answer": """🔍 Found 3 account(s) matching 'technology':

• **TechCorp Solutions** - Technology
  Annual Revenue: $50,000,000

• **CloudManufacturing Inc.** - Technology  
  Annual Revenue: $120,000,000

• **TechVault Security** - Technology
  Annual Revenue: $35,000,000""",
                "tools_used": ["search_accounts"]
            }
        
        # Contacts
        elif "contact" in message_lower:
            return {
                "answer": """📇 **Contacts at TechCorp Solutions**

• **Sarah Chen** - VP of Engineering
  📧 sarah.chen@techcorp.com | 📱 (555) 123-4567

• **Michael Rodriguez** - CTO
  📧 m.rodriguez@techcorp.com | 📱 (555) 123-4568

• **Emily Thompson** - Director of IT
  📧 e.thompson@techcorp.com | 📱 (555) 123-4569""",
                "tools_used": ["get_contacts"]
            }
        
        # Default help message
        else:
            return {
                "answer": """I can help you with:

📊 **Pipeline Analysis**
- "What are my top 5 deals?"
- "Show me my pipeline summary"

📈 **Forecasting**
- "What is the Q4 forecast?"
- "Show me Q1 projections"

🔍 **Account & Contact Lookup**
- "Find technology companies"
- "Search for retail accounts"
- "Get contacts for TechCorp"

Try asking one of these questions!""",
                "tools_used": []
            }
