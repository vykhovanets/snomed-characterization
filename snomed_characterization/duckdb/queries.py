q_concepts = """
    select * from concept c 
    left join concept_ancestor ca
    on c.concept_id=ca.descendant_concept_id
    or c.concept_id=ca.ancestor_concept_id
    where c.invalid_reason is  null
    AND ca.min_levels_of_separation=1
     and standard_concept is not null
     and domain_id in ('Condition')
     -- and domain_id in ('Condition', 'Observation')
    """
