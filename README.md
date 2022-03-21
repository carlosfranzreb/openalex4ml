# OpenAlex4ML

Package to retrieve documents and subjects from [OpenAlex](https://openalex.org/) to create training datasets for supervised models. You first decide how many subjects you want to consider in the dataset, choosing the number of descending subjects under each of the 19 subjects of the first level. The resulting subjects are then used to retrieve documents that are evenly distributed across the subjects.

## Retrieving subjects

The class `openalex4ml.subjects.SubjectRetriever` retrieves up to _n_ subjects that descend from each of the 19 subjects of the first level, discarding the subjects that are assigned to less than _m_ documents. Discarding rare subjects is useful for two reasons: first, it ensures that the chosen subjects are relevant, as subjects that are seldom assigned to documents will likely also be rare in your dataset, and second, it ensures that there are enough training examples for that subject.

We have tried different thresholds for how many assignments a subject needs to be considered, to strike a balance between picking subjects from the upper levels, which are more general, and picking subjects that are popular. The problem is that the fields differ in popularity. For example, \textit{Medicine} has more than 200 subjects in the third level with more than 25k assigned documents, whereas \textit{Environmental science} only has 31 across all levels. We therefore start with a larger limit, iterate over all levels and all fields, and decrease the limit before iterating again. We first iterate through the descendants of each field and add subjects that are assigned to at least 25,000 publications. If the list of a field does not include 200 subjects after this iteration, we do so again, considering subjects assigned to at least 10,000. We repeat this procedure with 5,000, 1,000 and 100 assignments. When we iterate through the subjects of a field, we start by the second level and descend if necessary.

The numbers of assigned documents stated above (25k, 10k, 5k, 1k and 100) is modified depending on the parameter _m_. All values smaller than _m_ are removed from the list, and _m_ is appended. To avoid uninformative Wikipedia texts such as _"Emotionalism may refer to:"_, we also discard subjects whose description says _"Wikimedia disambiguation page"_ or _"Wikimedia glossary list article"_. The description from a subject comes from the corresponding Wikidata link, through which we later extract the Wikipedia link.

## Retrieving documents

TODO