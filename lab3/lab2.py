import urllib.request
import pandas as pd
from datetime import datetime
import os
import glob
import time 
import hashlib
import json

ascii_art = """
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣤⣾⡿⠿⢿⣦⡀⠀⠀⠀⠀⠀⠀
⠀⠀⢀⣶⣿⣶⣶⣶⣦⣤⣄⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣰⣿⠟⠁⣀⣤⡄⢹⣷⡀⠀⠀⠀⠀⠀
⠀⠀⢸⣿⡧⠤⠤⣌⣉⣩⣿⡿⠶⠶⠒⠛⠛⠻⠿⠶⣾⣿⣣⠔⠉⠀⠀⠙⡆⢻⣷⠀⠀⠀⠀⠀
⠀⠀⢸⣿⠀⠀⢠⣾⠟⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣾⣿⡃⠀⠀⠀⠀⠀⢻⠘⣿⡀⠀⠀⠀⠀
⠀⠀⠘⣿⡀⣴⠟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠛⠻⢶⣤⣀⠀⢘⠀⣿⡇⠀⠀⠀⠀
⠀⠀⠀⢿⣿⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉⠛⢿⣴⣿⠀⠀⠀⠀⠀
⠀⠀⠀⣸⡟⠀⠀⠀⣴⡆⠀⠀⠀⠀⠀⠀⠀⣷⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠻⣷⡀⠀⠀⠀⠀
⠀⠀⢰⣿⠁⠀⠀⣰⠿⣇⠀⠀⠀⠀⠀⠀⠀⢻⣷⡀⠀⢠⡄⠀⠀⠀⠀⠀⡀⠀⠹⣷⠀⠀⠀⠀
⠀⠀⣾⡏⠀⢀⣴⣿⣤⢿⡄⠀⠀⠀⠀⠀⠀⠸⣿⣷⡀⠘⣧⠀⠀⠀⠀⠀⣷⣄⠀⢻⣇⠀⠀⠀
⠀⠀⢻⣇⠀⢸⡇⠀⠀⠀⢻⣄⠀⠀⠀⠀⠀⣤⡯⠈⢻⣄⢻⡄⠀⠀⠀⠀⣿⡿⣷⡌⣿⡄⠀⠀
⠀⢀⣸⣿⠀⢸⡷⣶⣶⡄⠀⠙⠛⠛⠛⠛⠛⠃⣠⣶⣄⠙⠿⣧⠀⠀⠀⢠⣿⢹⣻⡇⠸⣿⡄⠀
⢰⣿⢟⣿⡴⠞⠀⠘⢿⡿⠀⠀⠀⠀⠀⠀⠀⠀⠈⠻⣿⡇⠀⣿⡀⢀⣴⠿⣿⣦⣿⠃⠀⢹⣷⠀
⠀⢿⣿⠁⠀⠀⠀⠀⠀⠀⠀⢠⣀⣀⡀⠀⡀⠀⠀⠀⠀⠀⠀⣿⠛⠛⠁⠀⣿⡟⠁⠀⠀⢀⣿⠂
⠀⢠⣿⢷⣤⣀⠀⠀⠀⠀⠀⠀⠉⠉⠉⠛⠉⠀⠀⠀⠀⠀⢠⡿⢰⡟⠻⠞⠛⣧⣠⣦⣀⣾⠏⠀
⠀⢸⣿⠀⠈⢹⡿⠛⢶⡶⢶⣤⣤⣤⣤⣤⣤⣤⣤⣶⠶⣿⠛⠷⢾⣧⣠⡿⢿⡟⠋⠛⠋⠁⠀⠀
⠀⣾⣧⣤⣶⣟⠁⠀⢸⣇⣸⠹⣧⣠⡾⠛⢷⣤⡾⣿⢰⡟⠀⠀⠀⣿⠋⠁⢈⣿⣄⠀⠀⠀⠀⠀
⠀⠀⠀⣼⡏⠻⢿⣶⣤⣿⣿⠀⠈⢉⣿⠀⢸⣏⠀⣿⠈⣷⣤⣤⣶⡿⠶⠾⠋⣉⣿⣦⣀⠀⠀⠀
⠀⠀⣼⡿⣇⠀⠀⠙⠻⢿⣿⠀⠀⢸⣇⠀⠀⣻⠀⣿⠀⣿⠟⠋⠁⠀⠀⢀⡾⠋⠉⠙⣿⡆⠀⠀
⠀⠀⢻⣧⠙⢷⣤⣦⠀⢸⣿⡄⠀⠀⠉⠳⣾⠏⠀⢹⣾⡇⠀⠀⠙⠛⠶⣾⡁⠀⠀⠀⣼⡇⠀⠀
⠀⠀⠀⠙⠛⠛⣻⡟⠀⣼⣿⣇⣀⣀⣀⡀⠀⠀⠀⣸⣿⣇⠀⠀⠀⠀⠀⠈⢛⣷⠶⠿⠋⠀⠀⠀
⠀⠀⠀⠀⠀⢠⣿⣅⣠⣿⠛⠋⠉⠉⠛⠻⠛⠛⠛⠛⠋⠻⣧⡀⣀⣠⢴⠾⠉⣿⣆⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⣼⡏⠉⣿⡟⠁⠀⠀⠀⢀⠀⠀⠀⠀⠀⠀⠀⠙⠿⣿⣌⠁⠀⠀⠈⣿⡆⠀⠀⠀⠀
⠀⠀⠀⠀⠀⣿⣇⣠⣿⣿⡶⠶⠶⣶⣿⣷⡶⣶⣶⣶⣶⡶⠶⠶⢿⣿⡗⣀⣤⣾⠟⠁⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠈⠙⠛⢻⣿⡇⠀⠀⣿⡟⠛⠷⠶⠾⢿⣧⠁⠀⠀⣸⡿⠿⠟⠉⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⢿⣷⣦⣤⡿⠀⠀⠀⠀⠀⠀⢿⣧⣤⣼⣿⠇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
"""



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
    print("\nregions of Ukraine")
    for i in range(1, 28, 2):  
        r1 = f"{i}. {REGIONS[i]:<18}"  
        r2 = f"{i+1}. {REGIONS[i+1]}" if i+1 in REGIONS else ""  
        print(f"{r1} {r2}")
    print()

