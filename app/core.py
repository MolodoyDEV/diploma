from typing import Dict

import pandas as pd

from app import model_by_name, translator_to_en
from app.utils import clean_text, BODY_COL_NAME, create_pad_sequences


def predict(message: str) -> Dict[str, float]:
    message = clean_text(message)

    if not message:
        raise ValueError("Empty message after cleaning!")

    message = translator_to_en.translate(message)

    df = pd.DataFrame([message], columns=[BODY_COL_NAME])
    result_by_model_name: Dict[str, float] = {}

    for name, data in model_by_name.items():
        tokenizer = data['tokenizer']
        model = data['model']
        message_pad = create_pad_sequences(tokenizer, df[BODY_COL_NAME])
        prediction = model.predict(message_pad)
        prediction = prediction[0][0]
        result_by_model_name[name] = prediction

    return result_by_model_name
