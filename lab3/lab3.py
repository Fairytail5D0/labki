import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
import glob
import time
from datetime import datetime
import urllib.request
import hashlib
import numpy as np

st.set_page_config(
    page_title="Ukraine VHI data analysis",
    page_icon="🗿",
    layout="wide",
    initial_sidebar_state="expanded"
)

REGIONS = {
    1: 'Вінницька', 2: 'Волинська', 3: 'Дніпропетровська', 4: 'Донецька', 5: 'Житомирська',
    6: 'Закарпатська', 7: 'Запорізька', 8: 'Івано-Франківська', 9: 'Київська', 10: 'Кіровоградська',
    11: 'Луганська', 12: 'Львівська', 13: 'Миколаївська', 14: 'Одеська', 15: 'Полтавська',
    16: 'Рівенська', 17: 'Сумська', 18: 'Тернопільська', 19: 'Харківська', 20: 'Херсонська',
    21: 'Хмельницька', 22: 'Черкаська', 23: 'Чернівецька', 24: 'Чернігівська', 25: 'Республіка Крим',
    26: 'Київ', 27: 'Севастополь',
}

NOAA_TO_UA = {
    1: 22, 2: 24, 3: 23, 4: 25, 5: 3, 6: 4, 7: 8, 8: 19,
    9: 20, 10: 21, 11: 9, 12: 26, 13: 10, 14: 11, 15: 12, 16: 13,
    17: 14, 18: 15, 19: 16, 20: 27, 21: 17, 22: 18, 23: 6, 24: 1,
    25: 2, 26: 7, 27: 5
}

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
                st.info(f"data for {REGIONS[ua_id]} (ID: {ua_id}, NOAA ID: {noaa_id}) alredy relevant,skip")
                os.remove(temp_filepath)
                return latest_file
            else:
                st.success(f"found new data for {REGIONS[ua_id]}, updating...")
                os.remove(latest_file) 
                os.rename(temp_filepath, filepath) 
                st.success(f"data for {REGIONS[ua_id]} (ID: {ua_id}, NOAA ID: {noaa_id}) updated in {filepath}")
                return filepath
        else:
            urllib.request.urlretrieve(url, filepath)
            st.success(f"data for {REGIONS[ua_id]} (ID: {ua_id}, NOAA ID: {noaa_id}) dawnloaded in {filepath}")
            return filepath
    except Exception as e:
        st.error(f"error dawnloading data for  {REGIONS[ua_id]}: {e}")
        return None

@st.cache_data
def read_vhi_files(directory="vhi_data"):
    all_files = glob.glob(os.path.join(directory, "vhi_*.csv"))
    df_list = []
    
    if not all_files:
        st.warning("didnt find data files VHI for this dir")
        return pd.DataFrame()

    for filename in all_files:
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
                            continue
            
            if data_rows:
                df = pd.DataFrame(data_rows)
                df_list.append(df)
            
        except Exception as e:
            st.error(f"error reading file {filename}: {e}")

    if df_list:
        final_df = pd.concat(df_list, ignore_index=True)
        
        original_length = len(final_df)
        final_df = final_df.drop(final_df.loc[final_df['VHI'] == -1].index)
        
        final_df['Region_ID'] = final_df['Region'].map(NOAA_TO_UA)
        final_df['Region_Name'] = final_df['Region_ID'].map(REGIONS)
        
        final_df = final_df.sort_values(['Year', 'Week', 'Region_ID']).reset_index(drop=True)
        
        return final_df
    else:
        st.warning("no files were successfully processed")
        return pd.DataFrame()

def download_all_regions_vhi(directory="vhi_data", delay=1):
    with st.spinner("dawnloading data for all regions..."):
        downloaded_files = []
        progress_bar = st.progress(0)
        
        total_regions = len(REGIONS)
        for i, region_id in enumerate(range(1, 28)):
            try:
                time.sleep(delay)
                file_path = download_vhi_data(region_id, directory)
                if file_path:
                    downloaded_files.append(file_path)
                progress_bar.progress((i + 1) / total_regions)
            except Exception as e:
                st.error(f"error dawnloading for region {region_id}: {e}")
        
        st.success(f"dawnloading ended. {len(downloaded_files)} files")
        progress_bar.empty()
    return downloaded_files

