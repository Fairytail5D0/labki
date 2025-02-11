import urllib.request
import pandas as pd
from datetime import datetime
import os
import glob
import time 

REGIONS = {
    1: 'Вінницька', 2: 'Волинська', 3: 'Дніпропетровська', 4: 'Донецька', 5: 'Житомирська',
    6: 'Закарпатська', 7: 'Запорізька', 8: 'Івано-Франківська', 9: 'Київська', 10: 'Кіровоградська',
    11: 'Луганська', 12: 'Львівська', 13: 'Миколаївська', 14: 'Одеська', 15: 'Полтавська',
    16: 'Рівенська', 17: 'Сумська', 18: 'Тернопільська', 19: 'Харківська', 20: 'Херсонська',
    21: 'Хмельницька', 22: 'Черкаська', 23: 'Чернівецька', 24: 'Чернігівська', 25: 'Республіка Крим',26: 'Київ',27:'Севастополь',
}


NOAA_TO_UA = {
    1: 22,  2: 24,  3: 23,  4: 25,   5: 3,   6: 4,  7: 8,  8: 19,   
    9: 20, 10: 21, 11: 9, 12: 26, 13: 10, 14: 11, 15: 12, 16: 13,  
    17: 14, 18: 15, 19: 16,  20: 27,  21: 17,  22: 18,  23: 6,  24: 1,  
    25: 2 , 26: 7, 27: 5 
}

def print_regions():
    """ Виводить список областей у зручному форматі """
    print("\nregions of Ukraine")
    for i in range(1, 28, 2):  
        r1 = f"{i}. {REGIONS[i]:<18}"  
        r2 = f"{i+1}. {REGIONS[i+1]}" if i+1 in REGIONS else ""  
        print(f"{r1} {r2}")
    print()

def download_vhi_data(ua_id, directory="vhi_data"):
    """
    Завантажує дані VHI для вказаної області, конвертуючи український індекс в NOAA
    та зберігає їх у зазначену директорію.
    """
    if not os.path.exists(directory):
        os.makedirs(directory)  # Створює директорію, якщо її немає
    
    noaa_id = list(NOAA_TO_UA.keys())[list(NOAA_TO_UA.values()).index(ua_id)]  
    url = f"https://www.star.nesdis.noaa.gov/smcd/emb/vci/VH/get_TS_admin.php?country=UKR&provinceID={noaa_id}&year1=1981&year2=2024&type=Mean"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f'vhi_{REGIONS[ua_id]}_{timestamp}.csv'
    filepath = os.path.join(directory, filename)  # Зберігаємо файл у вказану директорію
    
    try:
        vhi_url = urllib.request.urlopen(url)
        with open(filepath, 'wb') as out:
            out.write(vhi_url.read())
        print(f"data fro {REGIONS[ua_id]} (ID: {ua_id}, NOAA ID: {noaa_id}) dawnloaded in  {filepath}\n")
        return filepath
    except Exception as e:
        print(f"error downloading for the province {REGIONS[ua_id]}: {e}\n")
        return None

def download_all_regions_vhi(directory="vhi_data", delay=2):
    """
    Завантажує дані VHI для всіх регіонів України з невеликою затримкою між запитами
    """
    print("starting to download data for all provincees...")
    downloaded_files = []
    
   
    for region_id in range(1, 28):
        try:
            # Невелика затримка між запитами, щоб не перевантажувати сервер
            time.sleep(delay)
            
            file_path = download_vhi_data(region_id, directory)
            if file_path:
                downloaded_files.append(file_path)
        except Exception as e:
            print(f"error downloading for the province  {region_id}: {e}")
    
    print(f"download completed.{len(downloaded_files)} файлів.")
    return downloaded_files
    
#-----------------------------------------------------------------------------    
 


def read_vhi_files(directory="vhi_data"):
    """
    Зчитує всі CSV файли з вказаної директорії у єдиний DataFrame
    з урахуванням нової структури імен файлів
    """
    # Шаблон для пошуку файлів
    all_files = glob.glob(os.path.join(directory, "vhi_*_*.csv"))
    df_list = []
    
    if not all_files:
        print("⚠ Вказана директорія не містить файлів з VHI даними.")
    
    for filename in all_files:
        print(f"📄 Читання файлу: {filename}...")
        df = pd.read_csv(filename, index_col=False, header=1)
        df.columns = ['Year', 'Week', 'SMN', 'SMT', 'VCI', 'TCI', 'VHI', 'Region']
        df_list.append(df)
    
    if df_list:
        print(f"✅ Завантажено {len(df_list)} файлів VHI даних.")
        return pd.concat(df_list, ignore_index=True)
    else:
        print("⚠ Не вдалося зчитати жодного файлу.")
        return pd.DataFrame()

def update_region_indices(df):
    """
    Оновлює індекси областей згідно з українською класифікацією
    """
    print("updating indexes...")
    df['Region_Name'] = df['Region'].map(REGIONS)
    print("indexes updated")
    return df

def get_vhi_for_region_year(df, region_id, year):
    """
    Повертає ряд VHI для вказаної області та року
    """
    result = df[(df['Region'] == region_id) & (df['Year'] == year)][['Week', 'VHI']]
    print(f"📊 Дані VHI для області {REGIONS[region_id]} за {year} рік:")
    print(result)
    return result

