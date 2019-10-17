from sklearn.linear_model import SGDClassifier
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from re import split, search
import re
import pandas as pd
import json
from flask import Flask, request


app = Flask(__name__)

def fit_model(clf, train, **params):
    texts = train['Описание']
    texts_labels = train['Газоснабжение финал']
    model = Pipeline(
        [('tfidf', TfidfVectorizer(ngram_range=(1, 3))), ('clf', clf(**params))])
    model.fit(texts, texts_labels)
    return model


def prepare(train):
    model = fit_model(SGDClassifier, train, **
                      {'loss': 'hinge', 'penalty': 'none', 'learning_rate': 'constant', 'eta0': 0.5})
    return model


def clear(row, exception=''):
    try:
        row.at['Full description'] = row.at['Описание']
        descr = row['Описание']  # ' '.join(results)
        if exception and search(exception, descr, re.IGNORECASE):
            row.at['Predicted'] = 'нет данных'
            return row
        regex = r'(^|\s|,|\(|\\)газ(?!(он|пром|пено|бетон| баллон|ет|овик))'
        sentences = split(r'[.?!;]', row.at['Описание'])
        results = []
        found = False
        for s in sentences:
            if search(regex, s, flags=re.IGNORECASE):
                results.append(s)
        if not results:
            for s in sentences:
                if search(r'(^|\s|,)коммуник', s, flags=re.IGNORECASE):
                    results.append(s)
        # if search(regex, descr, re.IGNORECASE) or search(r'(^|\s|,|\()коммуник', descr, re.IGNORECASE):
        #     found = True
        if not results:
            row.at['Predicted'] = 'нет данных'
            return row
        else:
            descr = ' '.join(results)
            splitted = list(filter(lambda x: x, split(r'([:!?., ])', descr)))
            new_descr = ''
            if len(splitted) > 20:
                for i, e in enumerate(splitted):
                    if search(regex, e, re.IGNORECASE):
                        start = max(i - 20, 0)
                        end = min(i + 21, len(splitted))
                        new_descr = ' '.join(splitted[start: end])
                        break
                else:
                    for i, e in enumerate(splitted):
                        if search(r'(^|\s|,|\()коммуник', e, re.IGNORECASE):
                            start = max(i - 20, 0)
                            end = min(i + 21, len(splitted))
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


def start():
    gas = pd.read_excel('gas.xlsx', sheet_name='газоснабжение', usecols=[
                       'Описание', 'Газоснабжение из описания', 'Газоснабжение финал'])
    gas['Full description'] = [None] * len(gas)
    gas = gas.apply(clear, axis=1)
    return prepare(gas)


gas = start()


def classify(type_, data, exception):
    global gas
    if type_ == 'газ':
        model = gas
    # Paste new models here and into start() func
    test = pd.read_json(json.dumps(data), orient='records')
    test['Full description'] = [None] * len(test)
    test['Predicted'] = [None] * len(test)
    test = test.apply(clear, axis=1, args=(exception,))
    clear_test = test.loc[test.Predicted.isnull()]
    no_test = test.dropna(subset=['Predicted'])
    if not clear_test.empty:
        res = model.predict(clear_test['Описание'])
    else:
        res = clear_test['Описание']
    clear_test.loc[:, 'Predicted'] = res
    full = pd.concat((clear_test, no_test))
    return full.to_json(orient='records', force_ascii=False)


@app.route('/clf', methods=['POST'])
def clf():
    js = request.json
    return classify(js['type'], js['data'], js['exception'])

app.run('10.199.13.111', 9512)
