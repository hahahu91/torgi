import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
#from sklearn.datasets import fetch_openml
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, MinMaxScaler #StandardScaler
from sklearn.linear_model import Ridge
from sklearn.tree import DecisionTreeRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.model_selection import train_test_split #, GridSearchCV
from sklearn.metrics import mean_absolute_error #mean_squared_error

import matplotlib.pyplot as plt

np.random.seed(0)

def remove_row_emissions(data, row_name):
    print("remove emissions ", row_name)
    lower_bound = data[row_name].quantile(q=0.025)
    upper_bound = data[row_name].quantile(q=0.975)
    #print(data)
    data[(data[row_name] < lower_bound) | (data[row_name] > upper_bound)] = np.nan
    data.dropna(subset=[row_name], inplace=True)
#загрузка данных
def loading_data(paths):
    # columns = ["Цена за кв.м", "Регион", "Форма проведения", "Жителей в округе",
    #  "Коммерческих объектов", "Жителей h3", "Имущество", "Расстояние до почты", "Этаж"]
    numeric_features = ["Жителей", "Коммерческих объектов", "Расстояние до почты", "Общая площадь"]
    df = pd.DataFrame()
    if type(paths) == list:
        for path in paths:
            df = pd.concat((df, pd.read_excel(path),), axis=0)
    else:
        df = pd.read_excel(paths)

    df["Жителей"] = df[["Жителей h3", "Жителей в округе"]].max(axis=1, numeric_only=True)
    df.drop(columns=['Жителей h3', 'Жителей в округе'], axis=1, inplace=True)
    # если жителей в округе 2к значит, точно есть почтовое отделение просто его не смогли найти, не будем учитывать его
    df.loc[((df['Расстояние до почты'].isnull()) & (df["Жителей"] >= 2000)), 'Расстояние до почты'] = 100
    df['Расстояние до почты'].replace(np.nan, 5000, inplace=True)
    df['Коммерческих объектов'].replace(np.nan, 0, inplace=True)
    df['Этаж'].replace(np.nan, 0, inplace=True)
    df['Жителей'].replace('', np.nan, inplace=True)
    df.loc[df["Жителей"] == 'None', "Жителей"] = np.nan

    df.dropna(subset=['Жителей'], inplace=True)
    for name in numeric_features:
        df[name].replace(np.nan, 0, inplace=True)
    df["Этаж"].replace(np.nan, 0, inplace=True)
    # df = df.dropna()

    return df

def get_predicted():
    df = loading_data(['../torgi/output_archive.xlsx', '../torgi/output_train.xlsx'])
    # print(pd.isnull(df).any())
    # print(df)

    target = "Цена за кв.м"
    numeric_features = ["Жителей", "Коммерческих объектов", "Расстояние до почты", "Общая площадь"]
    categorical_features = ["Регион", "Форма проведения", "Имущество", "Этаж"]
    columns = [target] +numeric_features + categorical_features

    # Сброс ограничений на количество символов в записи
    pd.set_option('display.max_colwidth', None)
    pd.set_option('display.max_columns', 10)

    #смотрим в каких регионах сильный разброс цены за кв.м
    df.boxplot(by ='Регион', column =[target], grid = False, figsize=(20,10))

    #удаляем выбросы
    remove_row_emissions(df, "Цена за кв.м")

    # print(df.info())
    # print(df.corrwith(df[target]))

    numeric_transformer = Pipeline(
        steps=[("imputer", SimpleImputer(strategy='median')), ("scaler", MinMaxScaler())]
    )
    #SimpleImputer(strategy='constant', fill_value=1)

    categorical_transformer = OneHotEncoder(handle_unknown="ignore")

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, numeric_features),
            ("cat", categorical_transformer, categorical_features),
        ]
    )

    clf = Pipeline(
        steps=[("preprocessor", preprocessor), ("regressor", KNeighborsRegressor(8))]
    )
    #Ridge(alpha=10)
        #model train score: 0.367
        #model test score: 0.300
        #MAE: 10674.231

    #KNeighborsRegressor(8)
        #model train score: 0.405
        #model test score: 0.305
        #MAE: 10418.642
    #DecisionTreeRegressor(max_depth=4)
        #model train score: 0.435
        #model test score: 0.121
        #MAE: 11433.182

    #тренируем модель
    y = df["Цена за кв.м"].values
    X = df[numeric_features + categorical_features]
    # print(X)
    df_test = loading_data('../torgi/output_test.xlsx')
    df_test = df_test[~df_test["Регион"].isin(set([78,77]))]

    y_test = df_test["Цена за кв.м"].values
    X_test = df_test[numeric_features + categorical_features]

    clf.fit(X, y)

    # X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)
    # clf.fit(X_train, y_train)

    print("model train score: %.3f" % clf.score(X, y))
    print("model test score: %.3f" % clf.score(X_test, y_test))
    print("MAE: %.3f" % mean_absolute_error(y_test, clf.predict(X_test)))

    df2 = df_test.copy()
    df2['predicted'] = clf.predict(df2[numeric_features+categorical_features])
    # print(df2)

    from export_to_xlsx import save_opening_output_file, set_predicted_in_xls
    try:
        # что бы можно было оставлять открым файл оутпут
        save_opening_output_file("../torgi/output_test.xlsx")
    except Exception as _ex:
        print(_ex)

    set_predicted_in_xls("../torgi/output_test.xlsx", df2)

if __name__ == "__main__":
    get_predicted()
