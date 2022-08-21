import os.path

import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.datasets import fetch_openml
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder, MinMaxScaler
from sklearn.linear_model import Ridge
from sklearn.tree import DecisionTreeRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import mean_squared_error, mean_absolute_error

import json

import matplotlib.pyplot as plt

from vubros import code_myohe
np.random.seed(0)
def install_setting_of_columns_for_predicted(writer):
    workbook = writer.book
    worksheet = writer.sheets['Sheet1']
    worksheet.autofilter('A1:T1000')
    currency_format = workbook.add_format({'num_format': '# ### ##0₽'})
    date_forman = workbook.add_format({'num_format': 'dd.mm.yy hh:mm'})
    currency_format_with_penny = workbook.add_format({'num_format': '# ### ##0.0₽'})
    format_area = workbook.add_format({'num_format': '# ##0.0м2'})
    format_distance = workbook.add_format({'num_format': '#\ ##0\ \м'})
    format_hyper = workbook.add_format({'font_color': 'blue', 'underline': True})
    center = workbook.add_format()
    center.set_center_across()

    # (max_row, max_col) = df.shape
    # max_row = worksheet.get_highest_row()
    # Регион
    worksheet.set_column('C:C', 3)
    # area
    worksheet.set_column('D:D', 9, format_area)


    worksheet.set_column('E:E', 3)
    worksheet.set_column('G:G', 3)
    #worksheet.set_column('D:D', 23, format_hyper)

    worksheet.set_column('F:F', 5)
    worksheet.set_column('J:J', 5)

    worksheet.set_column('H:H', 7, format_distance)

    worksheet.set_column('I:I', 5, center)

    worksheet.set_column('K:K', 12, currency_format)
    worksheet.set_column('B:B', 12, currency_format)
    #worksheet.set_column('S:T', 22, format_hyper)


    red = workbook.add_format({'bg_color': '#FFC7CE',
                               'font_color': '#9C0006'})
    green = workbook.add_format({'bg_color': '#C6EFCE',
                                 'font_color': '#006100'})

    worksheet.conditional_format('E1:E1000', {'type': 'text',
                                              'criteria': 'containsText',
                                              'value': "PP",
                                              'format': green})
    worksheet.conditional_format('K1:K1000', {'type': 'cell',
                                              'criteria': '<=',
                                              'value': '$B:$B',
                                              'format': green})
    # worksheet.set_column('G:G', 40)
    # worksheet.set_column('F:F', 12, date_forman)
    # worksheet.set_column('U:U', 12)
    # worksheet.set_column('U:U', 17)
    # # worksheet.set_column('T:T', 18)
    # # price
    # # worksheet.set_column('I:K', 9, currency_format)
    # worksheet.set_column('I:I', 9, currency_format)
    # worksheet.set_column('J:K', 8, currency_format_with_penny)
    # worksheet.set_column('L:L', 8, currency_format)
    #
    #
    #
    # worksheet.conditional_format('I1:I1000', {'type': 'cell',
    #                                           'criteria': '<=',
    #                                           'value': 10000,
    #                                           'format': green})
    # worksheet.conditional_format('J1:K1000', {'type': 'cell',
    #                                           'criteria': 'between',
    #                                           'minimum': 0.1,
    #                                           'maximum': 10,
    #                                           'format': green})
    # worksheet.conditional_format('F1:F1000', {'type': 'time_period',
    #                                           'criteria': 'next week',
    #                                           'format': red})
    # worksheet.conditional_format('F1:F1000', {'type': 'time_period',
    #                                           'criteria': 'this week',
    #                                           'format': red})
