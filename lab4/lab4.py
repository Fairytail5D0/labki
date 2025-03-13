import numpy as np
import pandas as pd
import timeit


def load_data_pandas():
    df = pd.read_csv('/home/biba/analizlabs/lab4/household_power_consumption.txt', 
                     sep=';', 
                     decimal='.', 
                     na_values=['?'])

    numeric_columns = [
        'Global_active_power', 'Global_reactive_power', 'Voltage', 
        'Global_intensity', 'Sub_metering_1', 'Sub_metering_2', 'Sub_metering_3'
    ]
    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    df['datetime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'], format='%d/%m/%Y %H:%M:%S')

    df.dropna(inplace=True)

    return df


def load_data_numpy():
    types = [
        ("Date", "U10"), ("Time", "U8"), 
        ("Global_active_power", "float64"), ("Global_reactive_power", "float64"),
        ("Voltage", "float64"), ("Global_intensity", "float64"), 
        ("Sub_metering_1", "float64"), ("Sub_metering_2", "float64"), 
        ("Sub_metering_3", "float64")
    ]

    data = np.genfromtxt('/home/biba/analizlabs/lab4/household_power_consumption.txt', 
                         delimiter=';', 
                         dtype=types, 
                         encoding='utf-8', 
                         skip_header=1, 
                         missing_values='?')

    mask = ~np.isnan(data['Global_active_power']) & ~np.isnan(data['Voltage']) & ~np.isnan(data['Global_intensity'])
    data = data[mask]

    hours = np.array([int(t[:2]) for t in data['Time']])
    
    return data, hours


def first_level_tasks(df, np_data, np_hours):
    print("first level tasks:\n")

    def task1_numpy(arr):
        return arr[arr['Global_active_power'] > 5]

    def task1_pandas(dataframe):
        return dataframe[dataframe['Global_active_power'] > 5]

    def task2_numpy(arr):
        return arr[arr['Voltage'] > 235]

    def task2_pandas(dataframe):
        return dataframe[dataframe['Voltage'] > 235]

    def task3_numpy(arr):
        mask = (arr['Global_intensity'] >= 19) & (arr['Global_intensity'] <= 20)
        return arr[mask & (arr['Sub_metering_1'] + arr['Sub_metering_2'] > arr['Sub_metering_3'])]

    def task3_pandas(dataframe):
        mask = (dataframe['Global_intensity'] >= 19) & (dataframe['Global_intensity'] <= 20)
        return dataframe[mask & (dataframe['Sub_metering_1'] + dataframe['Sub_metering_2'] > dataframe['Sub_metering_3'])]

    def task4_numpy(arr):
        sample = np.random.choice(arr, 500000, replace=False)
        submetering_values = np.array(
            [sample['Sub_metering_1'], sample['Sub_metering_2'], sample['Sub_metering_3']]
        ).astype(np.float64)  
        return np.mean(submetering_values, axis=1)

    def task4_pandas(dataframe):
        sample = dataframe.sample(n=500000, random_state=42)
        return sample[['Sub_metering_1', 'Sub_metering_2', 'Sub_metering_3']].mean()

    def task5_numpy(arr, hours):
        mask = (hours > 18) & (arr['Global_active_power'] > 6)
        filtered = arr[mask]

        submetering_values = np.vstack((filtered['Sub_metering_1'], filtered['Sub_metering_2'], filtered['Sub_metering_3'])).T
        
        idx_max = np.argmax(submetering_values, axis=1)

        final_selection = filtered[idx_max == 1]

        mid = len(final_selection) // 2
        result = np.concatenate((final_selection[:mid:3], final_selection[mid::4]))

        return result

    def task5_pandas(dataframe):
        df_filtered = dataframe[(dataframe['datetime'].dt.hour > 18) & (dataframe['Global_active_power'] > 6)]
        df_filtered = df_filtered[df_filtered[['Sub_metering_1', 'Sub_metering_2', 'Sub_metering_3']].idxmax(axis=1) == 'Sub_metering_2']

        first_half = df_filtered.iloc[:len(df_filtered)//2].iloc[::3]
        second_half = df_filtered.iloc[len(df_filtered)//2:].iloc[::4]

        return pd.concat([first_half, second_half])

    tasks = [
        ("Select records > 5 kW", task1_numpy, task1_pandas),
        ("Select records > 235 V", task2_numpy, task2_pandas),
        ("Complex filtering task", task3_numpy, task3_pandas)
    ]

    for task_name, numpy_func, pandas_func in tasks:
        numpy_time = timeit.timeit(lambda: numpy_func(np_data), number=10)
        pandas_time = timeit.timeit(lambda: pandas_func(df), number=10)

        print(f"{task_name}:")
        print(f"NumPy Time: {numpy_time:.4f} s")
        print(f"Pandas Time: {pandas_time:.4f} s")

        if numpy_time < pandas_time:
            print("NumPy  faster for this task")
        else:
            print("Pandas faster for this task")

        print("\n")

    numpy_time_task4 = timeit.timeit(lambda: task4_numpy(np_data), number=10)
    pandas_time_task4 = timeit.timeit(lambda: task4_pandas(df), number=10)

    print("Task 4 (Mean values of selected groups):")
    print(f"NumPy Time: {numpy_time_task4:.4f} s")
    print(f"Pandas Time: {pandas_time_task4:.4f} s")

    mean_values_numpy = task4_numpy(np_data)
    mean_values_pandas = task4_pandas(df)

    print(f"Mean values (NumPy): Sub_metering_1: {mean_values_numpy[0]:.4f}, Sub_metering_2: {mean_values_numpy[1]:.4f}, Sub_metering_3: {mean_values_numpy[2]:.4f}")
    print(f"Mean values (Pandas): Sub_metering_1: {mean_values_pandas['Sub_metering_1']:.4f}, Sub_metering_2: {mean_values_pandas['Sub_metering_2']:.4f}, Sub_metering_3: {mean_values_pandas['Sub_metering_3']:.4f}\n")

    numpy_time_task5 = timeit.timeit(lambda: task5_numpy(np_data, np_hours), number=10)
    pandas_time_task5 = timeit.timeit(lambda: task5_pandas(df), number=10)

    print("Task 5 (Filtered records count):")
    print(f"NumPy Time: {numpy_time_task5:.4f} s")
    print(f"pandas Time: {pandas_time_task5:.4f} s")

    filtered_count_numpy = len(task5_numpy(np_data, np_hours))
    filtered_count_pandas = len(task5_pandas(df))

    print(f"filtered records count (NumPy): {filtered_count_numpy}")
    print(f"filtered records count (Pandas): {filtered_count_pandas}")


def main():
    df = load_data_pandas()
    np_data, np_hours = load_data_numpy()
    first_level_tasks(df, np_data, np_hours)


if __name__ == "__main__":
    main()
