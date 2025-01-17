q_concepts = """
    WITH grouped_ancestors AS (
        SELECT 
            descendant_concept_id,
            ARRAY_AGG(ancestor_concept_id ORDER BY ancestor_concept_id) as level_1_ancestors
        FROM concept_ancestor ca
        JOIN concept_relationship cr 
        ON ca.ancestor_concept_id = cr.concept_id_2
        AND ca.descendant_concept_id = cr.concept_id_1
        WHERE min_levels_of_separation = 1
        AND cr.relationship_id = 'Is a'
        GROUP BY descendant_concept_id
    )
    SELECT 
        c.*,
        ga.level_1_ancestors
    FROM concept c
    INNER JOIN grouped_ancestors ga ON c.concept_id = ga.descendant_concept_id
    WHERE c.invalid_reason IS NULL 
        AND c.standard_concept = 'S'
        AND c.domain_id = 'Condition';
    """

q_people_concepts = """
    select distinct condition_concept_id
    from condition_occurrence;
    """