def get_vhi_extremes(df, region_ids, years):
    """
    Знаходить екстремуми VHI для вказаних областей та років
    """
    filtered_df = df[(df['Region'].isin(region_ids)) & (df['Year'].isin(years))]
    if filtered_df.empty:
        print("⚠ Не знайдено даних для вказаних областей або років.")
        return None
    
    stats = {
        'min_vhi': filtered_df['VHI'].min(),
        'max_vhi': filtered_df['VHI'].max(),
        'mean_vhi': filtered_df['VHI'].mean(),
        'median_vhi': filtered_df['VHI'].median()
    }
    
    print(f"📈 Статистика для VHI в області/роках {region_ids} та {years}:")
    print(f"Мінімальний VHI: {stats['min_vhi']}")
    print(f"Максимальний VHI: {stats['max_vhi']}")
    print(f"Середнє VHI: {stats['mean_vhi']}")
    print(f"Медіана VHI: {stats['median_vhi']}")
    
    return stats

def get_vhi_range(df, region_ids, start_year, end_year):
    """
    Повертає ряд VHI за вказаний діапазон років для вказаних областей
    """
    result = df[(df['Region'].isin(region_ids)) & (df['Year'].between(start_year, end_year))][['Year', 'Week', 'Region', 'VHI']]
    print(f"📊 Діапазон VHI для областей {region_ids} з {start_year} по {end_year}:")
    print(result)
    return result

def find_extreme_droughts(df, threshold_percent=20):
    """
    Знаходить роки з екстремальними посухами, що торкнулися більше вказаного відсотка областей
    """
    results = []
    total_regions = 25
    threshold_regions = int(total_regions * threshold_percent / 100)
    
    print(f"🔍 Пошук екстремальних посух, що торкнулися більше ніж {threshold_percent}% областей...")
    
    for year in df['Year'].unique():
        year_data = df[df['Year'] == year]
        drought_regions = year_data[year_data['VHI'] < 15]['Region'].unique()
        
        if len(drought_regions) >= threshold_regions:
            results.append({
                'year': year,
                'affected_regions': len(drought_regions),
                'regions': [REGIONS[r] for r in drought_regions if r in REGIONS],
                'vhi_values': year_data[year_data['Region'].isin(drought_regions)]['VHI'].tolist()
            })
    
    if results:
        print(f"✅ Знайдено {len(results)} років з екстремальними посухами.")
        for result in results:
            print(f"Рік {result['year']} - Області: {', '.join(result['regions'])} - VHI: {result['vhi_values']}")
    else:
        print("⚠ Не знайдено екстремальних посух за вказаний поріг.")
    
    return results

def main():
    df = None
    while True:
        print("\nMenu:")
        print("1 - Download data for a separate province")
        print("2 - Download data for all provinces")
        print("3 - Read and analyze VHI data")
        print("0 - Exit")
        
        try:
            choice = int(input("Enter number of operation: "))
            
            if choice == 0:
                print("Exiting...")
                break
            elif choice == 1:
                print_regions()
                province_id = int(input("Enter province number (1-27) or 0 to exit: "))
                if 1 <= province_id <= 27:
                    download_vhi_data(province_id)
                elif province_id == 0:
                    print("Exiting...")
                else:
                    print("Invalid input. Enter a number from 1 to 27.")
            elif choice == 2:
                download_all_regions_vhi()
            elif choice == 3:
                df = read_vhi_files()
                if df is not None:
                    while True:
                        print("\nVHI Data Analysis Menu:")
                        print("1 - Update region indices")
                        print("2 - Get VHI for a region and year")
                        print("3 - Get VHI extremes for regions and years")
                        print("4 - Get VHI for a range of years")
                        print("5 - Find extreme droughts")
                        print("0 - Return to main menu")
                        
                        sub_choice = int(input("Enter number of operation: "))
                        
                        if sub_choice == 0:
                            break
                        elif sub_choice == 1:
                            df = update_region_indices(df)
                        elif sub_choice == 2:
                            region_id = int(input("Enter region ID: "))
                            year = int(input("Enter year: "))
                            get_vhi_for_region_year(df, region_id, year)
                        elif sub_choice == 3:
                            region_ids = list(map(int, input("Enter region IDs separated by space: ").split()))
                            years = list(map(int, input("Enter years separated by space: ").split()))
                            get_vhi_extremes(df, region_ids, years)
                        elif sub_choice == 4:
                            region_ids = list(map(int, input("Enter region IDs separated by space: ").split()))
                            start_year = int(input("Enter start year: "))
                            end_year = int(input("Enter end year: "))
                            get_vhi_range(df, region_ids, start_year, end_year)
                        elif sub_choice == 5:
                            threshold = int(input("Enter threshold percentage (default 20): ") or 20)
                            find_extreme_droughts(df, threshold)
                        else:
                            print("Invalid choice. Enter a number between 0 and 5.")
            else:
                print("Invalid choice. Enter a number between 0 and 3.")
        except ValueError:
            print("Invalid input. Enter an integer.")

if __name__ == "__main__":
    main()
