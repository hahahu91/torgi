#Начнем с загрузки двух наборов данных, индексированных по дате:
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


from sklearn import preprocessing


def code_myohe(data, feature):
    for i in data[feature].unique():
        data[str(i)] = (data[feature] == i).astype(float)

def regres_with_scaler():
    pd.set_option('display.max_columns', 10)
    # Сброс ограничений на количество символов в записи
    pd.set_option('display.max_colwidth', None)

    data = pd.read_excel('../torgi/output_archive.xlsx',
                          usecols=["Регион", "Цена за кв.м", "Общая площадь", "Коммерческих объектов", "Жителей h3",
                                   "Жителей в округе",
                                   "Расстояние до почты", "Этаж"])  # index_col=0#counts = pd.read_excel('../torgi/output.xlsx', index_col=0)

    # residence = daily[["Жителей h3", "Жителей в округе"]]
    data["Жителей"] = data[["Жителей h3", "Жителей в округе"]].max(axis=1)
    data.drop(columns=['Жителей h3', 'Жителей в округе'], axis=1, inplace=True)

    data['Расстояние до почты'].replace(np.nan, 5000, inplace=True)
    data['Коммерческих объектов'].replace(np.nan, 0, inplace=True)
    data['Этаж'].replace(np.nan, 0, inplace=True)
    #data['Этаж'].replace('', 0, inplace=True)
    data['Жителей'].replace('', np.nan, inplace=True)
    data.dropna(subset=['Жителей'], inplace=True)
    print(pd.isnull(data).any())
    code_myohe(data, "Регион")
    # print(daily)
    regions = data["Регион"].unique().astype(str)
    data.drop("Регион", axis=1, inplace=True)

    print(data)
    column_names = ["Общая площадь", "Жителей", "Коммерческих объектов", "Расстояние до почты"]

    column_names.extend(regions)

    features = data[column_names]
    prices = data["Цена за кв.м"]  # Всего
##

    scaler = preprocessing.MinMaxScaler()
    d = scaler.fit_transform(features)
    scaled_df = pd.DataFrame(d, columns=column_names)
    scaled_df["Этаж"] = data["Этаж"]
    scaled_df['Этаж'].replace(np.nan, 0, inplace=True)
    print(pd.isnull(scaled_df).any())
    #print(scaled_df["Этаж"])
    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(scaled_df, prices, test_size = 0.8, random_state=10)

    #return
    print(X_train)
   # return
    from sklearn.linear_model import LinearRegression

    regr = LinearRegression()  #fit_intercept=False

    regr.fit(X_train.values, y_train)
    print("training data", regr.score(X_train.values, y_train))
    print("test data", regr.score(X_test.values, y_test))
    print("Intercept", regr.intercept_)
    print(pd.DataFrame(data=regr.coef_, index=scaled_df.columns, columns=['coef']))



    # X = daily[column_names]
    # y = daily["Цена за кв.м"] # Всего
    #
    # from sklearn.linear_model import LinearRegression
    # model = LinearRegression() #fit_intercept=False
    # model.fit(X, y)
    # data['predicted'] = regr.predict(scaled_df)
    # # #Сравниваем общий и предсказанный моделью велосипедный трафик визуально
    # # #(рис. 5.52):
    # data[['Цена за кв.м', 'predicted']].plot(alpha=0.5);
    # print(data["predicted"])

    # #расброс цена за кв.м
    # plt.figure(figsize=(10,6))
    # plt.hist(data["Цена за кв.м"], bins=50)
    # plt.xlabel("Цена за кв.м")
    # plt.show()

    ##дальность от почты
    # plt.figure(figsize=(10,6))
    # frequency = scaled_df["Расстояние до почты"].value_counts()
    # plt.hist(data["Цена за кв.м"], bins=50)
    # plt.xlabel("Расстояние до почты")
    # plt.bar(frequency.index, height=frequency)
    # plt.show()

    # print(scaled_df.describe())
    # print("corr\r\n","--"*50)
    # print("Площадь", data["Цена за кв.м"].corr(scaled_df["Общая площадь"]))
    # print("Коммерческих объектов", data["Цена за кв.м"].corr(scaled_df["Коммерческих объектов"]))
    # print("Жителей", data["Цена за кв.м"].corr(scaled_df["Жителей"]))
    # print("Расстояние до почты", data["Цена за кв.м"].corr(scaled_df["Расстояние до почты"]))
    # print(scaled_df.corr())
    #
    # print("--"*50)


    # #визаализируем корреляцию
    # mask=np.zeros_like(scaled_df.corr())
    # triangle_indices = np.triu_indices_from(mask)
    # mask[triangle_indices] = True
    # plt.figure()
    # sns.heatmap(scaled_df.corr(), mask=mask, annot=True)
    # sns.set_style('white')
    # plt.xticks(fontsize=14)
    # plt.yticks(fontsize=14)
    # plt.show()

regres_with_scaler()
#regres()