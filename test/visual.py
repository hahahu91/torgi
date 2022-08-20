
def visualize_data(path_file):
    with open(path_file, encoding='utf8') as f:
        json_data = json.load(f)
        df = json_normalize(json_data['content'])

        df_debtors = df[df['Имущество'].isin(["Должников"])]
        df_municipal = df[df['Имущество'].isin(["Муниципальное"])]
        x1 = df_debtors['Общая площадь'].to_numpy()
        x2 = df_municipal['Общая площадь'].to_numpy()
        # x = df['Общая площадь'].to_numpy()
        y1 = pd.to_numeric(df_debtors['Цена']).to_numpy()
        y2 = pd.to_numeric(df_municipal['Цена']).to_numpy()
        # plt.plot(df['Общая площадь'], pd.to_numeric(df['Цена']))
        [row1, column1] = df_debtors.shape
        [row2, column2] = df_municipal.shape
        # print(x1)
        # print(y1)

        x1 = x1.reshape(row1, 1)
        y1 = y1.reshape(row1, 1)
        x2 = x2.reshape(row2, 1)
        y2 = y2.reshape(row2, 1)
        regr_debt = LinearRegression()
        regr_debt.fit(x1, y1)
        regr_muni = LinearRegression()
        regr_muni.fit(x2, y2)
        #
        # # plot it as in the example at http://scikit-learn.org/
        #plt.subplot(2, 1, 1)
        plt.scatter(x1, y1, color='green')
        plt.plot(x1, regr_debt.predict(x1), color='green', linewidth=2)
        # plt.xticks(())
        # plt.yticks(())
        #plt.subplot(2, 1, 2)
        plt.scatter(x2, y2, color='red')
        plt.plot(x2, regr_muni.predict(x2), color='red', linewidth=2)
        # plt.xticks(())
        # plt.yticks(())
        plt.show()