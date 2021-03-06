# OpenAlex4ML

Package to retrieve documents and subjects from [OpenAlex](https://openalex.org/) to create training datasets for supervised models. You first decide how many subjects you want to consider in the dataset, choosing the number of descending subjects under each of the 19 subjects of the first level. The resulting subjects are then used to retrieve documents that are evenly distributed across the subjects.

## Retrieving subjects

The class `openalex4ml.subjects.get.SubjectRetriever` retrieves up to _n_ subjects that descend from each of the 19 subjects of the first level, discarding the subjects that are assigned to less than _m_ documents. Discarding rare subjects is useful for two reasons: first, it ensures that the chosen subjects are relevant, as subjects that are seldom assigned to documents will likely also be rare in your dataset, and second, it ensures that there are enough training examples for that subject.

We have tried different thresholds for how many assignments a subject needs to be considered, to strike a balance between picking subjects from the upper levels, which are more general, and picking subjects that are popular. The problem is that the fields differ in popularity. For example, \textit{Medicine} has more than 200 subjects in the third level with more than 25k assigned documents, whereas \textit{Environmental science} only has 31 across all levels. We therefore start with a larger limit, iterate over all levels and all fields, and decrease the limit before iterating again. We first iterate through the descendants of each field and add subjects that are assigned to at least 25,000 publications. If the list of a field does not include 200 subjects after this iteration, we do so again, considering subjects assigned to at least 10,000. We repeat this procedure with 5,000, 1,000 and 100 assignments. When we iterate through the subjects of a field, we start by the second level and descend if necessary.

The numbers of assigned documents stated above (25k, 10k, 5k, 1k and 100) is modified depending on the parameter _m_. All values smaller than _m_ are removed from the list, and _m_ is appended. To avoid uninformative Wikipedia texts such as _"Emotionalism may refer to:"_, we also discard subjects whose description says _"Wikimedia disambiguation page"_ or _"Wikimedia glossary list article"_. The description from a subject comes from the corresponding Wikidata link, through which we later extract the Wikipedia link.

The class `SubjectRetriever` can be used as follows:

```python
retriever = SubjectRetriever()
retriever.retrieve()
retriever.dump_subjects('dump_file.json')
```

## Subjects as SKOS

Some applications may require the OpenAlex subjects as a SKOS. We provide a function that transforms the JSON file with the subjects to a SKOS in Turtle format in `openalex4ml.subjects.skos`.

## Retrieving documents

Once you have chosen a set of subjects, you can create a training dataset with the function `openalex4ml.docs.get.dump_docs`, which retrieves _n_ documents for each of the subjects. The title and abstract of each document are optionally processed and filtered, before being stored along with all its assigned subjects. We only consider journal articles.

Abstracts are offered by OpenAlex as inverted indices, so they are constructed before processing. The processing consists of lower-casing all words, and lemmatizing them with the `en_core_web_sm` tokenizer from SpaCy, which is assisted by the POS tags computed by Flair's `upos-fast` SequenceTagger. The filtering step removes words that are either in SpaCy's stopword list or have less than three letters.


## Fixing hierarchy violations

The subject assignments of the retrieved documents sometimes don't obey the hierarchy. This happens when a document is assigned a subject but not its ancestors in the subject hierarchy. We provide a function that fixes these violations: `openalex4ml.docs.correct.fix_violations`. Given the folder where the documents are stored, the file with the subjects and a dump folder, it iterates over the documents, adding the ancestors of the assigned subjects if they are not present in the list, as defined in the file with the subjects. It then stores the documents with the correct assignments in the given dump folder.

## Vectorizing the data

We provide a function (`openalex4ml.docs.vectorize.dump_vecs`) to vectorize the data with pre-trained [fasttext vectors](https://fasttext.cc/docs/en/english-vectors.html). We have used the file called _"wiki-news-300d-1M-subword.vec.zip"_, but you can use any other file in this page. Files from another source can also be used, if they provide the vectors in the same format as fasttext. The format is shown in the fasttext website. Remember to unzip the file before feeding it to the vectorizing function.

## Splitting the data

We also provide a function to split the data into training and test sets: `openalex4ml.docs.split.split_data`. This function splits the data given the folder where the vector files are stored, a folder where to dump the split data, and a percentage of documents that should be used for testing. The documents are stored by the subject used to retrieve them, so the splitting occurs evenly across subjects. This means that we split the documents retrieved for each subject independently.

The training files are named with a number, whereas the test file is named `test.json`. Each file contains a list of documents, where each document is represented by a dictionary with the keys `data` and `subjects`, which map to the vector representations of the texts and the assigned subjects, respectively.

## Loading the data

The dataset that results from performing all the above steps can be used to train a PyTorch model with the class `openalex4ml.docs.load.Dataset`. It iterates over the files and returns tuples of the vector representations of documents and its assigned subjects. The subjects are an array with ones for assigned subjects and zeros elsewhere. Both arrays are returned as tensors. The data contained in each file can be optionally shuffled.

This class is a child of PyTorch's `IterableDataset`, and can therefore be fed to the DataLoader class, as shown [here](https://pytorch.org/docs/stable/data.html).

## Analysing the data

The file `openalex4ml.docs.count` contains three functions that can be used to analyse the extracted documents. They compute the following statistics:

1. Number of documents extracted per subject.
2. Number of assignments of each subject.
3. Number of subjects assigned to each document.

## Our dataset

We have used this code to create a training dataset that comprises 2,157 subjects and 214,538 documents. The list of subjects includes up to 200 descendants of each of the 19 fields. We retrieved up to 100 documents per subject, which was possible for all subjects except for 17. Given that we avoid duplicates, many of these subjects were already present in the list of retrieved subjects for other documents. Only for two of these subjects we could not find any documents: _"Algorithm design"_ and _"Premise"_. This may be because we only consider journal articles, and discard documents of any other kind.

In total, there are 1,890,080 subject assignments. 821,273 of these assignments were added to fix hierarchy violations. The field that has benefited the most from fixing the hierarchy violations is _"Engineering"_, which went from being the field with the least assignments (2,565), to having over 60,000 assignments. All fields have more than 20,000 assignments after the corrections, whereas before there were several with less than 5,000 assignments. You can find the resulting subjects and documents in the `data.zip` file.
