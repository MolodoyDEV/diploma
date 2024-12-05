from concurrent.futures import ThreadPoolExecutor
from typing import List

import pandas as pd

from deep_translator import GoogleTranslator

BODY_COL_NAME = 'body'
LABEL_COL_NAME = 'label'
MAX_BODY_LEN = 5_000


def translate_text_batch_to_ru(batch: List[str]) -> List[str]:
    """Max text len is 5000 symbols!"""
    translator = GoogleTranslator(source='auto', target='ru')
    return translator.translate_batch(batch)


def translate_data_to_ru(
        original_path: str,
        target_path: str,
        body_column_name=BODY_COL_NAME,
        label_column_name=LABEL_COL_NAME
):
    df = pd.read_csv(original_path, quotechar='"', delimiter=',', usecols=[body_column_name, label_column_name])
    df = df.reindex(columns=[body_column_name, label_column_name])
    df.columns = [BODY_COL_NAME, LABEL_COL_NAME]
    df[LABEL_COL_NAME] = df[LABEL_COL_NAME].astype(bool)

    df = df.loc[df[BODY_COL_NAME].str.len() < MAX_BODY_LEN]

    def process_chunk(chunk):
        print('process_chunk')
        try:
            chunk[BODY_COL_NAME] = translate_text_batch_to_ru(chunk[BODY_COL_NAME].tolist())
        except Exception as e:
            print(f"TRANSLATION ERROR: {e}")

    chunk_size = 100_000
    chunks = [df[i:i + chunk_size] for i in range(0, df.shape[0], chunk_size)]

    with ThreadPoolExecutor(max_workers=10) as executor:
        executor.map(process_chunk, chunks)

    df = pd.concat(chunks)
    print(df)
    df.to_csv(target_path, index=False)


if __name__ == '__main__':
    translate_data_to_ru(
        'data/original/fraud.csv',
        'data/ru/fraud.csv',
        body_column_name='Body',
        label_column_name='Label'
    )
    translate_data_to_ru(
        'data/original/phishing.csv',
        'data/ru/phishing.csv'
    )
    translate_data_to_ru(
        'data/original/spam.csv',
        'data/ru/spam.csv',
        body_column_name='text'
    )
