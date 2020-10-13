from pathlib import Path
PROJECT_DIR = Path(__file__).parents[1].resolve()
DATA_DIR = PROJECT_DIR / 'data'
DATABASE = DATA_DIR / 'search_results.db'
PROCESSED_DATA_DIR = DATA_DIR / 'processed'