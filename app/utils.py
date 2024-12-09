import pickle
import random

import numpy as np
import pandas as pd
from keras import Model
from keras.src.legacy.preprocessing.text import Tokenizer
from keras.src.utils import pad_sequences

# Параметры токенизации.
max_words = 10000  # Максимальное количество слов для токенации.
max_length = 10  # Максимальная длина последовательности.
BODY_COL_NAME = 'body'
LABEL_COL_NAME = 'label'
RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)
random.seed(RANDOM_SEED)


def create_tokenizer(X: pd.DataFrame) -> Tokenizer:
    tokenizer = Tokenizer(num_words=max_words)
    tokenizer.fit_on_texts(X)
    return tokenizer


def save_tokenizer(tokenizer: Tokenizer, path: str):
    with open(path + '.pickle', 'wb') as f:
        pickle.dump(tokenizer, f)


def load_tokenizer(path: str) -> Tokenizer:
    with open(path + '.pickle', 'rb') as f:
        return pickle.load(f)


def create_pad_sequences(tokenizer: Tokenizer, X: pd.DataFrame) -> pd.DataFrame:
    X = tokenizer.texts_to_sequences(X)
    X = pad_sequences(X, maxlen=max_length)
    return X


def load_model(path: str) -> Model:
    from keras.src.saving import load_model

    model = load_model(f'{path}.h5')
    print("Модель загружена!")
    model.summary()  # Вывод информации о загруженной модели.
    return model


def save_model(model: Model, path: str):
    model.save(f'{path}.h5')
    print("Модель сохранена!")


def clean_text(text):
    text = text.lower()

    for symbol in ['/', '-', '=', '+', 'fw:', 're:', '.']:
        text = text.replace(symbol, '')

    text = text.replace('  ', ' ')
    return text.strip()
