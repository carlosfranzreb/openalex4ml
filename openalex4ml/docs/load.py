""" Load the documents. This class is an argument for PyTorch's DataLoader."""


from os import listdir
import json
from random import shuffle

import torch
from torch.utils.data import IterableDataset


class Dataset(IterableDataset):
  def __init__(self, folder, subjects_file, n_words, n_dims, shuffle=True):
    """ Initializes the Dataset.
    folder (str): location of the folder that contains the training files. The
      file structure is explained in the README.
    subjects_file (str): contains ID, name, etc. of subjects. They are
      mapped to the output neurons by their indices. """
    self.folder = folder
    self.subject_info = json.load(open(subjects_file))
    self.subjects = [subject_id for subject_id in self.subject_info]
    self.n_words = n_words
    self.n_dims = n_dims
    self.shuffle = shuffle
    self.n_docs = len(listdir(self.folder)) * 3000  # aprox
  
  def __len__(self):
    """ Return the number of documents across all files. """
    return self.n_docs

  def __iter__(self):
    """ Iterate over files and return documents-subjects tuples. Files with
    'test' in the name are ignored. The subjects are an array with ones
    for assigned subjects and zeros elsewhere. Both arrays are returned as
    tensors. """
    for file in listdir(self.folder):
      if 'test' in file:
        continue
      docs = json.load(open(f'{self.folder}/{file}', encoding='utf-8'))
      if self.shuffle is True:
        shuffle(docs)
      for doc in docs:
        if len(doc['data']) == 0:  # doc has no words
          continue
        data, labels = self.prepare_data(doc)
        yield data, labels
  
  def prepare_data(self, doc):
    """ Yield vectors and labels after resizing the vectors to fit the number
    of words and converting labels into a one-hot vector. """
    all_data = torch.tensor(doc['data'])
    if all_data.shape[0] >= self.n_words:
      data = all_data[:self.n_words]
    else:
      data = torch.zeros(self.n_words, self.n_dims)
      data[:all_data.shape[0]] = all_data
    subjects = torch.zeros(len(self.subjects))
    for subject in doc['subjects']:
      if subject in self.subjects:
        subjects[self.subjects.index(subject)] = 1
    return data, subjects

  def test_set(self, fname='test'):
    """ Load the test set into a dictionary and return it. If the test file is
    not called 'test', pass the name to the function.  """
    test = json.load(open(f'{self.folder}/{fname}.json'))
    for doc in test:
      if len(doc['data']) == 0:  # doc has no words
        continue
      data, labels = self.prepare_data(doc)
      yield data, labels