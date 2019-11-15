from sklearn.linear_model import SGDClassifier
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from re import split, search
import re
import pandas as pd
import json
from flask import Flask, request
import logging as log

log.basicConfig(
    format=u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s', level=log.DEBUG)
eng = 'ETOPAHKXCBMetopahkxcbmёu'
rus = 'ЕТОРАНКХСВМеторанкхсвмеи'
mapping = str.maketrans(dict(zip(eng, rus)))

app = Flask(__name__)
log.debug('Flask app created')

with open('config.json', encoding='utf-8') as f:
    regexes = json.load(f)['regex']


def fit_model(clf, train, **params):
    texts = train['text']
    texts_labels = train['final']
    model = Pipeline(
        [('tfidf', TfidfVectorizer(ngram_range=(1, 3))), ('clf', clf(**params))])
    model.fit(texts, texts_labels)
    return model


def prepare(train):
    model = fit_model(SGDClassifier, train, **
                      {'loss': 'hinge', 'penalty': 'none', 'learning_rate': 'constant', 'eta0': 0.5})
    return model


def clear(row, type_, exception=''):
    try:
        regex = ''
        communications = ''
        descr = row['Full description'].lower().translate(mapping)
        if exception and search(exception, descr, re.IGNORECASE):
            row.at['predicted'] = 'нет данных'
            return row
        regex = regexes[type_]['regex']
        communications = regexes[type_]['communications']
        sentences = split(r'[.?!;]', row.at['text'].translate(mapping))
        results = []
        found = False
        for s in sentences:
            if search(regex, s, flags=re.IGNORECASE):
                results.append(s)
        if not results:
            for s in sentences:
                if search(communications, s, flags=re.IGNORECASE):
                    results.append(s)
        # if search(regex, descr, re.IGNORECASE) or search(r'(^|\s|,|\()коммуник', descr, re.IGNORECASE):
        #     found = True
        if not results:
            row.at['predicted'] = 'нет данных'
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
                        row.at['text'] = new_descr
                        return row
                for i, e in enumerate(splitted):
                    if search(communications, e, re.IGNORECASE):
                        start = max(i - 20, 0)
                        end = min(i + 21, len(splitted))
                        new_descr = ' '.join(splitted[start: end])
                        row.at['text'] = new_descr
                        return row

            row.at['text'] = descr
    except Exception as e:
        print(f'{e.__class__.__name__}: {e}')
    row.at['text'] = str(row.at['text'])
    return row


def new_start():
    log.info('Loading tables')
    with open('config.json', encoding='utf-8') as f:
        files = json.load(f)['files']
    for t, f in files.items():
        log.debug(f'Loading `{t}`')
        files[t] = pd.read_json(f'files/{f}', orient='records', encoding='cp1251')
        ###
        # if t == 'отделка':
        #     files[t] = files[t].iloc[int(0.8 * len(f)):]
        ###
        log.debug(f'{t} loaded, clearing')
        files[t] = files[t].rename(columns={'Описание': 'text', 'Код': 'id', 'Финал': 'final'})
        files[t]['Full description'] = files[t]['text']
        files[t] = files[t].apply(clear, axis=1, args=(t,))
        log.debug(f'Preparing {t}')
        files[t] = prepare(files[t])
        log.debug(f'{t} prepared')
    return files

files = new_start()


def classify(type_, data, exception=''):
    log.debug(f'Classifying type: {type_}, exception: {exception}')  # ', data: {data}')
    model = files.get(type_)
    if type_ is None:
        log.error('Unresolved type')
        return 'Unresolved type'
    # Paste new models here and into start() func
    test = pd.read_json(json.dumps(data), orient='records')
    test['Full description'] = test['text']  # No need, implemented in start()
    test['predicted'] = [None] * len(test)
    log.debug('Clearing texts')
    test = test.apply(clear, axis=1, args=(type_, exception))
    clear_test = test.loc[test.predicted.isnull()]
    no_test = test.dropna(subset=['predicted'])
    if not clear_test.empty:
        res = model.predict(clear_test['text'])
    else:
        log.error('No valuable records')
        res = clear_test['text']
    clear_test.loc[:, 'predicted'] = res
    full = pd.concat((clear_test, no_test))
    return full[['id', 'text', 'predicted']].to_json(orient='records', force_ascii=False)


@app.route('/clf', methods=['POST'])
def clf():
    js = request.json
    return classify(js['type'], js['data'], js['exception'])


log.debug('Flask app starts')
app.run(host='10.199.13.111', port=9512)