def loading_data(paths):
    columns = ["Цена за кв.м", "Регион", "Общая площадь", "Форма проведения", "Жителей в округе",
               "Коммерческих объектов", "Жителей h3", "Имущество", "Расстояние до почты", "Этаж"]
    numeric_features = ["Жителей", "Коммерческих объектов", "Общая площадь", "Расстояние до почты"]
    df = pd.DataFrame()
    if type(paths) == list:
        for path in paths:
            df = pd.concat((df, pd.read_excel(path)[columns]), axis=0)
    else:
        df = pd.read_excel(paths)[columns]

    df["Жителей"] = df[["Жителей h3", "Жителей в округе"]].max(axis=1, numeric_only=True)
    df.drop(columns=['Жителей h3', 'Жителей в округе'], axis=1, inplace=True)
    # если жителей в округе 2к значит, точно есть почтовое отделение просто его не смогли найти, не будем учитывать его
    df.loc[((df['Расстояние до почты'].isnull()) & (df["Жителей"] >= 2000)), 'Расстояние до почты'] = 100
    df['Расстояние до почты'].replace(np.nan, 5000, inplace=True)
    df['Коммерческих объектов'].replace(np.nan, 0, inplace=True)
    df['Этаж'].replace(np.nan, 0, inplace=True)
    # data['Этаж'].replace('', 0, inplace=True)
    df['Жителей'].replace('', np.nan, inplace=True)
    df.dropna(subset=['Жителей'], inplace=True)
    df.loc[df["Жителей"] == 'None', "Жителей"] = np.nan
    for name in numeric_features:
        df[name].replace(np.nan, 0, inplace=True)
    df["Этаж"].replace(np.nan, 0, inplace=True)
    df = df.dropna()

    return df
#загрузка данных
#df = pd.concat((pd.read_excel('../torgi/output_archive.xlsx')[columns], pd.read_excel('../torgi/output.xlsx')[columns]), axis=0)
df = loading_data(['../torgi/output_archive.xlsx', '../torgi/output.xlsx'])
target = "Цена за кв.м"
numeric_features = ["Жителей", "Коммерческих объектов", "Общая площадь", "Расстояние до почты"]
categorical_features = ["Регион", "Форма проведения", "Имущество", "Этаж"]
columns = [target] +numeric_features + categorical_features

# Сброс ограничений на количество символов в записи
pd.set_option('display.max_colwidth', None)
pd.set_option('display.max_columns', 10)

print(pd.isnull(df).any())
#смотрим в каких регионах сильный разброс цены за кв.м
df.boxplot(by ='Регион', column =[target], grid = False, figsize=(20,10))
#plt.show()
#убираем их из обучения, так как для них нужно обучать свою модель
df = df[~df["Регион"].isin(set([78,77,40]))]

print(df.info())
print(df.corrwith(df[target]))

y = df["Цена за кв.м"].values
X = df.drop("Цена за кв.м", axis=1)
# X = df[numeric_features+floors+regions+type_auc]
# y = df[target].values
#print(X, y)

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
    steps=[("preprocessor", preprocessor), ("regressor",  DecisionTreeRegressor(max_depth=4))]
)
#KNeighborsRegressor(8)
#DecisionTreeRegressor(max_depth=4)

#X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)

clf.fit(X, y)

df_test = loading_data('../torgi/output_test.xlsx')
df_test = df_test[~df_test["Регион"].isin(set([78,77,40]))]

y_test = df_test["Цена за кв.м"].values
X_test = df_test.drop("Цена за кв.м", axis=1)

print("model train score: %.3f" % clf.score(X, y))
print("model test score: %.3f" % clf.score(X_test, y_test))
print("MAE: %.3f" % mean_absolute_error(y_test, clf.predict(X_test)))

df2 = df_test.copy()
df2['predicted'] = clf.predict(df2[numeric_features+categorical_features])
print(df2)

from export_to_xlsx import save_opening_output_file, install_setting_of_columns
try:
    # что бы можно было оставлять открым файл оутпут
    save_opening_output_file("result_with_predicted.xlsx")
except Exception as _ex:
    print(_ex)

with pd.ExcelWriter("result_with_predicted.xlsx", engine='xlsxwriter', mode="w") as writer:
    df2.to_excel(writer, encoding='utf-8')
    install_setting_of_columns_for_predicted(writer)
    #return