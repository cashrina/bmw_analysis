import pandas as pd
import numpy as np
from sqlalchemy import create_engine

def process_bmw_data(input_path):
    print("Загрузка данных")
    df = pd.read_csv(input_path)

    df.columns = df.columns.str.lower().str.replace(' ','_')
    print("Очистка и переработка")
    df = df.drop_duplicates().dropna(subset=["price","year","mileage"])
    df = df[(df['year'] >= 1990) & (df["year"] <= 2026)]

    current_year = 2026
    df["car_age"] = current_year - df["year"]
    print("Расчет метрик")

    condition = [
        (df['car_age'] <=3) & (df['mileage'] < 30000),
        (df['car_age'] <=7) & (df['mileage'] < 100000),
        (df['car_age'] >15)
    ]

    choices = ['В идеальном состоянии', 'В хорошем состоянии', 'В поддержанном состоянии']
    df['usage_category'] = np.select(condition,choices,default = 'Высокое использование')

    df['price_tier'] = pd.qcut(
        df['price'],
        q=4,
        labels=['Бюджетные', 'Средний класс', 'Премиум', 'Люкс']
    )

    df['annual_mileage'] = (df['mileage']/np.maximum(df['car_age'], 1)).round(1)

    age_factor = np.clip(100-(df['car_age'] * 5),0, 100)
    mileage_factor = np.clip(100 - (df['mileage'] / 2500),0, 100)
    df['liquidity_score'] = ((age_factor * 0.6) + (mileage_factor *0.4)).round(1)

    group_medians = df.groupby(['model', 'year'])['price'].transform('median')
    df['as_bargin'] = df['price'] < (group_medians * 0.85)

    print("Обработка завершена")

    return df

def save_to_postgress(df, table_name='bmw_cars'):
    print("Подключение к Постгресс")
    db_url = "postgresql://superset:superset@localhost:5432/superset"

    engine = create_engine(db_url)

    print(f"Запись {len(df)} строк в таблицу '{table_name}")

    df.to_sql(table_name,engine,if_exists = 'replace', index = False)

    print("Данные загружены в Постгресс")

if __name__ == "__main__":
    input_file = "bmw.csv"
    output_file = "bmw_processed.csv"

    processed_df = process_bmw_data(input_file)
    processed_df.to_csv(output_file, index = False)

    save_to_postgress(processed_df,table_name="bmw_cars")

    print("Подготовка данных")

    
