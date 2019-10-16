# -*-coding: utf-8-*-
import re
from re import split, search
import pandas as pd

# def clear(row):
#     try:
#         row.at['Full description'] = row.at['Описание']
#         regex = r'(^|\s|,)газ'
#         sentences = split(r'[.?!]', row.at['Описание'])
#         results = []
#         for s in sentences:
#             if search(regex, s, flags=re.IGNORECASE):
#                 results.append(s)
#         if not results:
#             for s in sentences:
#                 if search(r'(^|\s|,)газкоммуник', s, flags=re.IGNORECASE):
#                     results.append(s)
#         if not results:
#             row.at['Predicted'] = 'нет'
#             return row
#         else:
#             descr = ' '.join(results)
#             splitted = list(filter(lambda x: x, split(r'[!?., ]', descr)))
#             new_descr = ''
#             if len(splitted) > 10:
#                 for i, e in enumerate(splitted):
#                     if search(regex, e, re.IGNORECASE):
#                         start = max(i - 10, 0)
#                         end = min(i + 11, len(splitted))
#                         new_descr = ' '.join(splitted[start: end])
#                         break
#             if new_descr:
#                 row.at['Описание'] = new_descr
#             else:
#                 row.at['Описание'] = descr
#     except Exception as e:
#         print(f'{e.__class__.__name__}: {e}')
#     finally:
#         row.at['Описание'] = str(row.at['Описание'])
#         return row


def clear(row):
    try:
        row.at['Full description'] = row.at['Описание']
        regex = r'(^|\s|,)газ'
        sentences = split(r'[.?!]', row.at['Описание'])
        results = []
        for s in sentences:
            if search(regex, s, flags=re.IGNORECASE):
                results.append(s)
        if not results:
            for s in sentences:
                if search(r'(^|\s|,)коммуник', s, flags=re.IGNORECASE):
                    results.append(s)
        if not results:
            row.at['Predicted'] = 'нет'
            return row
        else:
            descr = row['Описание']  # ' '.join(results)
            splitted = list(filter(lambda x: x, split(r'[!?., ]', descr)))
            new_descr = ''
            if len(splitted) > 10:
                for i, e in enumerate(splitted):
                    if search(regex, e, re.IGNORECASE):
                        start = max(i - 10, 0)
                        end = min(i + 11, len(splitted))
                        new_descr = ' '.join(splitted[start: end])
                        break
                else:
                    for i, e in enumerate(splitted):
                        if search(r'(^|\s|,)коммуник', e, re.IGNORECASE):
                            start = max(i - 10, 0)
                            end = min(i + 11, len(splitted))
                            new_descr = ' '.join(splitted[start: end])
                            break
            if new_descr:
                row.at['Описание'] = new_descr
            else:
                row.at['Описание'] = descr
    except Exception as e:
        print(f'{e.__class__.__name__}: {e}')
    finally:
        row.at['Описание'] = str(row.at['Описание'])
        return row
        
# df = pd.read_excel('input.xlsx', sheet_name='газоснабжение', usecols=['Описание', 'Газоснабжение из описания', 'Газоснабжение финал'])
# x = df.iloc[0]
x = pd.Series()
x.at['Predicted'] = None
x.at['Full description'] = None
x.at['Описание'] = 'Продается земельный участок 15 соток ИЖС под строительство дома, расположенный по адресу: Московская область, г.Подольск, ул.Родниковая. Кадастровый номер:50:31:0040803:47. Участок расположен на землях населенных пунктов. Использование земельного участка не ограниченно обременением, природоохранными, санитарными, технологическимии иными зонами. Участок прямоугольной формы со всеми коммуникациями. В 150 м протекает река Лопасня, рядом церковь, в 500 м находится лицей 4, магазины, банк, автобусная отсановка.'
print(clear(x))