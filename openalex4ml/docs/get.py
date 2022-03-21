""" Retrieve documents from OpenAlex for each subject. Process the titles and
abstracts before storing them. Keep also the assigned subjects. Use the link
to the works (works_api_url) to find the documents that are assigned each
subject. Save documents in multiple files. """


import requests as req
import json
from os import listdir
import logging
from time import time
from string import ascii_lowercase as letters


from flair.data import Sentence
from flair.tokenization import SpacyTokenizer
from flair.models import SequenceTagger

from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet

import spacy


class DocRetriever:
  def __init__(self, subjects_file):
    self.subjects = json.load(open(subjects_file))
    self.tokenizer = SpacyTokenizer('en_core_web_sm')
    self.lemmatizer = WordNetLemmatizer()
    self.tagger = SequenceTagger.load('upos-fast')
    self.tag_dict = {
      'ADJ': wordnet.ADJ,
      'NOUN': wordnet.NOUN,
      'VERB': wordnet.VERB,
      'ADV': wordnet.ADV
    }
    self.retrieved = []  # IDs of docs that were retrieved
    self.stopwords = spacy.load('en_core_web_sm').Defaults.stop_words
  
  def get_docs(self, url, n=50, process=True, filter=True):
    """ Given the URL leading to the documents of a subject, yield documents
    that are either publications. n is the number of docs that will be yielded.
    If process=True, lemmatize the text; if filter=True, filter the texts. """
    yielded, page = 0, 1
    url += ',type:journal-article&page='
    try:
      while yielded < n:
        res = req.get(f'{url}{page}').json()
        logging.info(f'Fetched page {page}')
        for doc in res['results']:
          if doc['id'] in self.retrieved:
            continue
          abstract_idx = doc['abstract_inverted_index']
          if abstract_idx is not None:
            abstract = self.build_abstract(abstract_idx)
            text = self.append_texts(doc['display_name'], abstract)
            data = self.process_text(text) if process is True else text
            data = self.filter_text(data) if filter is True else data
            yield {
              'data': data,
              'subjects': {s['id']: s['score'] for s in doc['concepts']
                  if s['id'] in self.subjects}
            }
            yielded += 1
            self.retrieved.append(doc['id'])
            if yielded == n:
              logging.info(f'{yielded} docs were found.')
              return
        page += 1
    except Exception as e:
      logging.error(f'An error occurred: {e}')
      logging.info(f'{yielded} docs were found.')
      return

  def process_text(self, text):
    """ Lower-case the string and lemmatize the words. """
    sentence = Sentence(text)
    self.tagger.predict(sentence)
    lemmas = []
    for token in sentence:
      if token.labels[0].value in self.tag_dict:
        lemmas.append(self.lemmatizer.lemmatize(
          token.text.lower(), self.tag_dict[token.labels[0].value])
        )
      else:
        lemmas.append(token.text.lower())
    return lemmas

  def filter_text(self, text):
    """ A word is removed if it either has less than three letters or if it is
    in the given stopwords list. Check only for lower-cased letters, as the
    texts were lower-cased during processing. """
    filtered = []
    for token in text:
      cnt_letters = sum([char in letters for char in token])
      if cnt_letters > 2 and token not in self.stopwords:
        filtered.append(token)
    return filtered  
  
  def build_abstract(self, abstract_idx):
    """ Given an abstract as an inverted index, return it as normal text. """
    text = ''
    n_words = sum([len(v) for v in abstract_idx.values()])
    for i in range(n_words):
      for word in abstract_idx:
        if i in abstract_idx[word]:
          text += word + ' '
    return text
  
  def append_texts(self, title, abstract):
    """ Append the abstract to the text. If the title ends in a score,
    just add them. If not, add the score first. """
    if title[-1] == '.':
      return title + ' ' + abstract
    elif title[-2:] == '. ':
      return title + abstract
    else:
      return title + '. ' + abstract
  

def dump_docs(subjects_file, dump_folder, n_docs=100, n_file=3000,
    process=True, filter=True):
  """ Retrieve 'n_docs' docs for each subject and dump them in the folder
  'data/openalex/docs', with 'n_file' docs per file. n_docs should be a
  factor of n_file. We only check n_file after each subject is done. It can
  occur that a file has more than n_file docs, but never less. """
  retriever = DocRetriever(subjects_file)
  subjects = json.load(open(subjects_file))
  batch = {}
  cnt, file_nr = 0, 1
  for subject, data in subjects.items():
    logging.info(f'Retrieving docs for {subject}')
    batch[subject] = []
    for doc in retriever.get_docs(data['works_api_url'], n_docs, process,
        filter):
      batch[subject].append(doc)
    cnt += len(batch[subject])
    if cnt >= n_file:
      json.dump(batch, open(f'{dump_folder}/{file_nr}.json', 'w'))
      file_nr += 1
      cnt = 0
      batch = {}
  if len(batch) > 0:
    json.dump(batch, open(f'{dump_folder}/{file_nr}.json', 'w'))
