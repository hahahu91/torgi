#Начнем с загрузки двух наборов данных, индексированных по дате:
import pandas as pd
import numpy as np
daily = pd.read_excel('../torgi/output.xlsx', usecols=["Регион", "Цена за кв.м","Общая площадь", "Cтоимость чел/кв.м", "Жителей в округе", "Коммерческих объектов"]) # index_col=0#counts = pd.read_excel('../torgi/output.xlsx', index_col=0)
print(daily)
daily['Cтоимость чел/кв.м'].replace('', np.nan, inplace=True)
#daily['Жителей h3'].replace('', np.nan, inplace=True)
daily.dropna(subset=['Cтоимость чел/кв.м'], inplace=True)
#daily = daily[~daily['Жителей в округе'].isnull()]
print(daily)

daily = daily.sort_values(by=['Регион']).reset_index(drop=True)

def code_myohe(data, feature):
    for i in data[feature].unique():
        data[str(i)] = (data[feature] == i).astype(float)

code_myohe(daily, "Регион")
print(daily)
regions = daily["Регион"].unique().astype(str)
print(regions)
column_names = ["Общая площадь", "Жителей в округе", "Коммерческих объектов"]
column_names.extend(regions)
print(column_names)
X = daily[column_names]
y = daily["Цена за кв.м"] # Всего

from sklearn.linear_model import LinearRegression
model = LinearRegression() #fit_intercept=False
model.fit(X, y)
daily['predicted'] = model.predict(X)
#Сравниваем общий и предсказанный моделью велосипедный трафик визуально
#(рис. 5.52):
daily[['Цена за кв.м', 'predicted']].plot(alpha=0.5);


params = pd.Series(model.coef_, index=X.columns)
print(params)
for p in params.items():
    print(p)
from sklearn.utils import resample
np.random.seed(1)
err = np.std([model.fit(*resample(X, y)).coef_
for i in range(1000)], 0)
#Оценив эти ошибки, взглянем на результаты еще раз:
print(pd.DataFrame({'effect': params.round(0),
'error': err.round(0)}))
# # plt.scatter(daily["Цена за кв.м"], daily['predicted'], color='green')
# # plt.plot(X, model.predict(X), color='green', linewidth=2)

import matplotlib.pyplot as plt
plt.show()
