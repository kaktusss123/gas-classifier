import pandas as pd

filename = 'площадь_контексты_исправленные'
rename = {
    'text': 'Описание',
    'Участок?': 'Финал',
    'id': 'Код'
}

pd.read_excel(f'{filename}.xlsx').rename(columns=rename).to_json(f'{filename}.json', orient='records', force_ascii=False)