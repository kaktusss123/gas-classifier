import pandas as pd

pd.read_json('files/постройки.json', encoding='cp1251', orient='records').to_excel('')