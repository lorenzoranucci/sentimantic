INSERT INTO type (uri) VALUES ('http://dbpedia.org/ontology/Person');
INSERT INTO type (uri) VALUES ('http://www.w3.org/2001/XMLSchema#date');
INSERT INTO type (uri) VALUES ('http://dbpedia.org/ontology/Place');
INSERT INTO type (uri) VALUES ('http://dbpedia.org/ontology/Organisation');
INSERT INTO type (uri) VALUES ('http://dbpedia.org/ontology/Event');
INSERT INTO type (uri) VALUES ('http://dbpedia.org/ontology/Work');
INSERT INTO type (uri) VALUES ('http://dbpedia.org/ontology/Language');
INSERT INTO type (uri) VALUES ('http://dbpedia.org/ontology/Award');
INSERT INTO namedentity (name) VALUES ('PERSON');
INSERT INTO namedentity (name) VALUES ('DATE');
INSERT INTO namedentity (name) VALUES ('GPE');
INSERT INTO namedentity (name) VALUES ('ORG');
INSERT INTO namedentity (name) VALUES ('EVENT');
INSERT INTO namedentity (name) VALUES ('WORK_OF_ART');
INSERT INTO namedentity (name) VALUES ('LANGUAGE');
INSERT INTO type_namedentity_assoc (type, namedentity) VALUES ('http://dbpedia.org/ontology/Person', 'PERSON');
INSERT INTO type_namedentity_assoc (type, namedentity) VALUES ('http://www.w3.org/2001/XMLSchema#date', 'DATE');
INSERT INTO type_namedentity_assoc (type, namedentity) VALUES ('http://dbpedia.org/ontology/Place', 'GPE');
INSERT INTO type_namedentity_assoc (type, namedentity) VALUES ('http://dbpedia.org/ontology/Organisation', 'ORG');
INSERT INTO type_namedentity_assoc (type, namedentity) VALUES ('http://dbpedia.org/ontology/Event', 'EVENT');
INSERT INTO type_namedentity_assoc (type, namedentity) VALUES ('http://dbpedia.org/ontology/Work', 'WORK_OF_ART');
INSERT INTO type_namedentity_assoc (type, namedentity) VALUES ('http://dbpedia.org/ontology/Language', 'LANGUAGE');
INSERT INTO type_namedentity_assoc (type, namedentity) VALUES ('http://dbpedia.org/ontology/Award', 'ORG');

CREATE OR REPLACE VIEW persongpe_candidate AS
SELECT document.id AS docid,
    document.name AS docname,
    persongpe.id AS candid,
    candidate.split,
    sentence.text,
    label.value AS label_value,
    marginal.probability
   FROM persongpe
     JOIN candidate ON candidate.id = persongpe.id
     JOIN span ON persongpe.subject_person_id = span.id
     JOIN sentence ON span.sentence_id = sentence.id
     JOIN document ON sentence.document_id = document.id
     LEFT JOIN label ON candidate.id = label.candidate_id
     LEFT JOIN marginal ON marginal.candidate_id = candidate.id;