def calculate_file_hash(filepath):
    
    hasher = hashlib.md5()
    with open(filepath, 'rb') as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()





def download_vhi_data(ua_id, directory="vhi_data"):
    if not os.path.exists(directory):
        os.makedirs(directory)

    noaa_id = list(NOAA_TO_UA.keys())[list(NOAA_TO_UA.values()).index(ua_id)]
    url = f"https://www.star.nesdis.noaa.gov/smcd/emb/vci/VH/get_TS_admin.php?country=UKR&provinceID={noaa_id}&year1=1981&year2=2024&type=Mean"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f'vhi_{REGIONS[ua_id]}_{timestamp}.csv'
    filepath = os.path.join(directory, filename)

    try:
        
        existing_files = glob.glob(os.path.join(directory, f'vhi_{REGIONS[ua_id]}_*.csv'))
        if existing_files:
        
            latest_file = max(existing_files, key=os.path.getctime)
            latest_hash = calculate_file_hash(latest_file)

           
            temp_filepath = os.path.join(directory, f'temp_{filename}')
            urllib.request.urlretrieve(url, temp_filepath)
            new_hash = calculate_file_hash(temp_filepath)

            if latest_hash == new_hash:
                print(f"data for  {REGIONS[ua_id]} (ID: {ua_id}, NOAA ID: {noaa_id}) alredy relevant,skip ")
                os.remove(temp_filepath)
                return None
            else:
                print(f"found new data {REGIONS[ua_id]},updating...")
                os.remove(latest_file) 
                os.rename(temp_filepath, filepath) 
                print(f"data for  {REGIONS[ua_id]} (ID: {ua_id}, NOAA ID: {noaa_id}) updated in {filepath}")
                return filepath
        else:
           
            urllib.request.urlretrieve(url, filepath)
            print(f"data for  {REGIONS[ua_id]} (ID: {ua_id}, NOAA ID: {noaa_id}) dawnloaded in  {filepath}")
            return filepath
    except Exception as e:
        print(f"rrror dawnloading data for  {REGIONS[ua_id]}: {e}")
        return None



