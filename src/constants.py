from pathlib import Path
PROJECT_DIR = Path(__file__).parents[1].resolve()
DATA_DIR = PROJECT_DIR / 'data'
DATABASE = DATA_DIR / 'search_results.db'
PROCESSED_DATA_DIR = DATA_DIR / 'processed'


class Classification:
    _CARDINAL_XLSX_FILENAME = 'cardinal_classification.xlsx'
    CARDINAL_PATH = PROCESSED_DATA_DIR / _CARDINAL_XLSX_FILENAME
    _CARDINAL_XLSX_MARKED_FILENAME = 'cardinal_classification_marked.xlsx'
    CARDINAL_MARKED_PATH = PROCESSED_DATA_DIR / _CARDINAL_XLSX_MARKED_FILENAME


class NER:
    CARDINAL = 'CARDINAL'


def ner_beginning(ner: str) -> str:
    return f'B-{ner}'


def ner_inside(ne: str) -> str:
    return f'I-{ne}'
