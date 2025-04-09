import numpy as np
import pandas as pd
import timeit
import matplotlib.pyplot as plt
from scipy.stats import pearsonr, spearmanr
from sklearn.preprocessing import OneHotEncoder
import seaborn as sns
import csv

def load_data():
    df = pd.read_csv('/home/biba/analizlabs/lab4/imports-85.data', 
                     sep=',', 
                     decimal='.', 
                     na_values=['?'])
    
    column_names = [
    "symboling", "normalized-losses", "make", "fuel-type", "aspiration",
    "num-of-doors", "body-style", "drive-wheels", "engine-location",
    "wheel-base", "length", "width", "height", "curb-weight",
    "engine-type", "num-of-cylinders", "engine-size", "fuel-system",
    "bore", "stroke", "compression-ratio", "horsepower", "peak-rpm",
    "city-mpg", "highway-mpg", "price"
    ]

    df.columns = column_names

    numeric_columns = [
        "symboling", "wheel-base", "length", "width", "height", "curb-weight",
        "engine-size", "bore", "stroke", "compression-ratio", "horsepower",
        "peak-rpm", "city-mpg", "highway-mpg", "price"
    ]

    df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric, errors='coerce')
    
    print("Data loaded into Pandas DataFrame:")
    print(df.head())  # Показуємо перші рядки DataFrame

    data_np = []
    with open('/home/biba/analizlabs/lab4/imports-85.data', 'r') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            data_np.append(row)
    
    data_np = np.array(data_np)
    print("\nData loaded into NumPy array:")
    print(data_np[:5]) 
    
    col_indices = {name: i for i, name in enumerate(column_names)}
    
    return df, data_np, col_indices, numeric_columns

