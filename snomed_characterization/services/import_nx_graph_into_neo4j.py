from neo4j import GraphDatabase
from snomed_characterization.services.import_duckdb_concepts_to_snomed_graph import (
    ImportDuckDBConceptsToSNOMEDGraph,
)
from snomed_characterization.snomed_graph import SNOMEDGraph


class ImportNXGraphIntoNeo4J:
    def __init__(self, uri, db_path, user, password):
        self.uri = uri
        self.user = user
        self.password = password
        self.db_path = db_path

    def call(self):
        # process to import the concepts from DuckDB to SNOMED Graph
        snomed = SNOMEDGraph()

        _ = ImportDuckDBConceptsToSNOMEDGraph(self.db_path, snomed).call()
        nx_graph = snomed.graph

        with GraphDatabase.driver(self.uri, auth=(self.user, self.password)) as driver:
            with driver.session() as session:
                session.write_transaction(self._create_neo4j_graph, nx_graph)

        print("graph loaded into Neo4j")

    def _create_neo4j_graph(self, tx, graph):
        """
        Creates nodes and relationships in Neo4j from a NetworkX graph.

        Args:
            tx: Neo4j transaction object.
            graph: NetworkX graph object.
        """
        for node in graph.nodes(data=True):
            node_id = node[0]
            node_properties = node[1]
            # Dynamically include the label in the query
            query = "CREATE (n:`Node`) SET n += $properties SET n.id = $node_id"
            tx.run(query, properties=node_properties, node_id=node_id)

        for source, target, edge_properties in graph.edges(data=True):
            query = (
                "MATCH (a:`Node` {id: $source_id}), (b:`Node` {id: $target_id}) "
                "CREATE (a)-[:RELATES_TO $properties]->(b)"
            )
            tx.run(
                query,
                source_id=source,
                target_id=target,
                properties=edge_properties,
            )
