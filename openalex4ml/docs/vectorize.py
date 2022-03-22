""" Vectorize the texts of the documents using the pre-trained fasttext
vectors. You can also use any other file with vectors that has the same
format. """


import json
from os import listdir
import logging


def dump_vecs(docs_folder, vecs_folder, vecs_file):
  """ Retrieve the vectors of the docs and dump them in another folder. """
  fin = open(vecs_file, encoding='utf-8', newline='\n', errors='ignore')
  pretrained = {}
  fin.readline()  # skip first line
  for line in fin:
    tokens = line.rstrip().split(' ')
    pretrained[tokens[0]] = list(map(float, tokens[1:]))
  for file in listdir(docs_folder):
    docs = json.load(open(f'{docs_folder}/{file}', encoding='utf-8'))
    vecs = {}
    for subject in docs:
      vecs[subject] = []
      for doc in docs[subject]:
        vecs[subject].append({'data': [], 'subjects': doc['subjects']})
        for w in doc['data']:
          if w in pretrained:
            vecs[subject][-1]['data'].append(pretrained[w])
        found = len(vecs[subject][-1]["data"])
        logging.info(f'Found {found} vecs for {len(doc["data"])} words')
    json.dump(vecs, open(f'{vecs_folder}/{file}', 'w', encoding='utf-8'))