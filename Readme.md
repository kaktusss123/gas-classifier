# Классификатор описания

<details> 
  <summary>Описание алгоритма </summary>

При запуске сервиса происходит векторизация данных и обучение модели с использованием данных из файла `input.xlsx`.  
[Источник](http://zabaykin.ru/?p=558)  

TODO:  
- [x] Добавить воду  
- [x] Добавить свет  
- [x] Добавить водные ресурсы
- [x] Добавить межевание
- [x] Добавить лес
- [ ] Добавить доступ к участку
- [ ] Исправить обучающую выборку для водных ресурсов


Параметры модели: 

- Vectorizer: [TfIdf](https://scikit-learn.org/0.21/modules/generated/sklearn.feature_extraction.text.TfidfVectorizer.html)
- Classifier: [SGDClassifier](https://scikit-learn.org/0.20/modules/generated/sklearn.linear_model.SGDClassifier.html)  
- Loss function: [hinge](https://en.wikipedia.org/wiki/Hinge_loss)  
- Regularizator: None  
- Learning rate: constant (eta = eta0)  
- eta0: 0.5  

Данные настройки были выявлены путем тестирования различных моделей с различными параметрами. Наименьшей ошибки удалось добиться именно с этими параметрами. Ошибка составляет около 6% для газа.  

Во входных данных необходимо указать тип тех описаний, которые передаются (газ, свет или вода).  
Также во входных даннх имеется возможность указать регулярное выражение-исключение. В случае нахождения выражения в тексте описания, оно автоматически помечается как `нет данных`.

Также значение `нет данных` присваивается описанию в случае ненахождения шаблона `тип` и шаблона `коммуникации`.

Перед выполнением предсказания происходит очистка описания от лишнего. Оставляется только +-10 слов вокруг ключевой фразы.
</details>

<details>
  <summary>Использование сервиса</summary>
Api url: http://10.199.13.111:9512/clf

Сервис принимает данные в формате json.  
Структура входного json:
```json
{
    "type": "газ|свет|вода|лес|водрес|межевание",
    "exception": "regex",
    "data": [
        {
            "id": 123,
            "text": "Описание"
        },
        {
            "id": 234,
            "text": "Описание2"
        }
    ]
}
```
Структура выходного json:
```json
[
    {
        "id": 123,
        "text": "Описание, обрезанное по ключевой фразе",
        "predicted": "нет|по границе|на участке|недалеко"
    },
    {
        "id": 234,
        "text": "Описание2, обрезанное по ключевой фразе",
        "predicted": "нет|по границе|на участке|недалеко"
    }
]
```
</details>