def download_all_regions_vhi(directory="vhi_data", delay=2):
    print("starting to download data for all provincees...")
    downloaded_files = []
    
   
    for region_id in range(1, 28):
        try:
            
            time.sleep(delay)
            
            file_path = download_vhi_data(region_id, directory)
            if file_path:
                downloaded_files.append(file_path)
        except Exception as e:
            print(f"error downloading for the province  {region_id}: {e}")
    
    print(f"download completed.{len(downloaded_files)} files")
    return downloaded_files
    
    
   
def read_vhi_files(directory="vhi_data"):
    all_files = glob.glob(os.path.join(directory, "vhi_*.csv"))
    df_list = []
    
    if not all_files:
        print("no VHI data files found in the this dir")
        return pd.DataFrame()

    for filename in all_files:
        print(f"reading file: {filename}...")
        try:
            with open(filename, 'r') as file:
                lines = file.readlines()
            
            region_id = int(lines[0].split('Province=')[1].split(':')[0].strip())
           
            data_rows = []
            for line in lines[2:]:  
                clean_line = (line.replace('<tt><pre>', '')
                                .replace('</tt></pre>', '')
                                .strip())
                
                if clean_line and not clean_line.startswith('<'):
                    values = [v.strip() for v in clean_line.split(',') if v.strip()]
                    if len(values) >= 7:  
                        try:
                            row = {
                                'Year': int(values[0]),
                                'Week': int(values[1]),
                                'SMN': float(values[2]),
                                'SMT': float(values[3]),
                                'VCI': float(values[4]),
                                'TCI': float(values[5]),
                                'VHI': float(values[6]),
                                'Region': region_id
                            }
                            data_rows.append(row)
                        except (ValueError, IndexError) as e:
                            print(f"error parsing line: {clean_line}")
                            print(f"Error details: {e}")
                            continue
            
            if data_rows:
                df = pd.DataFrame(data_rows)
                df_list.append(df)
                print(f"sucessfully processed data for region {region_id}")
            
        except Exception as e:
            print(f"rrror reading file {filename}: {e}")

    if df_list:
        print(f"\nsuccessfully loaded {len(df_list)} VHI data files")
        final_df = pd.concat(df_list, ignore_index=True)
        
        
        original_length = len(final_df)
        final_df = final_df.drop(final_df.loc[final_df['VHI'] == -1].index)
        rows_dropped = original_length - len(final_df)
        print(f"\nremoved {rows_dropped} rows where VHI = -1 (nan)")
        
        final_df['Region_Name'] = final_df['Region'].map(NOAA_TO_UA).map(REGIONS)
        
        print("\ndf structure:")
        print("=" * 80)
        print("\ncolumns in the df:")
        print(final_df.columns.tolist())
        
        final_df = final_df.sort_values(['Year', 'Week', 'Region']).reset_index(drop=True)
        
        print("\nfirst few rows of the data:")
        print("=" * 80)
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', 1000)
        print(final_df.head().to_string())
        
        print("\nsample of data for each region :")
        print("=" * 80)
        sample_by_region = (final_df.sort_values(['Year', 'Week'])
                          .groupby('Region_Name')
                          .first()
                          .reset_index())
        print(sample_by_region[['Region_Name', 'Year', 'Week', 'VHI']].to_string())
        
        print("\ndata  validation:")
        print("=" * 80)
        print(f"total records: {len(final_df):,}")
        print(f"year range: {final_df['Year'].min()} - {final_df['Year'].max()}")
        print(f"week range: {final_df['Week'].min()} - {final_df['Week'].max()}")
        print(f"num of regions: {final_df['Region'].nunique()}")
        
        first_week = final_df.groupby('Region')['Week'].min()
        if (first_week != 1).any():
            print("\n some regions don't start with week 1:")
            for region, week in first_week[first_week != 1].items():
                print(f"region {REGIONS.get(region, region)}: starts from week {week}")
        
        return final_df
    else:
        print("no files were successfully processed")
        return pd.DataFrame()

def update_region_indices(df):
    
    if 'Region' not in df.columns:
        print(" 'Region' column not found in df")
        return df
    
    print("updating region indices...")
    df['Region'] = df['Region'].map(NOAA_TO_UA)
    df['Region_Name'] = df['Region'].map(REGIONS)
    print("region indices updated successfully")
    return df

