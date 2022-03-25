""" Compute statistics of a set of documents. """


from os import listdir
import json


def subject_counts(subjects_file, docs_folder, dump_folder):
  """ Iterate over the files in the given folder and count how often each
  subject is assigned to a document. """
  subjects = json.load(open(subjects_file))
  counts = {s['name']: 0 for s in subjects.values()}
  for file in listdir(docs_folder):
    docs = json.load(open(f'{docs_folder}/{file}'))
    for subject in docs:
      for doc in docs[subject]:
        for assigned in doc['subjects']:
          counts[subjects[assigned]['name']] += 1
  json.dump(counts, open(f'{dump_folder}/subject_counts.json', 'w'))


def docs_per_subject(subjects_file, docs_folder, dump_folder):
  """ Iterate over the files in the given folder and count how many docs were
  retrieved for each of the subjects. """
  subjects = json.load(open(subjects_file))
  counts = {s['name']: 0 for s in subjects.values()}
  for file in listdir(docs_folder):
    docs = json.load(open(f'{docs_folder}/{file}'))
    for subject in docs:
      counts[subjects[subject]['name']] = len(docs[subject])
  json.dump(counts, open(f'{dump_folder}/docs_per_subject.json', 'w'))


def subjects_per_doc(docs_folder, dump_folder):
  """ Iterate over the files in the given folder and count how many subjects
  are assigned to each doc. """
  subjects = json.load(open(subjects_file))
  counts = {s['name']: [] for s in subjects.values()}
  for file in listdir(docs_folder):
    docs = json.load(open(f'{docs_folder}/{file}'))
    for subject in docs:
      for doc in docs[subject]:
        counts[subjects[subject]['name']].append(len(doc['subjects']))
  json.dump(counts, open(f'{dump_folder}/subjects_per_doc.json', 'w'))


def count_all(subjects_file, docs_folder, dump_folder):
  """ Run the three functions above. """
  subject_counts(subjects_file, docs_folder, dump_folder)
  docs_per_subject(subjects_file, docs_folder, dump_folder)
  subjects_per_doc(docs_folder, dump_folder)


if __name__ == "__main__":
  subjects_file = 'data/openalex/subjects.json'
  docs_folder = 'data/openalex/docs'
  dump_folder = 'analysis'
  count_all(subjects_file, docs_folder, dump_folder)