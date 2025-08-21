"""
Simple search strategy for SEO enhancement
"""
import random
import os
from ..logging.logger import log


class SimpleSearchStrategy:
    def __init__(self, brand_name: str, target_domain: str):
        self.brand_name = brand_name
        self.target_domain = target_domain
        self.search_count = 0
    
    def get_search_query(self, base_topic: str) -> str:
        """
        Generate search query: 30% brand, 70% discovery (Spanish keywords for noviachat)
        """
        self.search_count += 1
        
        # 30% brand searches
        if random.random() < 0.3:
            brand_queries = [
                self.brand_name,
                f"{self.brand_name} sitio web",
                f"{self.brand_name} oficial",
                f"www {self.brand_name}",
                f"{self.brand_name} {base_topic}",
                f"{self.brand_name}.com",
                f"{self.brand_name} chat",
                f"{self.brand_name} app"
            ]
            query = random.choice(brand_queries)
            log(f"Búsqueda de marca #{self.search_count}: {query}")
            
        else:
            # 70% discovery searches - Spanish keywords for AI girlfriend chat
            discovery_queries = [
                "novia virtual gratis",
                "novia virtual app",
                "novia virtual chat",
                "chicas virtuales",
                "novia IA gratis",
                "novia virtual en español"
            ]
            query = random.choice(discovery_queries)
            log(f"Búsqueda de descubrimiento #{self.search_count}: {query}")
        
        return query