def second_level_tasks(df, data_np, col_indices, numeric_columns):
    print("Second level tasks:\n")
    
    print("Task 1: Handling missing values\n")
    
    print("Missing values before handling:")
    print(df.isnull().sum())
    
    numeric_columns_df = df.select_dtypes(include=['float64', 'int64']).columns
    for col in numeric_columns_df:
        df[col] = df[col].fillna(df[col].median())
    
    categorical_columns = df.select_dtypes(include=['object']).columns
    for col in categorical_columns:
        df[col] = df[col].fillna(df[col].mode()[0])
    
    print("\nMissing values after handling in Pandas DataFrame:")
    print(df.isnull().sum())
    
    print("\nHandling missing values using NumPy arrays:")
    
    horsepower_idx = col_indices['horsepower']
    horsepower_np = np.array([row[horsepower_idx] for row in data_np])
    
    horsepower_np = np.array([float(x) if x != '?' else np.nan for x in horsepower_np])
    
    horsepower_np_clean = horsepower_np[~np.isnan(horsepower_np)]
    median_value = np.median(horsepower_np_clean)
    horsepower_np_filled = np.where(np.isnan(horsepower_np), median_value, horsepower_np)
    print(f"Original NaN count: {np.isnan(horsepower_np).sum()}")
    print(f"After filling NaN count: {np.isnan(horsepower_np_filled).sum()}")
    
    print("\nTask 2: Normalization and Standardization\n")
    
    def normalize(arr):
        return (arr - np.min(arr)) / (np.max(arr) - np.min(arr))
    
    def standardize(arr):
        return (arr - np.mean(arr)) / np.std(arr)

    price_idx = col_indices['price']
    price_np = np.array([float(row[price_idx]) if row[price_idx] != '?' else np.nan for row in data_np])
    price_np = price_np[~np.isnan(price_np)] 
    price_normalized_np = normalize(price_np)
    price_standardized_np = standardize(price_np)
    
    print("NumPy array price statistics:")
    print(f"Original - Min: {np.min(price_np)}, Max: {np.max(price_np)}, Mean: {np.mean(price_np):.2f}, Std: {np.std(price_np):.2f}")
    print(f"Normalized - Min: {np.min(price_normalized_np)}, Max: {np.max(price_normalized_np)}, Mean: {np.mean(price_normalized_np):.2f}, Std: {np.std(price_normalized_np):.2f}")
    print(f"Standardized - Min: {np.min(price_standardized_np):.2f}, Max: {np.max(price_standardized_np):.2f}, Mean: {np.mean(price_standardized_np):.2f}, Std: {np.std(price_standardized_np):.2f}")
    
    df_price_clean = df.dropna(subset=['price'])
    df_numeric = df_price_clean[numeric_columns].copy()
    df_normalized = df_numeric.apply(normalize)
    df_standardized = df_numeric.apply(standardize)
    
    print("\nPandas DataFrame statistics (price column):")
    print(f"Original - Min: {df_price_clean['price'].min()}, Max: {df_price_clean['price'].max()}, Mean: {df_price_clean['price'].mean():.2f}, Std: {df_price_clean['price'].std():.2f}")
    print(f"Normalized - Min: {df_normalized['price'].min()}, Max: {df_normalized['price'].max()}, Mean: {df_normalized['price'].mean():.2f}, Std: {df_normalized['price'].std():.2f}")
    print(f"Standardized - Min: {df_standardized['price'].min():.2f}, Max: {df_standardized['price'].max():.2f}, Mean: {df_standardized['price'].mean():.2f}, Std: {df_standardized['price'].std():.2f}")
    
    print("\nTask 3: Histogram with 10 ranges\n")
    
    plt.figure(figsize=(10, 6))
    plt.subplot(2, 1, 1)
    price_hist, price_bins = np.histogram(price_np, bins=10)
    plt.bar(range(len(price_hist)), price_hist, width=0.8)
    plt.title('Price Histogram (NumPy)')
    plt.xlabel('Price Range')
    plt.ylabel('Frequency')
    
    plt.subplot(2, 1, 2)
    df_price_clean['price'].hist(bins=10, grid=False, color='skyblue')
    plt.title('Price Histogram (Pandas)')
    plt.xlabel('Price')
    plt.ylabel('Frequency')
    plt.tight_layout()
    plt.savefig('price_histogram.png')
    plt.close()
    print("Histogram generated and saved as 'price_histogram.png'")
    
    print("\nTask 4: Scatter plot of two numeric attributes\n")
    
    horsepower_idx = col_indices['horsepower']
    mpg_idx = col_indices['city-mpg']
    
    combined_data = []
    for row in data_np:
        if row[horsepower_idx] != '?' and row[mpg_idx] != '?':
            combined_data.append([float(row[horsepower_idx]), float(row[mpg_idx])])
    
    combined_data = np.array(combined_data)
    horsepower_np = combined_data[:, 0]
    mpg_np = combined_data[:, 1]
    
    plt.figure(figsize=(10, 6))
    plt.subplot(2, 1, 1)
    plt.scatter(horsepower_np, mpg_np, alpha=0.6)
    plt.title('Horsepower vs. City MPG (NumPy)')
    plt.xlabel('Horsepower')
    plt.ylabel('City MPG')
    
    df_scatter = df.dropna(subset=['horsepower', 'city-mpg'])
    plt.subplot(2, 1, 2)
    df_scatter.plot.scatter(x='horsepower', y='city-mpg', alpha=0.6, color='green', ax=plt.gca())
    plt.title('Horsepower vs. City MPG (Pandas)')
    plt.tight_layout()
    plt.savefig('horsepower_vs_mpg.png')
    plt.close()
    print("Scatter plot generated and saved as 'horsepower_vs_mpg.png'")
    
    print("\nTask 5: Pearson and Spearman correlation\n")
    
    pearson_coef, p_value = pearsonr(horsepower_np, mpg_np)
    spearman_coef, s_p_value = spearmanr(horsepower_np, mpg_np)
    
    print("NumPy/SciPy correlation between Horsepower and City MPG:")
    print(f"Pearson correlation coefficient: {pearson_coef:.3f} (p-value: {p_value:.4f})")
    print(f"Spearman correlation coefficient: {spearman_coef:.3f} (p-value: {s_p_value:.4f})")
    
    correlation_df = df_scatter[['horsepower', 'city-mpg']].corr(method='pearson')
    spearman_df = df_scatter[['horsepower', 'city-mpg']].corr(method='spearman')
    
    print("\nPandas correlation between Horsepower and City MPG:")
    print("Pearson correlation matrix:")
    print(correlation_df)
    print("\nSpearman correlation matrix:")
    print(spearman_df)
    
    print("\nTask 6: One-Hot Encoding\n")
    
    make_idx = col_indices['make']
    make_values = [row[make_idx] for row in data_np]
    unique_makes = np.unique(make_values)
    
    make_oh_np = np.zeros((len(make_values), len(unique_makes)))
    for i, make in enumerate(make_values):
        make_idx_in_unique = np.where(unique_makes == make)[0][0]
        make_oh_np[i, make_idx_in_unique] = 1
    
    print(f"NumPy manual One-Hot Encoding shape: {make_oh_np.shape}")
    print(f"Categories: {unique_makes}")
    
    make_array = np.array(make_values).reshape(-1, 1)
    encoder = OneHotEncoder(sparse_output=False)
    make_encoded_np = encoder.fit_transform(make_array)
    print(f"\nNumPy/sklearn One-Hot Encoding shape: {make_encoded_np.shape}")
    print(f"Categories: {encoder.categories_[0]}")
    
    make_encoded_pd = pd.get_dummies(df['make'], prefix='make')
    print(f"\nPandas One-Hot Encoding shape: {make_encoded_pd.shape}")
    print("First 5 columns:", list(make_encoded_pd.columns[:5]))
    
    print("\nTask 7: Visualization of multidimensional data\n")
    
    plt.figure(figsize=(15, 10))
    pair_plot_features = ['horsepower', 'city-mpg', 'price', 'curb-weight']
    df_pair_plot = df.dropna(subset=pair_plot_features)
    sns.pairplot(df_pair_plot[pair_plot_features])
    plt.savefig('pair_plot.png')
    plt.close()
    print("Pair plot generated and saved as 'pair_plot.png'")
    
    plt.figure(figsize=(12, 10))
    correlation_matrix = df_pair_plot[numeric_columns].corr()
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', linewidths=0.5, fmt='.2f')
    plt.title('Correlation Heatmap')
    plt.tight_layout()
    plt.savefig('correlation_heatmap.png')
    plt.close()
    print("Correlation heatmap generated and saved as 'correlation_heatmap.png'")
    
    plt.figure(figsize=(15, 10))
    features_for_parallel = ['horsepower', 'city-mpg', 'engine-size', 'price', 'curb-weight']
    df_parallel = df.dropna(subset=features_for_parallel)
    
    df_normalized = df_parallel[features_for_parallel].copy()
    for col in features_for_parallel:
        df_normalized[col] = (df_normalized[col] - df_normalized[col].min()) / (df_normalized[col].max() - df_normalized[col].min())
    
    df_normalized['make'] = df_parallel['make']
    top_makes = df_parallel['make'].value_counts().nlargest(5).index.tolist()
    df_normalized = df_normalized[df_normalized['make'].isin(top_makes)]
    
    from pandas.plotting import parallel_coordinates
    parallel_coordinates(df_normalized, 'make', colormap='tab10')
    plt.title('Parallel Coordinates Plot')
    plt.grid(False)
    plt.savefig('parallel_coordinates.png')
    plt.close()
    print("Parallel coordinates plot generated and saved as 'parallel_coordinates.png'")

def main():
    df, data_np, col_indices, numeric_columns = load_data()
    second_level_tasks(df, data_np, col_indices, numeric_columns)

if __name__ == "__main__":
    main()
