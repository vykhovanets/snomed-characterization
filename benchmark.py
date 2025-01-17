import os
import psutil
import gc
import time
import sys
import random
import networkx as nx
from pyroaring import BitMap
from snomed_characterization.graphs.bitmap_graph import (
    BitMapGraph,
    IS_ANCESTOR_OF,
    IS_DESCENDANT_OF,
)


def get_process_memory():
    """Get current process memory in MB"""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024


def get_object_size(obj):
    """Get size of object in bytes"""
    seen = set()

    def sizeof(obj):
        if id(obj) in seen:
            return 0
        seen.add(id(obj))
        size = sys.getsizeof(obj)

        if isinstance(obj, (str, int, float, bool, BitMap)):
            return size
        elif isinstance(obj, dict):
            size += sum(sizeof(k) + sizeof(v) for k, v in obj.items())
        elif isinstance(obj, (list, tuple, set)):
            size += sum(sizeof(x) for x in obj)
        elif hasattr(obj, "__dict__"):
            size += sizeof(obj.__dict__)
        return size

    return sizeof(obj)


def generate_test_hierarchy(num_concepts: int, avg_parents: int = 2):
    """Generate test hierarchy with bidirectional relationships"""
    concepts = list(range(num_concepts))
    ancestor_relationships = []  # (source, target, "is_ancestor_of")
    descendant_relationships = []  # (source, target, "is_descendant_of")

    for concept in range(1, num_concepts):
        num_parents = min(random.randint(1, avg_parents), concept)
        if num_parents > 0:
            parents = random.sample(range(concept), num_parents)
            # Add both ancestor and descendant relationships
            for parent in parents:
                ancestor_relationships.append((parent, concept))
                descendant_relationships.append((concept, parent))

    return concepts, ancestor_relationships, descendant_relationships


def memory_comparison_test(num_concepts: int):
    """Run memory and performance comparison"""
    print(f"\nTesting with {num_concepts} concepts...")

    # Generate test data
    concepts, ancestor_rels, descendant_rels = generate_test_hierarchy(num_concepts)

    # Test BitMap implementation
    gc.collect()
    initial_memory = get_process_memory()
    start_time = time.time()

    bitmap_graph = BitMapGraph()

    # First add all concepts
    for concept in concepts:
        bitmap_graph.nodes.add(concept)
        bitmap_graph.relationships[concept, IS_ANCESTOR_OF] = BitMap()
        bitmap_graph.relationships[concept, IS_DESCENDANT_OF] = BitMap()

    # Then add relationships
    for source, target in ancestor_rels:
        bitmap_graph.relationships[source, IS_ANCESTOR_OF].add(target)
    for source, target in descendant_rels:
        bitmap_graph.relationships[source, IS_DESCENDANT_OF].add(target)

    bitmap_memory = get_process_memory() - initial_memory
    bitmap_time = time.time() - start_time
    bitmap_size = get_object_size(bitmap_graph)

    # Test NetworkX implementation
    gc.collect()
    initial_memory = get_process_memory()
    start_time = time.time()

    nx_graph = nx.DiGraph()
    nx_graph.add_nodes_from(concepts)
    nx_graph.add_edges_from(ancestor_rels)  # Only need one direction for NetworkX

    nx_memory = get_process_memory() - initial_memory
    nx_time = time.time() - start_time
    nx_size = get_object_size(nx_graph)

    # Test operations on a sample of nodes
    num_samples = min(100, num_concepts)
    sample_nodes = random.sample(concepts, num_samples)

    # Ancestor lookup
    start = time.time()
    for node in sample_nodes:
        _ = bitmap_graph.get_all_ancestors(node)
    bitmap_ancestor_time = (time.time() - start) / num_samples

    start = time.time()
    for node in sample_nodes:
        _ = set(nx.ancestors(nx_graph, node))
    nx_ancestor_time = (time.time() - start) / num_samples

    # Descendant lookup
    start = time.time()
    for node in sample_nodes:
        _ = bitmap_graph.get_all_descendants(node)
    bitmap_descendant_time = (time.time() - start) / num_samples

    start = time.time()
    for node in sample_nodes:
        _ = set(nx.descendants(nx_graph, node))
    nx_descendant_time = (time.time() - start) / num_samples

    results = {
        "bitmap": {
            "memory_mb": bitmap_memory,
            "build_time": bitmap_time,
            "object_size": bitmap_size,
            "ancestor_lookup_ms": bitmap_ancestor_time * 1000,
            "descendant_lookup_ms": bitmap_descendant_time * 1000,
        },
        "networkx": {
            "memory_mb": nx_memory,
            "build_time": nx_time,
            "object_size": nx_size,
            "ancestor_lookup_ms": nx_ancestor_time * 1000,
            "descendant_lookup_ms": nx_descendant_time * 1000,
        },
    }

    print("\nResults:")
    print(f"{'Metric':<20} {'BitMap':<15} {'NetworkX':<15} {'Ratio (NX/BM)':<15}")
    print("-" * 65)
    print(
        f"Memory (MB){'':12} {bitmap_memory:<15.2f} {nx_memory:<15.2f} {nx_memory/bitmap_memory:<15.2f}"
    )
    print(
        f"Build Time (s){'':8} {bitmap_time:<15.2f} {nx_time:<15.2f} {nx_time/bitmap_time:<15.2f}"
    )
    print(
        f"Object Size (KB){'':7} {bitmap_size/1024:<15.2f} {nx_size/1024:<15.2f} {nx_size/bitmap_size:<15.2f}"
    )
    print(
        f"Ancestor Lookup (ms) {bitmap_ancestor_time*1000:<15.2f} {nx_ancestor_time*1000:<15.2f} {nx_ancestor_time/bitmap_ancestor_time:<15.2f}"
    )
    print(
        f"Descendant Lookup (ms) {bitmap_descendant_time*1000:<15.2f} {nx_descendant_time*1000:<15.2f} {nx_descendant_time/bitmap_descendant_time:<15.2f}"
    )

    return results
