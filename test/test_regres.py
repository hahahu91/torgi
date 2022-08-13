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
# print(daily["Регион"].unique())
# regions = ['12', '91', '50', '77', '58', '16', '21']
# for i in regions:
#     daily[regions[i]] = (daily.index.col["Регион"] == i).astype(float)

#weather = pd.read_csv('599021.csv', index_col='DATE', parse_dates=True)
# Далее вычислим общий ежедневный поток велосипедов и поместим эти данные
# в отдельный объект DataFrame:
# daily = counts.resample('d', how='sum')
# daily['Total'] = daily.sum(axis=1)
# daily = daily[['Total']] # удаляем остальные столбцы
# Мы видели ранее, что паттерны использования варьируются день ото дня. Учтем
# это в наших данных, добавив двоичные столбцы-индикаторы дня недели:
# In[16]: days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
# for i in range(7):
# daily[days[i]] = (daily.index.dayofweek == i).astype(float)
# Следует ожидать, что велосипедисты будут вести себя иначе по выходным. До-
# бавим индикаторы и для этого:
# In[17]: from pandas.tseries.holiday import USFederalHolidayCalendar
# cal = USFederalHolidayCalendar()
# holidays = cal.holidays('2012', '2016')
# daily = daily.join(pd.Series(1, index=holidays, name='holiday'))
# daily['holiday'].fillna(0, inplace=True)
# Логично предположить, что свое влияние на количество едущих на велосипедах
# людей окажет и световой день. Воспользуемся стандартными астрономическими
# расчетами для добавления этой информации (рис. 5.51):
# Заглянем глубже: линейная регрессия 455
# In[18]:
# def hours_of_daylight(date, axis=23.44, latitude=47.61):
# """Рассчитываем длительность светового дня для заданной даты"""
# days = (date - pd.datetime(2000, 12, 21)).days
# m = (1. - np.tan(np.radians(latitude))
# * np.tan(np.radians(axis) *
# np.cos(days * 2 * np.pi / 365.25)))
# return 24. * np.degrees(np.arccos(1 - np.clip(m, 0, 2))) / 180.
# daily['daylight_hrs'] = list(map(hours_of_daylight, daily.index))
# daily[['daylight_hrs']].plot();
# Рис. 5.51. Визуализация длительности светового дня в Сиэтле
# Мы также добавим к данным среднюю температуру и общее количество осадков.
# Помимо количества дюймов осадков, добавим еще и флаг для обозначения засуш-
# ливых дней (с нулевым количеством осадков):
# In[19]: # Температуры указаны в десятых долях градуса Цельсия;
# # преобразуем в градусы
# weather['TMIN'] /= 10
# weather['TMAX'] /= 10
# weather['Temp (C)'] = 0.5 * (weather['TMIN'] + weather['TMAX'])
# # Осадки указаны в десятых долях миллиметра; преобразуем в дюймы
# weather['PRCP'] /= 254
# weather['dry day'] = (weather['PRCP'] == 0).astype(int)
# daily = daily.join(weather[['PRCP', 'Temp (C)', 'dry day']])

# Добавим счетчик, который будет увеличиваться, начиная с первого дня, и отмерять
# количество прошедших лет. Он позволит нам отслеживать ежегодные увеличения
# или уменьшения ежедневного количества проезжающих:
# In[20]: daily['annual'] = (daily.index - daily.index[0]).days / 365.
# Теперь наши данные приведены в полный порядок, и мы можем посмотреть на
# них:
# In[21]: daily.head()
# Out[21]:
# Total Mon Tue Wed Thu Fri Sat Sun holiday daylight_hrs \\
# Date
# 2012-10-03 3521 0 0 1 0 0 0 0 0 11.277359
# 2012-10-04 3475 0 0 0 1 0 0 0 0 11.219142
# 2012-10-05 3148 0 0 0 0 1 0 0 0 11.161038
# 2012-10-06 2006 0 0 0 0 0 1 0 0 11.103056
# 2012-10-07 2142 0 0 0 0 0 0 1 0 11.045208
# PRCP Temp (C) dry day annual
# Date
# 2012-10-03 0 13.35 1 0.000000
# 2012-10-04 0 13.60 1 0.002740
# 2012-10-05 0 15.30 1 0.005479
# 2012-10-06 0 15.85 1 0.008219
# 2012-10-07 0 15.85 1 0.010959
# После этого можно выбрать нужные столбцы и обучить линейную регрессионную
# модель на наших данных. Зададим параметр fit_intercept = False, поскольку
# флаги для дней, по сути, выполняют подбор точек пересечения с осями координат
# по дням:
# In[22]:
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
# from sklearn.utils import resample
# np.random.seed(1)
# err = np.std([model.fit(*resample(X, y)).coef_
# for i in range(1000)], 0)
# #Оценив эти ошибки, взглянем на результаты еще раз:
# print(pd.DataFrame({'effect': params.round(0),
# 'error': err.round(0)}))
# # plt.scatter(daily["Цена за кв.м"], daily['predicted'], color='green')
# # plt.plot(X, model.predict(X), color='green', linewidth=2)

import matplotlib.pyplot as plt
plt.show()
