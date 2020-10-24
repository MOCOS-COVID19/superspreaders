# superspreaders

## Installation
```pip install -r requirements.txt```

## Deep Pavlov configuration

```
pip install deeppavlov
python -m deeppavlov install ner_ontonotes_bert_mult  # Multi-language NER
```

## SpaCy configuration

```
python -m spacy download pl_core_news_lg
```


## Execution
Navigate to the project's main directory (`superspreaders`) and run
```streamlit run src/app.py```
