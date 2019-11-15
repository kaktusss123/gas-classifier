import pandas as pd

filename = 'постройки'
rename = {
    'Описание': 'Описание',
    'постройки': 'Финал',
    'Код': 'Код'
}

pd.read_excel(f'{filename}.xlsx').rename(columns=rename).to_json(f'{filename}.json', orient='records', force_ascii=False)