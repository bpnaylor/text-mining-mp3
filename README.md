# text-mining-mp3

## Usage (Windows)

#### 0. 

Pre-process all documents in ``[path_to_data_directory]`` and store results in ``[path_to_processed_data_file].json``.

- Run: ``python preprocess.py [path_to_data_directory] [path_to_stopwords_file] [path_to_processed_data_file].json``

#### 1. 

- Extract top features from preprocessed documents, ranked by chi-square value and information gain:

  - ``python task1.py [path_to_processed_data_file].json > [path_to_controlled_vocab].txt``

- You can also optionally view top ``[num_features]`` features by chi-square value and information gain:

  - Uncomment line 20: ``get_top_features(num_features))`` and update ``num_features`` to the number of desired features (e.g., 20)

  - Run: ``python task1.py [path_to_processed_data_file].json``
  
#### 2. 

Classify all documents as either positive (class==1) or negative (class==0) with a Naive Bayes linear classifier, using the features extracted in step 1 as the controlled vocabulary and additive smoothing for unseen words.

- Display each document id _X_ and decision function of the document _f(X)_, ranked by decision function output.

  - Uncomment line 30, ``document_ranking()``.
  
  - Run ``python task2.py [path_to_processed_data].json [path_to_controlled_vocab].txt``
  
- Display each feature in the controlled dictionary and its log ratio _log(p(w|y=1)/p(w|y=0))_, ranked by log ratios.

  - Uncomment line 29, ``feature_ranking()``.
  
  - Run ``python task2.py [path_to_processed_data].json [path_to_controlled_vocab].txt``

- View precision and recall metrics and plot the precision-recall curve.

  - Uncomment line 31, ``plot_metrics(true_classes,decision_functions)``.
  
  - Run ``python task2.py [path_to_processed_data].json [path_to_controlled_vocab].txt``
