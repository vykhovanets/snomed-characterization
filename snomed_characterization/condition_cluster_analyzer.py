import networkx as nx
from networkx.algorithms import community
import numpy as np
from collections import defaultdict
from typing import List, Dict, Set
import pyroaring as pr

class ConditionClusterAnalyzer:
    def __init__(self, snomed_graph: nx.DiGraph):
        self.snomed_graph = snomed_graph
        self.cooccurrence_graph = nx.Graph()

    def build_cooccurrence_network(self, patient_conditions: List[pr.BitMap]):
        condition_pairs = defaultdict(int)

        # TODO: improve the network build (normalize weights, )
        # Count co-occurrences
        for condition_bitmap in patient_conditions:
            conditions = list(condition_bitmap)
            for i in range(len(conditions)):
                for j in range(i + 1, len(conditions)):
                    pair = tuple(sorted([conditions[i], conditions[j]]))
                    condition_pairs[pair] += 1

        # Create co-occurrence network
        for (cond1, cond2), count in condition_pairs.items():
            # TODO: check if we can add a contion to add an edge depending on the ocurrences..
            self.cooccurrence_graph.add_edge(cond1, cond2, weight=count)

    def detect_clusters(self, method: str = "greedy_modularity", **kwargs) -> Dict[int, int]:
        # TODO: check best community approach
        """
        Detect clusters using NetworkX community detection algorithms

        Args:
            method: Algorithm to use ('greedy_modularity', 'label_propagation', 'girvan_newman')
            **kwargs: Additional parameters for specific algorithms

        Returns:
            Dictionary mapping node IDs to community IDs
        """
        if method == "greedy_modularity":
            communities = nx.algorithms.community.greedy_modularity_communities(
                self.cooccurrence_graph
            )
            return {node: i for i, comm in enumerate(communities) for node in comm}
        else:
            raise ValueError(f"Unsupported method: {method}")

    def get_cluster_metrics(self, communities: Dict[int, int]) -> Dict[str, float]:
        """
        Calculate metrics for the detected communities

        Args:
            communities: Dictionary mapping nodes to community IDs

        Returns:
            Dictionary of metrics
        """
        # Convert dict format to set format for modularity calculation
        community_sets = defaultdict(set)
        for node, comm_id in communities.items():
            community_sets[comm_id].add(node)

        metrics = {
            "modularity": nx.algorithms.community.quality.modularity(
                self.cooccurrence_graph, community_sets.values()
            ),
            "num_communities": len(community_sets),
            "avg_community_size": sum(len(c) for c in community_sets.values()) / len(community_sets),
            "min_community_size": min(len(c) for c in community_sets.values()),
            "max_community_size": max(len(c) for c in community_sets.values()),
        }

        return metrics

    def enrich_clusters_with_snomed(self, communities: Dict[int, int]) -> Dict[int, Set[int]]:
        """
        Enrich clusters with SNOMED parent concepts

        Args:
            communities: Dictionary mapping condition IDs to cluster IDs

        Returns:
            Dictionary mapping cluster IDs to sets of parent SNOMED concepts
        """
        cluster_parents = defaultdict(set)

        for condition, cluster_id in communities.items():
            try:
                ancestors = nx.ancestors(self.snomed_graph, condition)
                cluster_parents[cluster_id].update(ancestors)
            except nx.NetworkXError:
                continue

        return cluster_parents
