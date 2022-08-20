#Начнем с загрузки двух наборов данных, индексированных по дате:
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def regres():
    pd.set_option('display.max_columns', 10)
    # Сброс ограничений на количество символов в записи
    pd.set_option('display.max_colwidth', None)

    train = pd.read_excel('../torgi/output_archive.xlsx',
                          usecols=["Регион", "Цена за кв.м", "Общая площадь",  "Коммерческих объектов", "Жителей h3", "Жителей в округе", "Расстояние до почты", "Этаж"])  # index_col=0#counts = pd.read_excel('../torgi/output.xlsx', index_col=0)

    #residence = daily[["Жителей h3", "Жителей в округе"]]
    train["Жителей"] = train[["Жителей h3", "Жителей в округе"]].max(axis=1)
    train.drop(columns=['Жителей h3', 'Жителей в округе'], axis=1, inplace=True)

    train['Расстояние до почты'].replace(np.nan, 5000, inplace=True)
    train['Этаж'].replace(np.nan, 0, inplace=True)
    train['Коммерческих объектов'].replace(np.nan, 0, inplace=True)
    train['Жителей'].replace('', np.nan, inplace=True)
    train.dropna(subset=['Жителей'], inplace=True)
    print(pd.isnull(train).any())


    test = pd.read_excel('../torgi/output_test.xlsx',
                          usecols=["Регион", "Цена за кв.м", "Общая площадь",  "Коммерческих объектов", "Жителей h3", "Жителей в округе", "Расстояние до почты"])  # index_col=0#counts = pd.read_excel('../torgi/output.xlsx', index_col=0)

    #residence = daily[["Жителей h3", "Жителей в округе"]]
    test["Жителей"] = test[["Жителей h3", "Жителей в округе"]].max(axis=1)
    test.drop(columns=['Жителей h3', 'Жителей в округе'], axis=1, inplace=True)

    test['Расстояние до почты'].replace(np.nan, 5000, inplace=True)
    test['Коммерческих объектов'].replace(np.nan, 0, inplace=True)
    test['Жителей'].replace('', np.nan, inplace=True)
    test.dropna(subset=['Жителей'], inplace=True)
    print(pd.isnull(test).any())
    #daily = daily[~daily['Жителей в округе'].isnull()]

    #расброс цена за кв.м
    # plt.figure(figsize=(10,6))
    # plt.hist(daily["Цена за кв.м"], bins=50)
    # plt.xlabel("Цена за кв.м")
    # plt.show()

    # дальность от почты
    # plt.figure(figsize=(10,6))
    # frequency = daily["Расстояние до почты"].value_counts()
    # plt.hist(daily["Цена за кв.м"], bins=50)
    # plt.xlabel("Расстояние до почты")
    # plt.bar(frequency.index, height=frequency)
    # plt.show()

    # #print(daily.describe())
    # print("corr\r\n","--"*50)
    # print("Регион",daily["Цена за кв.м"].corr(daily["Регион"]))
    # print("Площадь", daily["Цена за кв.м"].corr(daily["Общая площадь"]))
    # print("Коммерческих объектов", daily["Цена за кв.м"].corr(daily["Коммерческих объектов"]))
    # print("Жителей", daily["Цена за кв.м"].corr(daily["Жителей"]))
    # print("Расстояние до почты", daily["Цена за кв.м"].corr(daily["Расстояние до почты"]))
    # print(daily.corr())
    #
    # print("--"*50)


    # #визаализируем корреляцию
    # mask=np.zeros_like(daily.corr())
    # triangle_indices = np.triu_indices_from(mask)
    # mask[triangle_indices] = True
    # plt.figure()
    # sns.heatmap(daily.corr(), mask=mask, annot=True)
    # sns.set_style('white')
    # plt.xticks(fontsize=14)
    # plt.yticks(fontsize=14)
    # plt.show()



    #daily = daily.sort_values(by=['Регион']).reset_index(drop=True)

    def code_myohe(data, feature):
        for i in data[feature].unique():
            data[str(i)] = (data[feature] == i).astype(float)

    code_myohe(train, "Регион")
    #print(daily)
    regions = train["Регион"].unique().astype(str)
    #print(regions)
    column_names = ["Общая площадь", "Жителей", "Коммерческих объектов", "Расстояние до почты"]
    column_names.extend(regions)
    train_features = train[column_names]
    train_prices = train["Цена за кв.м"] # Всего


    code_myohe(test, "Регион")
    #print(daily)
    #print(regions)
    features = test[column_names]
    prices = test["Цена за кв.м"] # Всего
    #print(y_log.skew())
    # sns.distplot(y_log)
    # plt.title(f"log price with skew {y_log.skew()}")
    # plt.show()
    # from sklearn.model_selection import train_test_split
    # X_train, X_test, y_train, y_test = train_test_split(features, prices, test_size = 0.9, random_state=10)

    from sklearn.linear_model import LinearRegression
    regr = LinearRegression() #fit_intercept=False
    regr.fit(train_features, train_prices)
    print("training data", regr.score(train_features, train_prices))
    print("test data", regr.score(features, prices))
    print("Intercept", regr.intercept_)

    print(pd.DataFrame(data=regr.coef_, index=train_features.columns, columns=['coef']))

   # return

    # X = daily[column_names]
    # y = daily["Цена за кв.м"] # Всего
    #
    # from sklearn.linear_model import LinearRegression
    # model = LinearRegression() #fit_intercept=False
    # model.fit(X, y)
    test['predicted'] = regr.predict(features)
    # #Сравниваем общий и предсказанный моделью велосипедный трафик визуально
    # #(рис. 5.52):
    test[['Цена за кв.м', 'predicted']].plot(alpha=0.5);
    print(test["predicted"])

    return
    params = pd.Series(regr.coef_, index=features.columns)
    print(params)
    for p in params.items():
        print(p)
    from sklearn.utils import resample
    np.random.seed(1)
    err = np.std([regr.fit(*resample(features, prices)).coef_
    for i in range(1000)], 0)
    #Оценив эти ошибки, взглянем на результаты еще раз:
    print(pd.DataFrame({'effect': params.round(0),
    'error': err.round(0)}))
    # # plt.scatter(daily["Цена за кв.м"], daily['predicted'], color='green')
    # # plt.plot(X, model.predict(X), color='green', linewidth=2)


    plt.show()

regres()