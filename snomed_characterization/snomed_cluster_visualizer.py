import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import networkx as nx
import numpy as np
from typing import List, Dict, Set

HQ_DPI = 300


class SNOMEDClusterVisualizer:
    def __init__(
        self, sim_graph: nx.Graph, clusters: List[Set[int]], conditions_df: pd.DataFrame
    ):
        """
        Initialize visualizer with similarity graph, clusters and condition information.

        Args:
            sim_graph: NetworkX graph with similarity edges
            clusters: List of sets containing clustered concept IDs
            conditions_df: DataFrame with concept information, indexed by concept_id
        """
        self.sim_graph = sim_graph
        self.clusters = clusters
        self.conditions_df = conditions_df

        # Set style
        sns.set_style("whitegrid")
        plt.rcParams["figure.figsize"] = [12, 8]

    def plot_cluster_sizes(self, save_path: str = None):
        """Plot distribution of cluster sizes"""
        cluster_sizes = [len(cluster) for cluster in self.clusters]

        plt.figure()
        sns.histplot(cluster_sizes, bins=20)
        plt.title("Distribution of Cluster Sizes")
        plt.xlabel("Cluster Size")
        plt.ylabel("Count")

        if save_path:
            plt.savefig(save_path, dpi=HQ_DPI)
        plt.show()

    def plot_similarity_distribution(self, save_path: str = None):
        """Plot distribution of similarity scores from edges"""
        similarities = [
            data["weight"] for _, _, data in self.sim_graph.edges(data=True)
        ]

        plt.figure()
        sns.histplot(similarities, bins=30)
        plt.title("Distribution of Similarity Scores")
        plt.xlabel("Similarity Score")
        plt.ylabel("Count")

        if save_path:
            plt.savefig(save_path, dpi=HQ_DPI)
        plt.show()

    def plot_concept_connectivity(self, top_n: int = 20, save_path: str = None):
        """Plot top N most connected concepts"""
        # Get degree of each node
        degrees = dict(self.sim_graph.degree())

        # Get top N by degree
        top_concepts = sorted(degrees.items(), key=lambda x: x[1], reverse=True)[:top_n]

        name_field = "concept_name"

        # Create DataFrame with concept names
        concept_data = []
        for concept_id, degree in top_concepts:
            name = (
                self.conditions_df.loc[concept_id, name_field]
                if name_field in self.conditions_df.columns
                else str(concept_id)
            )
            concept_data.append({"concept": name, "connections": degree})

        df = pd.DataFrame(concept_data)

        plt.figure(figsize=(15, 8))
        sns.barplot(data=df, x="connections", y="concept")
        plt.title(f"Top {top_n} Most Connected Concepts")
        plt.xlabel("Number of Connections")

        if save_path:
            plt.savefig(save_path, dpi=HQ_DPI)
        plt.show()

    def plot_cluster_similarity_heatmap(self, save_path: str = None):
        """Plot heatmap of inter-cluster similarities"""
        n_clusters = len(self.clusters)
        similarity_matrix = np.zeros((n_clusters, n_clusters))

        # Calculate average similarity between clusters
        for i in range(n_clusters):
            for j in range(i + 1, n_clusters):
                avg_sim = self._calculate_cluster_similarity(
                    self.clusters[i], self.clusters[j]
                )
                similarity_matrix[i, j] = avg_sim
                similarity_matrix[j, i] = avg_sim

        plt.figure(figsize=(12, 10))
        sns.heatmap(
            similarity_matrix,
            cmap="viridis",
            xticklabels=[f"C{i+1}" for i in range(n_clusters)],
            yticklabels=[f"C{i+1}" for i in range(n_clusters)],
        )
        plt.title("Inter-cluster Similarity Heatmap")

        if save_path:
            plt.savefig(save_path, dpi=HQ_DPI)
        plt.show()

    def _calculate_cluster_similarity(
        self, cluster1: Set[int], cluster2: Set[int]
    ) -> float:
        """Calculate average similarity between two clusters"""
        similarities = []
        for c1 in cluster1:
            for c2 in cluster2:
                if self.sim_graph.has_edge(c1, c2):
                    similarities.append(self.sim_graph.edges[c1, c2]["weight"])

        return np.mean(similarities) if similarities else 0

    def plot_cluster_compositions(
        self,
        top_clusters: int = 5,
        concepts_per_cluster: int = 5,
        save_path: str = None,
    ):
        """Plot top concepts in largest clusters"""
        # Sort clusters by size
        sorted_clusters = sorted(self.clusters, key=len, reverse=True)[:top_clusters]

        # Prepare data for plotting
        plot_data = []
        for i, cluster in enumerate(sorted_clusters):
            # Get concept names and their degrees
            name_field = "concept_name"
            cluster_concepts = []
            for concept_id in cluster:
                name = (
                    self.conditions_df.loc[concept_id, name_field]
                    if name_field in self.conditions_df.columns
                    else str(concept_id)
                )
                degree = self.sim_graph.degree(concept_id)
                cluster_concepts.append((name, degree))

            # Get top concepts by degree
            top_concepts = sorted(cluster_concepts, key=lambda x: x[1], reverse=True)[
                :concepts_per_cluster
            ]

            for name, degree in top_concepts:
                plot_data.append(
                    {
                        "cluster": f"Cluster {i+1}",
                        "concept": name,
                        "connections": degree,
                    }
                )

        df = pd.DataFrame(plot_data)

        plt.figure(figsize=(15, 10))
        sns.barplot(data=df, x="connections", y="concept", hue="cluster")
        plt.title(
            f"Top {concepts_per_cluster} Concepts in {top_clusters} Largest Clusters"
        )
        plt.xlabel("Number of Connections")

        if save_path:
            plt.savefig(save_path, dpi=HQ_DPI)
        plt.show()


# Example usage:
"""
# Create visualizer
visualizer = SNOMEDClusterVisualizer(sim_graph, clusters, conditions_df)

# Generate various plots
visualizer.plot_cluster_sizes('cluster_sizes.png')
visualizer.plot_similarity_distribution('similarities.png')
visualizer.plot_concept_connectivity(top_n=20, save_path='connectivity.png')
visualizer.plot_cluster_similarity_heatmap('cluster_similarity.png')
visualizer.plot_cluster_compositions(save_path='cluster_composition.png')
"""
