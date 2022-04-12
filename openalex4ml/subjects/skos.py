""" Create SKOS with the OpenAlex subjects in RDF Turtle format. """


import json


def create_skos(subjects_file, dump_file):
  f = open(dump_file, 'w', encoding='utf-8')
  f.write('@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .\n')
  f.write('@prefix skos: <http://www.w3.org/2004/02/skos/core#> .\n\n')
  subjects = json.load(open(subjects_file, encoding='utf-8'))
  for id, subject in subjects.items():
    f.write(f'<{id}> \n')
    f.write('\trdf:type skos:Concept ;\n')
    f.write(f'\trdf:prefLabel "{subject["name"]}"@en ')
    if len(subject['ancestors']) == 0:
      f.write('.\n\n')
    else:
      for ancestor in subject['ancestors']:
        f.write(';\n')
        f.write(f'\tskos:hasTopConcept <{ancestor["id"]}> ')
      f.write('.\n\n')
