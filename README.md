# Sulev Recommendations
Hi Anton! Let's keep using this channel with Sulev. About SNOMED - Sulev has produced some OMOP data datasets that you should use. I hope Sulev can help to get access and guide in the process.


Overall, for our project, we need to answer:

* What is the structure of overall SNOMED as used in OMOP?
* Are there different types of relationships? (e.g., is-a, part-of, etc.)
* Where is our actual health data mapped into OMOP on that structure?

We also need to consider aggregation of mapped data along the paths upward on the structure.


For working with sets of patients that have been mapped to each category, we believe it makes sense to immediately start using Roaring Bitmaps (https://roaringbitmap.org/).


If you assign a set of patients to one node and work upward in the ontology, you can simply perform UNION (avoid repetitive counting). It's also interesting to know how scalable this is - can we build an index of individuals over SNOMED so that every node has a bitmap representing individuals with that annotation?


Note that when working with SNOMED, we may need to work with higher-level concepts or lower levels; understanding the structure and mappings will help us design next steps.


Perhaps similar approaches could be done with ICD, ATC, RxNorm, Visits, procedures... but for our first project, SNOMED is a good starting point.


We would avoid focusing on visualizations too much as this can be hard and may distract from the calculations.


If needed, we might want to learn Cytoscape or GraphViz. But for now, let's focus on the calculations.


[text](https://drive.google.com/drive/u/1/folders/1Ttr3XHWgJcLo_8rmTZlka6mS2uvGlLCK)

