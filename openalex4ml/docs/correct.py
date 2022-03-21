""" Fix the hierarchy violations of the subject assignments by ensuring that each
document is assigned the ancestors of all the subjects it is originally
assigned. """


import json
from os import listdir


def fix_violations(doc_folder, subjects_file, dump_folder):
  """ Correct the hierarchy violations of the files in the given folder. """
  subjects = json.load(open(subjects_file))
  for file in listdir(doc_folder):
    docs = json.load(open(f'{doc_folder}/{file}'))
    correct_docs = {}
    for subject in docs:
      correct_docs[subject] = []
      for doc in docs[subject]:
        correct_docs[subject].append({
          'data': doc['data'],
          'subjects': complete(doc['subjects'], subjects)
        })
    json.dump(correct_docs, open(f'{dump_folder}/{file}', 'w'))


def complete(doc_subjects, all_subjects):
  """ Given the assigned subjects of a document, append the ancestors of each
  subject to the list. """
  complete_subjects = {}
  for subject, score in doc_subjects.items():
    complete_subjects[subject] = score
    for ancestor in all_subjects[subject]['ancestors']:
      if ancestor['id'] not in doc_subjects:
        if ancestor['id'] not in complete_subjects:
          complete_subjects[ancestor['id']] = score
  return complete_subjects
