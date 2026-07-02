import logging
from typing import List, Dict, Any
from tavily import TavilyClient
from blog_agent import config

logger = logging.getLogger(__name__)

def search_tavily(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """
    Search Tavily with the given query. Returns a list of dictionaries,
    each containing title, url, snippet/content, and optionally date.
    """
    api_key = config.TAVILY_API_KEY
    if not api_key:
        logger.warning("TAVILY_API_KEY not found in environment. Using mock search results.")
        # Return mock results for testing purposes
        return [
            {
                "title": f"Mock Search Result for: {query}",
                "url": f"https://example.com/mock-{hash(query) % 1000}",
                "snippet": f"This is a mock search snippet to help test the blog writing worker node for the query: '{query}'.",
                "date": "2026-06-30"
            }
        ]
    
    try:
        client = TavilyClient(api_key=api_key)
        response = client.search(query=query, max_results=max_results)
        results = response.get("results", [])
        
        evidence = []
        for r in results:
            evidence.append({
                "title": r.get("title", "No Title"),
                "url": r.get("url", ""),
                "snippet": r.get("content", ""), # Tavily uses 'content' for snippet text
                "date": r.get("published_date", "Unknown Date")
            })
        return evidence
    except Exception as e:
        logger.error(f"Error during Tavily search: {e}. Falling back to mock data.")
        return [
            {
                "title": f"Fallback Mock Result for: {query}",
                "url": "https://example.com/fallback-mock",
                "snippet": f"An error occurred while connecting to Tavily: {str(e)}. Using fallback content.",
                "date": "2026-06-30"
            }
        ]
