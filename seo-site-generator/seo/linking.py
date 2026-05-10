import networkx as nx
from typing import Optional


class InternalLinkGraph:
    def __init__(self):
        self.graph = nx.DiGraph()

    def add_page(self, slug: str, service: str, city: str, keyword: str):
        self.graph.add_node(slug, service=service, city=city, keyword=keyword)

    def build_links(self):
        nodes = list(self.graph.nodes(data=True))
        for slug, attrs in nodes:
            for other_slug, other_attrs in nodes:
                if slug == other_slug:
                    continue
                # Link pages with same service across cities
                if attrs["service"] == other_attrs["service"]:
                    self.graph.add_edge(slug, other_slug, link_type="same_service")
                # Link pages in same city across services
                elif attrs["city"] == other_attrs["city"]:
                    self.graph.add_edge(slug, other_slug, link_type="same_city")

    def get_links_for(self, slug: str, max_links: int = 4) -> list[str]:
        if slug not in self.graph:
            return []
        neighbors = list(self.graph.successors(slug))
        # Prioritize same-service links
        same_service = [
            n for n in neighbors
            if self.graph[slug][n].get("link_type") == "same_service"
        ]
        same_city = [
            n for n in neighbors
            if self.graph[slug][n].get("link_type") == "same_city"
        ]
        combined = (same_service + same_city)[:max_links]
        return combined

    def get_hub_pages(self, top_n: int = 5) -> list[tuple[str, int]]:
        ranked = sorted(
            self.graph.nodes(),
            key=lambda n: self.graph.in_degree(n),
            reverse=True,
        )
        return [(slug, self.graph.in_degree(slug)) for slug in ranked[:top_n]]

    def summary(self) -> dict:
        return {
            "total_pages": self.graph.number_of_nodes(),
            "total_links": self.graph.number_of_edges(),
            "hub_pages": self.get_hub_pages(),
        }
