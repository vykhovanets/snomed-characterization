from neo4j import GraphDatabase
from snomed_characterization.services.import_duckdb_concepts_to_snomed_complete_graph import (
    ImportDuckDBConceptsToCompleteSNOMEDGraph,
)
from snomed_characterization.graphs.snomed_complete_graph_builder import (
    SNOMEDCompleteGraphBuilder,
)


class ImportNXGraphIntoNeo4J:
    def __init__(self, uri: str, db_path: str, user: str, password: str):
        self.uri = uri
        self.user = user
        self.password = password
        self.db_path = db_path

    def call(self):
        """Execute the import process from NetworkX to Neo4j."""
        # Process to import the concepts from DuckDB to SNOMED Graph
        snomed = SNOMEDCompleteGraphBuilder()
        ImportDuckDBConceptsToCompleteSNOMEDGraph(self.db_path, snomed).call()
        nx_graph = snomed.graph

        with GraphDatabase.driver(self.uri, auth=(self.user, self.password)) as driver:
            with driver.session() as session:
                # Create constraints and indexes first
                self._create_constraints(session)
                # Import the graph
                session.write_transaction(self._create_neo4j_graph, nx_graph)

        print("Graph successfully loaded into Neo4j")

    def _create_constraints(self, session):
        """Create necessary constraints and indexes in Neo4j."""
        constraints = [
            "CREATE CONSTRAINT concept_id IF NOT EXISTS FOR (n:SNOMEDConcept) REQUIRE n.concept_id IS UNIQUE",
            "CREATE INDEX concept_code IF NOT EXISTS FOR (n:SNOMEDConcept) ON (n.concept_code)",
        ]

        for constraint in constraints:
            session.run(constraint)

    def _create_neo4j_graph(self, tx, graph):
        """
        Creates nodes and relationships in Neo4j from a NetworkX graph.

        Args:
            tx: Neo4j transaction object
            graph: NetworkX graph object
        """
        # Create nodes first
        self._create_nodes(tx, graph)
        # Then create relationships
        self._create_relationships(tx, graph)

    def _create_nodes(self, tx, graph):
        """Create SNOMED CT concept nodes in Neo4j."""
        query = """
        MERGE (n:SNOMEDConcept {concept_id: $concept_id})
        ON CREATE SET 
            n.concept_name = $concept_name,
            n.domain_id = $domain_id,
            n.vocabulary_id = $vocabulary_id,
            n.concept_class_id = $concept_class_id,
            n.standard_concept = $standard_concept,
            n.concept_code = $concept_code,
            n.valid_start_date = $valid_start_date,
            n.valid_end_date = $valid_end_date,
            n.invalid_reason = $invalid_reason
        """
        for node_id, node_data in graph.nodes(data=True):
            node_data = node_data.get("data", {})
            if hasattr(node_data, "__dict__"):
                node_data = node_data.__dict__
            properties = {
                "concept_id": node_id,  # Use node_id as concept_id
                "concept_name": node_data.get("concept_name", ""),
                "domain_id": node_data.get("domain_id", ""),
                "vocabulary_id": node_data.get("vocabulary_id", ""),
                "concept_class_id": node_data.get("concept_class_id", ""),
                "standard_concept": node_data.get("standard_concept", ""),
                "concept_code": node_data.get("concept_code", ""),
                "valid_start_date": node_data.get("valid_start_date", ""),
                "valid_end_date": node_data.get("valid_end_date", ""),
                "invalid_reason": node_data.get("invalid_reason", ""),
            }
            tx.run(query, **properties)

    def _create_relationships(self, tx, graph):
        """Create relationships between SNOMED CT concepts in Neo4j."""
        query = """
        MATCH (source:SNOMEDConcept {concept_id: $source_id}),
              (target:SNOMEDConcept {concept_id: $target_id})
        MERGE (source)-[r:IS_A]->(target)
        ON CREATE SET r += $properties
        """
        for source, target, edge_data in graph.edges(data=True):
            tx.run(
                query, source_id=source, target_id=target, properties=edge_data or {}
            )


db_path = "data/full_data.duckdb"
service = ImportNXGraphIntoNeo4J(
    db_path=db_path, uri="bolt://localhost:", user="neo4j", password="12345678"
)
service.call()