def init_session_state():
    if 'data_loaded' not in st.session_state:
        st.session_state.data_loaded = False
    
    if 'selected_index' not in st.session_state:
        st.session_state.selected_index = 'VHI'
    
    if 'selected_region' not in st.session_state:
        st.session_state.selected_region = 'Київська'
    
    if 'week_range' not in st.session_state:
        st.session_state.week_range = (1, 52)
    
    if 'year_range' not in st.session_state:
        st.session_state.year_range = (1981, 2023)
    
    if 'ascending_sort' not in st.session_state:
        st.session_state.ascending_sort = False
    
    if 'descending_sort' not in st.session_state:
        st.session_state.descending_sort = False

def reset_filters():
    st.session_state.selected_index = 'VHI'
    st.session_state.selected_region = 'Київська'
    st.session_state.week_range = (1, 52)
    
    df = read_vhi_files()
    if not df.empty:
        min_year = df['Year'].min()
        max_year = df['Year'].max()
        st.session_state.year_range = (min_year, max_year)
    else:
        st.session_state.year_range = (1981, 2023)
    
    st.session_state.ascending_sort = False
    st.session_state.descending_sort = False

def main():
    st.title("analysis of vegetation data in Ukraine")
    
    init_session_state()
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.subheader("args")
        
        if st.button("download data for all regions"):
            download_all_regions_vhi()
            st.session_state.data_loaded = True
        
        if not os.path.exists("vhi_data") or len(glob.glob(os.path.join("vhi_data", "vhi_*.csv"))) == 0:
            st.warning("first upload data for analysis")
            return
        
        df = read_vhi_files()
        if df.empty:
            st.warning("data isnt loaded or empty")
            return
        
        st.session_state.data_loaded = True
        
        st.session_state.selected_index = st.selectbox(
            "chose index for analys",
            options=['VCI', 'TCI', 'VHI'],
            index=['VCI', 'TCI', 'VHI'].index(st.session_state.selected_index)
        )
        
        st.session_state.selected_region = st.selectbox(
            "chose region",
            options=sorted(df['Region_Name'].unique()),
            index=list(sorted(df['Region_Name'].unique())).index(st.session_state.selected_region) 
                if st.session_state.selected_region in df['Region_Name'].unique() else 0
        )
 
        min_year = df['Year'].min()
        max_year = df['Year'].max()
        
        if st.session_state.year_range[0] < min_year:
            st.session_state.year_range = (min_year, st.session_state.year_range[1])
        if st.session_state.year_range[1] > max_year:
            st.session_state.year_range = (st.session_state.year_range[0], max_year)
        
        st.session_state.week_range = st.slider(
            "interval of weeks",
            min_value=1,
            max_value=52,
            value=st.session_state.week_range
        )
        
        st.session_state.year_range = st.slider(
            "interval of years",
            min_value=min_year,
            max_value=max_year,
            value=st.session_state.year_range
        )
        
        col1_sort, col2_sort = st.columns(2)
        
        with col1_sort:
            ascending = st.checkbox(
                "sort by ascending order",
                value=st.session_state.ascending_sort
            )
            if ascending and not st.session_state.ascending_sort:
                st.session_state.ascending_sort = True
                st.session_state.descending_sort = False
            elif not ascending:
                st.session_state.ascending_sort = False
        
        with col2_sort:
            descending = st.checkbox(
                "sort in descending order",
                value=st.session_state.descending_sort
            )
            if descending and not st.session_state.descending_sort:
                st.session_state.descending_sort = True
                st.session_state.ascending_sort = False
            elif not descending:
                st.session_state.descending_sort = False
        
        if st.button("reset filters"):
            reset_filters()
            st.rerun()  
    
    with col2:
        if st.session_state.data_loaded:
            filtered_df = df[
                (df['Region_Name'] == st.session_state.selected_region) &
                (df['Week'] >= st.session_state.week_range[0]) &
                (df['Week'] <= st.session_state.week_range[1]) &
                (df['Year'] >= st.session_state.year_range[0]) &
                (df['Year'] <= st.session_state.year_range[1])
            ]
            
            selected_index = st.session_state.selected_index
            if st.session_state.ascending_sort:
                filtered_df = filtered_df.sort_values(by=selected_index)
            elif st.session_state.descending_sort:
                filtered_df = filtered_df.sort_values(by=selected_index, ascending=False)
            
            tab1, tab2, tab3 = st.tabs(["table", "time series graph", "comparison of areas"])
            
            with tab1:
                st.subheader(f"data {selected_index} for {st.session_state.selected_region}")
                
                display_columns = ['Year', 'Week', selected_index]
                st.dataframe(filtered_df[display_columns], use_container_width=True)
                
                st.subheader("statistic")
                stats_df = pd.DataFrame({
                    'mean': [filtered_df[selected_index].mean()],
                    'min': [filtered_df[selected_index].min()],
                    'max': [filtered_df[selected_index].max()],
                    'median': [filtered_df[selected_index].median()],
                    'standard deviation': [filtered_df[selected_index].std()]
                })
                st.dataframe(stats_df.round(2), use_container_width=True)
            
            with tab2:
                st.subheader(f"graph {selected_index} for {st.session_state.selected_region}")
                
                if not filtered_df.empty:
                    fig, ax = plt.subplots(figsize=(10, 6))
                    
                    pivot_df = filtered_df.pivot_table(
                        index='Week',
                        columns='Year',
                        values=selected_index,
                        aggfunc='mean'
                    )
                    
                    for year in pivot_df.columns:
                        if year >= st.session_state.year_range[0] and year <= st.session_state.year_range[1]:
                            ax.plot(pivot_df.index, pivot_df[year], label=str(year))
                    
                    ax.set_xlabel('week of year')
                    ax.set_ylabel(selected_index)
                    ax.set_title(f'{selected_index} for {st.session_state.selected_region} in {st.session_state.year_range[0]}-{st.session_state.year_range[1]} роки')
                    ax.legend(title='Рік', bbox_to_anchor=(1.05, 1), loc='upper left')
                    ax.grid(True, linestyle='--', alpha=0.7)
                    
                    ax.set_xlim(st.session_state.week_range[0], st.session_state.week_range[1])
                    
                    plt.tight_layout()
                    st.pyplot(fig)
                else:
                    st.warning("no data to display with current filters")
            
            with tab3:
                st.subheader(f"comparison {selected_index} betwem regions")
                
                comparison_df = df[
                    (df['Week'] >= st.session_state.week_range[0]) &
                    (df['Week'] <= st.session_state.week_range[1]) &
                    (df['Year'] >= st.session_state.year_range[0]) &
                    (df['Year'] <= st.session_state.year_range[1])
                ]
                
                if not comparison_df.empty:
                    region_means = comparison_df.groupby('Region_Name')[selected_index].mean().reset_index()
                    region_means = region_means.sort_values(by=selected_index, ascending=False)
                    
                    colors = ['#1f77b4'] * len(region_means)
                    selected_idx = region_means[region_means['Region_Name'] == st.session_state.selected_region].index
                    if not selected_idx.empty:
                        for idx in selected_idx:
                            colors[idx] = '#ff7f0e'
                    
                    fig, ax = plt.subplots(figsize=(12, 8))
                    ax.bar(region_means['Region_Name'], region_means[selected_index], color=colors)
                    ax.set_xlabel('region')
                    ax.set_ylabel(f'average value {selected_index}')
                    ax.set_title(f'comparison  by average values {selected_index} betwen regions')
                    ax.set_xticklabels(region_means['Region_Name'], rotation=45, ha='right')
                    
                    from matplotlib.patches import Patch
                    legend_elements = [
                        Patch(facecolor='#1f77b4', label='other regions'),
                        Patch(facecolor='#ff7f0e', label=f'selected region: {st.session_state.selected_region}')
                    ]
                    ax.legend(handles=legend_elements, loc='upper right')
                    
                    plt.tight_layout()
                    st.pyplot(fig)
                    
                    st.subheader("table of comparisonregions")
                    st.dataframe(region_means, use_container_width=True)
                else:
                    st.warning("no data to compare with current filters")

if __name__ == "__main__":
    main()
