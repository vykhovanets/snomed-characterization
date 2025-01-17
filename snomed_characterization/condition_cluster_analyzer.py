import networkx as nx
from networkx.algorithms import community
import numpy as np
from collections import defaultdict
from typing import List, Dict, Set, Tuple


class ConditionClusterAnalyzer:
    """
    @snomed_graph: nx.DiGraph
    the snomed_graph is a subgraph with only conditions and ancestors related
    to the patients conditions bi directed graph with is_ancestor_of
    and is_descendant_of relationships.

    """

    def __init__(
        self,
        patient_conditions: List[List[int]],
        snomed_graph: nx.DiGraph,
        max_ancestor_depth=10000,
        hierarchy_coefficient=0.6,
        jaccard_coefficient=0.4,
    ):
        self.snomed_graph = snomed_graph
        self.cooccurrence_graph = nx.Graph()
        self.patient_conditions = patient_conditions
        self.max_ancestor_depth = max_ancestor_depth
        self.hierarchy_coefficient = hierarchy_coefficient
        self.jaccard_coefficient = jaccard_coefficient
        self.total_patients = len(patient_conditions)

        # Calculate basic statistics
        self.condition_frequencies = self._calculate_frequencies()
        self.cooccurrence_matrix = self._calculate_cooccurrence()

        # Cache ancestor paths for performance
        self.ancestor_paths = self._cache_ancestor_paths()

    def _calculate_cooccurrence(self) -> Dict[Tuple[int, int], int]:
        """Calculate co-occurrence counts for all pairs of conditions"""
        cooccurrence = defaultdict(int)
        for conditions in self.patient_conditions:
            for i, code1 in enumerate(conditions):
                for code2 in conditions[i + 1 :]:
                    pair = tuple(sorted([code1, code2]))
                    cooccurrence[pair] += 1
        return cooccurrence

    def _calculate_frequencies(self) -> Dict[int, int]:
        """Calculate frequency of each SNOMED code"""
        frequencies = defaultdict(int)
        for conditions in self.patient_conditions:
            for code in conditions:
                frequencies[code] += 1
        return frequencies

    def _cache_ancestor_paths(self) -> Dict[int, Dict[int, int]]:
        """Cache shortest paths to ancestors for all relevant concepts"""
        paths = defaultdict(dict)

        # Get all unique concepts from patient data
        all_concepts = {
            code for conditions in self.patient_conditions for code in conditions
        }

        for concept in all_concepts:
            # Use NetworkX to find paths to ancestors
            ancestors = self._get_ancestors_with_depths(concept)
            paths[concept] = ancestors

        return paths

    def _get_ancestors_with_depths(self, concept: int) -> Dict[int, int]:
        """Get ancestors and their depths using NetworkX traversal"""
        ancestors = {}
        visited = set()
        queue = [(concept, 0)]

        while queue:
            current, depth = queue.pop(0)
            if depth > self.max_ancestor_depth:
                continue

            if current in visited:
                continue

            visited.add(current)

            # Only add to ancestors if it's not the starting concept
            if current != concept:
                ancestors[current] = depth

            # Get parent concepts by following is_descendant_of edges
            for _, parent, data in self.snomed_graph.out_edges(current, data=True):
                if data.get("relationship") == "is_descendant_of":
                    if parent not in visited and depth + 1 <= self.max_ancestor_depth:
                        queue.append((parent, depth + 1))

        return ancestors

    def get_hierarchical_similarity(self, code1: int, code2: int) -> float:
        """
        Calculate similarity between concepts based on shared ancestors in the graph.
        """
        if code1 == code2:
            return 1.0

        ancestors1 = self.ancestor_paths.get(
            code1, self._get_ancestors_with_depths(code1)
        )
        ancestors2 = self.ancestor_paths.get(
            code2, self._get_ancestors_with_depths(code2)
        )

        # Find shared ancestors
        shared_ancestors = set(ancestors1.keys()) & set(ancestors2.keys())

        if not shared_ancestors:
            # Check if one is ancestor of another
            if code1 in ancestors2:
                return 1.0 / (1.0 + ancestors2[code1])
            if code2 in ancestors1:
                return 1.0 / (1.0 + ancestors1[code2])
            return 0.0

        # Calculate similarity based on closest shared ancestor
        similarities = []
        for ancestor in shared_ancestors:
            depth1 = ancestors1[ancestor]
            depth2 = ancestors2[ancestor]
            max_depth = max(depth1, depth2)
            # Similarity decreases with ancestor distance
            similarity = 1.0 / (1.0 + max_depth)
            similarities.append(similarity)

        return max(similarities)

    def get_enhanced_similarity(
        self,
        code1: int,
        code2: int,
    ) -> float:
        """
        Calculate enhanced similarity combining co-occurrence and hierarchical similarity.
        """
        jaccard = self.get_jaccard_similarity(code1, code2)
        hierarchical = self.get_hierarchical_similarity(code1, code2)

        # Combine similarities (adjustable weights)
        combined = (
            self.jaccard_coefficient * jaccard
            + self.hierarchy_coefficient * hierarchical
        )

        return combined

    def get_jaccard_similarity(self, code1: int, code2: int) -> float:
        """Calculate Jaccard similarity between two conditions"""
        union = self.condition_frequencies[code1] + self.condition_frequencies[code2]
        pair = tuple(sorted([code1, code2]))
        intersection = self.cooccurrence_matrix.get(pair, 0)

        if union == 0:
            return 0

        return intersection / (union - intersection)

    # @deperecated
    def get_similar_conditions(
        self,
        code: int,
        min_similarity: float = 0.3,
    ) -> List[Tuple[int, float]]:
        """Get all conditions similar to the given code above the threshold"""
        similarities = []
        all_codes = set()
        for conditions in self.patient_conditions:
            all_codes.update(conditions)

        for other_code in all_codes:
            if other_code != code:
                sim = self.get_enhanced_similarity(code, other_code)
                if sim >= min_similarity:
                    similarities.append((other_code, sim))

        return sorted(similarities, key=lambda x: x[1], reverse=True)

    def get_condition_clusters(
        self,
        similarity_threshold: float = 0.3,
        jaccard_coefficient=None,
        hierarchy_coefficient=None,
    ) -> Tuple[nx.Graph, List[Set[int]]]:
        """
        Cluster conditions based on combined similarity.
        Returns list of sets of related conditions.
        """
        # Create similarity graph
        sim_graph = nx.Graph()

        self.jaccard_coefficient = jaccard_coefficient or self.jaccard_coefficient
        self.hierarchy_coefficient = hierarchy_coefficient or self.hierarchy_coefficient

        # Get all unique codes
        all_codes = {
            code for conditions in self.patient_conditions for code in conditions
        }

        # Add nodes
        sim_graph.add_nodes_from(all_codes)

        # Add edges based on similarity
        for code1 in all_codes:
            for code2 in all_codes:
                if code1 < code2:  # Avoid duplicate pairs
                    sim = self.get_enhanced_similarity(code1, code2)
                    if sim >= similarity_threshold:
                        sim_graph.add_edge(code1, code2, weight=sim)

        # Find connected components (clusters)
        clusters = list(nx.connected_components(sim_graph))

        return sim_graph, clusters

    def build_cooccurrence_network(self):
        condition_pairs = defaultdict(int)

        # TODO: improve the network build (normalize weights, )
        # Count co-occurrences
        for conditions in self.patient_conditions:
            for i in range(len(conditions)):
                for j in range(i + 1, len(conditions)):
                    pair = tuple(sorted([conditions[i], conditions[j]]))
                    condition_pairs[pair] += 1

        # Create co-occurrence network
        for (cond1, cond2), count in condition_pairs.items():
            # TODO: check if we can add a contion to add an edge depending on the ocurrences..
            self.cooccurrence_graph.add_edge(cond1, cond2, weight=count)

    def detect_clusters(
        self, method: str = "greedy_modularity", **kwargs
    ) -> Dict[int, int]:
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
            communities = community.greedy_modularity_communities(
                self.cooccurrence_graph
            )
            # Convert to dict format
            return {node: i for i, comm in enumerate(communities) for node in comm}

        # can't be used in digraph
        elif method == "label_propagation":
            communities = community.label_propagation_communities(
                self.cooccurrence_graph
            )
            return {node: i for i, comm in enumerate(communities) for node in comm}

        elif method == "girvan_newman":
            # Get the first level of hierarchy from Girvan-Newman
            communities = next(community.girvan_newman(self.cooccurrence_graph))
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
            "modularity": community.modularity(
                self.cooccurrence_graph, community_sets.values()
            ),
            "num_communities": len(community_sets),
            "avg_community_size": np.mean(
                [len(comm) for comm in community_sets.values()]
            ),
            "min_community_size": min(len(comm) for comm in community_sets.values()),
            "max_community_size": max(len(comm) for comm in community_sets.values()),
        }

        return metrics

    def enrich_clusters_with_snomed(
        self, communities: Dict[int, int]
    ) -> Dict[int, Set[int]]:
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
                # XXX: check with Anton. not sure about this
                ancestors = nx.ancestors(self.snomed_graph, condition)
                cluster_parents[cluster_id].update(ancestors)
            except nx.NetworkXError:
                print(f"Error finding ancestors for condition {condition}")
                continue

        return cluster_parents