def get_vhi_for_region_year(df, region_id, year):
    
    if 'Region' not in df.columns or 'Year' not in df.columns:
        print("required columns not found in the df")
        return pd.DataFrame()
    
    result = df[(df['Region'] == region_id) & (df['Year'] == year)][['Week', 'VHI']]
    if result.empty:
        print(f"no  data found for region {REGIONS.get(region_id, 'Unknown')} in year {year}")
    else:
        print(f"VHI data for region {REGIONS.get(region_id, 'Unknown')} in {year}:")
        print(result.to_string(index=False))
    return result

def get_vhi_extremes(df, region_ids, years):
   
    if 'Region' not in df.columns or 'Year' not in df.columns:
        print("required columns not found in  df")
        return None
    
    filtered_df = df[
        (df['Region'].isin(region_ids)) & 
        (df['Year'].isin(years))
    ]
    
    if filtered_df.empty:
        print(" no data found for those regions n years")
        return None
    
    stats = {
        'min_vhi': filtered_df['VHI'].min(),
        'max_vhi': filtered_df['VHI'].max(),
        'mean_vhi': filtered_df['VHI'].mean(),
        'median_vhi': filtered_df['VHI'].median()
    }
    
    print("\nVHI statistics:")
    print(f"regions: {', '.join([REGIONS.get(r, 'Unknown') for r in region_ids])}")
    print(f"years: {', '.join(map(str, years))}")
    print(f"minimum VHI: {stats['min_vhi']:.2f}")
    print(f"maximum VHI: {stats['max_vhi']:.2f}")
    print(f"mean VHI: {stats['mean_vhi']:.2f}")
    print(f"median VHI: {stats['median_vhi']:.2f}")
    
    return stats
    
def get_vhi_range(df, region_ids, start_year, end_year):
    
    result = df[(df['Region'].isin(region_ids)) & (df['Year'].between(start_year, end_year))][['Year', 'Week', 'Region', 'VHI']]
    print(f"range for regions {region_ids} from {start_year} to {end_year}:")
    print(result)
    return result    


def find_extreme_droughts(df, threshold_percent=20):
    
    results = []
    total_regions = 25
    threshold_regions = int(total_regions * threshold_percent / 100)
    
    print(f"searching extreme doughts that touched more than  {threshold_percent}% regions...")
    
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
        print(f"found {len(results)} years with extreme droughts")
        for result in results:
            print(f"year {result['year']} - regions: {', '.join(result['regions'])} - VHI: {result['vhi_values']}")
    else:
        print("didnt find extreme droughts for this period")
    
    return results


def main():
    print(ascii_art)
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
                    print("exiting...")
                else:
                    print("dumbass  enter a number from 1 to 27")
            elif choice == 2:
                download_all_regions_vhi()
            elif choice == 3:
                df = read_vhi_files()
                if df is not None:
                    while True:
                        print("\nVHI data analysis menu:")
                        print("1 - update region indices")
                        print("2 - get VHI for a region and year")
                        print("3 - get VHI extremes for regions and years")
                        print("4 - Get VHI for a range of years")
                        print("5 - find extreme droughts")
                        print("0 - return to main menu")
                        
                        sub_choice = int(input("enter num of operation: "))
                        
                        if sub_choice == 0:
                            break
                        elif sub_choice == 1:
                            df = update_region_indices(df)
                        elif sub_choice == 2:
                            region_id = int(input("enter region ID: "))
                            year = int(input("enter year: "))
                            get_vhi_for_region_year(df, region_id, year)
                        elif sub_choice == 3:
                            region_ids = list(map(int, input("Enter region IDs separated by space: ").split()))
                            years = list(map(int, input("Enter years separated by space: ").split()))
                            get_vhi_extremes(df, region_ids, years)
                        elif sub_choice == 4:
                            region_ids = list(map(int, input("enter region IDs separated by space: ").split()))
                            start_year = int(input("enter start year: "))
                            end_year = int(input("enter end year: "))
                            get_vhi_range(df, region_ids, start_year, end_year)
                        elif sub_choice == 5:
                            threshold = int(input("enter threshold percentage (default 20): ") or 20)
                            find_extreme_droughts(df, threshold)
                        else:
                            print("dumbass enter a number between 0 and 5")
            else:
                print("dumbass enter a number between 0 and 3")
        except ValueError:
            print("dumbass enter an integer")

if __name__ == "__main__":
    main()
