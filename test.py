from sklearn.linear_model import SGDClassifier
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from re import split, search
import re
import pandas as pd
import json
from flask import Flask, request
import logging as log

log.basicConfig(format = u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s', level = log.DEBUG)
eng = 'ETOPAHKXCBMetopahkxcbm'
rus = 'ЕТОРАНКХСВМеторанкхсвм'
mapping = str.maketrans(dict(zip(eng, rus)))

# app = Flask(__name__)
log.debug('Flask app created')


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
        if type_ == 'газ':
            regex = r'(^|\s|\W|\d)газ(?!(он|пром|пено|бетон| баллон|ет|овик))'
            communications = r'(^|\s|\W|\d)коммуник'
        elif type_ == 'свет':
            regex = r'(^|\s|\W|\d)(электрич|свет)(?!к)'
            communications = r'(^|\s|\W|\d)коммуник'
        elif type_ == 'лес':
            regex = r'(^|\s|\W|при|\d)(лес|сосн[ыа])'
            communications = r'(^|\s|\W|\d)хвойн'
        elif type_ == 'водрес':
            regex = r'(^|\s|\W|\d)(озер|ре[чк]|водоем|водохр)'
            communications = r'(^|\s|\W|\d)(пляж|рыбал|берег|пруд)'
        elif type_ == 'вода':
            regex = r'(^|\s|\W|\d)(водо(пров|снабж)|коло(д[ец]|нк)|скважин)'
            communications = r'(^|\s|\W|\d)(вод[аы]|коммуник)'
        elif type_ == 'межевание':
            regex = r'(^|\s|\W|от|раз|до|об|за|про|\d)(меж[еёо]|геодез)'
            communications = r'(^|\s|\W|\d)границы'
        elif type_ == 'доступ':
            regex = r'(^|\s|\W|\d|за)(асфальт|грави|щеб[ен]|грунт)'
            communications = r'(^|\s|\W|\d)(бетон|насып)'
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
            print(descr, end='\n\n')
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


def start():
    ###
    # Debug only
    ###
    gas, electro, forest, river, plumbing, mezh, dostup = None, None, None, None, None, None, None


    log.debug('Pre-start')
    # gas = pd.read_excel('input.xlsx', sheet_name='газоснабжение', usecols=[
    #     'Описание', 'Газоснабжение финал'])
    # log.debug('Gas loaded')
    # gas = gas.rename(columns={'Описание': 'text', 'Газоснабжение финал': 'final'})
    # gas['Full description'] = gas['text']
    # gas = gas.apply(clear, axis=1, args=('газ',))
    # log.debug('Preparing gas...')
    # gas = prepare(gas)
    # log.debug('Gas prepared')
    # electro = pd.read_excel('input.xlsx', sheet_name='электричество', usecols=[
    #     'Описание', 'Электричество финал']).rename(columns={'Описание': 'text', 'Электричество финал': 'final'})
    # log.debug('Electricity loaded')
    # electro['Full description'] = electro['text']
    # electro = electro.apply(clear, axis=1, args=('свет',))
    # log.debug('Preparing electricity...')
    # electro = prepare(electro)
    # log.debug('Electricity prepared')
    # forest = pd.read_excel('input.xlsx', sheet_name='лесные ресурсы', usecols=['Описание', 'Лес из описания финал'])
    # log.debug('Forest loaded')
    # forest = forest.rename(columns={'Описание': 'text', 'Лес из описания финал': 'final'})
    # forest['Full description'] = forest['text']
    # forest = forest.apply(clear, axis=1, args=('лес',))
    # log.debug('Preparing forest...')
    # forest = prepare(forest)
    # log.debug('Forest prepared')

    # river = pd.read_excel('input.xlsx', sheet_name='водные ресурсы', usecols=['Описание', 'Водные ресурсы из описания финал'])
    # log.debug('River loaded')
    # river = river.rename(columns={'Описание': 'text', 'Водные ресурсы из описания финал': 'final'})
    # river['Full description'] = river['text']
    # river = river.apply(clear, axis=1, args=('водрес',))
    # log.debug('Preparing river...')
    # river = prepare(river)
    # log.debug('River prepared')

    # plumbing = pd.read_excel('input.xlsx', sheet_name='водоснабжение', usecols=['Описание', 'Водоснабжение финал'])
    # log.debug('Plumbing loaded')
    # plumbing = plumbing.rename(columns={'Описание': 'text', 'Водоснабжение финал': 'final'})
    # plumbing['Full description'] = plumbing['text']
    # plumbing = plumbing.apply(clear, axis=1, args=('вода',))
    # log.debug('Preparing plumbing...')
    # plumbing = prepare(plumbing)
    # log.debug('Plumbing prepared')

    # mezh = pd.read_excel('input.xlsx', sheet_name='межевание', usecols=['Описание', 'Межевание'])
    # log.debug('Mezh loaded')
    # mezh = mezh.rename(columns={'Описание': 'text', 'Межевание': 'final'})
    # mezh['Full description'] = mezh['text']
    # mezh = mezh.apply(clear, axis=1, args=('межевание',))
    # log.debug('Preparing mezh...')
    # mezh = prepare(mezh)
    # log.debug('Mezh prepared')

    dostup = pd.read_excel('input.xlsx', sheet_name='доступ к участку', usecols=['Описание', 'Доступ к участку финал'])
    ###
    dostup = dostup.iloc[:int(0.8 * len(dostup))]
    ###
    log.debug('Dostup loaded')
    dostup = dostup.rename(columns={'Описание': 'text', 'Доступ к участку финал': 'final'})
    dostup['Full description'] = dostup['text']
    dostup = dostup.apply(clear, axis=1, args=('доступ',))
    log.debug('Preparing dostup...')
    dostup = prepare(dostup)
    log.debug('Dostup prepared')
    return gas, electro, forest, river, plumbing, mezh, dostup


gas, electro, forest, river, plumbing, mezh, dostup = start()


def classify(type_, data, exception=''):
    log.debug(f'Classifying type: {type_}, exception: {exception}, data: {data}')
    global gas, electro, forest, river, plumbing, mezh
    if type_ == 'газ':
        log.debug('Selected model `газ`')
        model = gas
    elif type_ == 'свет':
        log.debug('Selected model `свет`')
        model = electro
    elif type_ == 'лес':
        log.debug('Selected model `лес`')
        model = forest
    elif type_ == 'водрес':
        log.debug('Selected model `водные ресурсы`')
        model = river
    elif type_ == 'вода':
        log.debug('Selected model `водоснабжение`')
        model = plumbing
    elif type_ == 'межевание':
        log.debug('Selected model `межевание`')
        model = mezh
    elif type_ == 'доступ':
        log.debug('Selected model `доступ к участку`')
        model = dostup
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
    return full[['id', 'text', 'predicted', 'final']].to_json(orient='records', force_ascii=False)


# @app.route('/clf', methods=['POST'])
# def clf():
#     js = request.json
#     return classify(js['type'], js['data'], js['exception'])


def test_model():
    log.debug('Reding test')
    test_forest = pd.read_excel('input.xlsx', sheet_name='доступ к участку', usecols=['Описание', 'Доступ к участку финал', 'Уникальный идентификационный номер'])
    test_forest = test_forest.iloc[int(0.2 * len(test_forest)):]
    test_forest = test_forest.rename(columns={'Описание': 'text', 'Доступ к участку финал': 'final', 'Уникальный идентификационный номер': 'id'})
    test_forest['Full description'] = test_forest['text']
    data = {"type": "доступ", "data": test_forest.to_dict(orient='records')}
    log.debug('Testing...')
    result = classify(data['type'], data['data'])
    log.debug('Writing...')
    result = pd.read_json(result, orient='records')
    result.to_excel('dostup_result.xlsx')



log.debug('Flask app starts')
# app.run()
test_model()