#
#
# from snomed_characterization.graphs.snomed_graph_builder import SNOMEDGraphBuilder
# from snomed_characterization.services.import_duckdb_concepts_to_snomed_graph import (
#     ImportDuckDBConceptsToSNOMEDGraph,
# )
#
#
# builder = SNOMEDGraphBuilder()
# db_path = "data/full_data.duckdb"
# importer_service = ImportDuckDBConceptsToSNOMEDGraph(db_path, builder)
#
# importer_service.call()
#
# graph = builder.graph
#
# import duckdb
# from typing import List
#
#
# def get_patient_conditions(conn: duckdb.DuckDBPyConnection) -> List[List[int]]:
#     query = """
#     WITH condition_arrays AS (
#       SELECT
#         person_id,
#         array_agg(DISTINCT condition_concept_id) as condition_ids
#       FROM condition_occurrence
#       WHERE
#         condition_concept_id != 0  -- exclude unmapped
#         AND condition_start_date IS NOT NULL
#       GROUP BY person_id
#     )
#     SELECT person_id, condition_ids
#     FROM condition_arrays
#     """
#
#     results = conn.execute(query).fetchall()
#
#     patient_conditions = [
#         list(map(int, condition_list)) for _, condition_list in results
#     ]
#
#     return patient_conditions
