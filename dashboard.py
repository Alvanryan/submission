import streamlit as st
import pandas as pd
import os
import seaborn as sns
import matplotlib.pyplot as plt

st.title("Analyze Air Quality Data")
st.write("Tugas Analisis")

folder_path = "./Data"
files = [file for file in os.listdir(folder_path) if file.endswith('.csv')]
combined_data = pd.concat([
    pd.read_csv(os.path.join(folder_path, file)).assign(station=file.split('.')[0]) for file in files
], ignore_index=True)

cd = combined_data.dropna()
cd.drop(['month', 'day', 'hour', 'wd'], axis=1, inplace=True)

stations = cd['station'].unique()
selected_station = st.sidebar.selectbox("Select a station to analyze:", options=stations)
station_data = cd[cd['station'] == selected_station]

st.header("Pertanyaan 1: Bagaimana variasi kualitas udara antar stasiun?")

st.header(f"KDE Plot for {selected_station}")
fig, ax = plt.subplots(figsize=(8, 6))
sns.kdeplot(station_data['PM2.5'], label='PM2.5', color='blue', fill=True, ax=ax)
sns.kdeplot(station_data['PM10'], label='PM10', color='orange', fill=True, ax=ax)
ax.set_title(f'Comparison of PM2.5 and PM10 Levels - {selected_station}')
ax.set_xlabel('Concentration')
ax.set_ylabel('Density')
ax.legend()
st.pyplot(fig)

st.header("Average Pollution Index per Station (2013-2017)")
cd['Pollution_Index'] = cd[['PM2.5', 'PM10', 'SO2', 'NO2', 'CO', 'O3']].sum(axis=1)
weights = {
    'PM2.5': 0.3,
    'PM10': 0.2,
    'SO2': 0.1,
    'NO2': 0.1,
    'CO': 0.1,
    'O3': 0.1,
}

cd['Pollution_Index'] = (
    cd['PM2.5'] * weights['PM2.5'] +
    cd['PM10'] * weights['PM10'] +
    cd['SO2'] * weights['SO2'] +
    cd['NO2'] * weights['NO2'] +
    cd['CO'] * weights['CO'] +
    cd['O3'] * weights['O3']
)

yearly_pollution_avg = cd.groupby(['year', 'station'])['Pollution_Index'].mean().reset_index()

show_all_stations = st.checkbox("Show all stations", value=True)
if show_all_stations:
    fig, ax = plt.subplots(figsize=(14, 7))
    sns.lineplot(
        data=yearly_pollution_avg, 
        x='year', 
        y='Pollution_Index', 
        hue='station', 
        markers=True, 
        dashes=False, 
        ax=ax
    )
    ax.set_title('Average Pollution Index per Station (2013-2017)', fontsize=18)
    ax.set_xlabel('Year', fontsize=14)
    ax.set_ylabel('Average Pollution Index', fontsize=14)
    ax.legend(title='Station', bbox_to_anchor=(1.05, 1), loc='upper left')
    st.pyplot(fig)
else:
    selected_station_line = st.selectbox("Select a station for line chart:", options=stations)
    filtered_data = yearly_pollution_avg[yearly_pollution_avg['station'] == selected_station_line]
    
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.lineplot(
        data=filtered_data, 
        x='year', 
        y='Pollution_Index', 
        marker='o', 
        color='blue', 
        ax=ax
    )
    ax.set_title(f'Average Pollution Index - {selected_station_line}', fontsize=18)
    ax.set_xlabel('Year', fontsize=14)
    ax.set_ylabel('Average Pollution Index', fontsize=14)
    st.pyplot(fig)

st.header("Pertanyaan 2: Bagaimana korelasi antara parameter meteorologi dengan parameter kualitas udara pada stasiun?")

pollution_params = ['PM10', 'PM2.5', 'CO', 'SO2', 'NO2', 'O3']
meteorology_params = ['TEMP', 'PRES', 'DEWP', 'RAIN']

selected_meteorology = st.sidebar.selectbox(
    "Select a meteorological parameter:", options=meteorology_params
)
selected_pollution = st.sidebar.selectbox(
    "Select a pollution parameter:", options=pollution_params
)

fig, ax = plt.subplots(figsize=(8, 6))
sns.scatterplot(
    data=station_data,
    x=selected_meteorology,
    y=selected_pollution,
    alpha=0.7,
    hue=selected_meteorology,
    palette="coolwarm",
    size=selected_pollution,
    sizes=(20, 200),
    ax=ax
)
ax.set_title(f"{selected_meteorology} vs {selected_pollution} - {selected_station}", fontsize=16)
ax.set_xlabel(selected_meteorology, fontsize=12)
ax.set_ylabel(selected_pollution, fontsize=12)
ax.grid(alpha=0.3)
ax.legend(title="Legend", bbox_to_anchor=(1.05, 1), loc='upper left')
st.pyplot(fig)

correlation_data = station_data[meteorology_params + pollution_params]
correlation_matrix = correlation_data[meteorology_params].corrwith(correlation_data[pollution_params])
correlation_matrix = correlation_data.corr().loc[pollution_params, meteorology_params, ]

fig, ax = plt.subplots(figsize=(10, 8))
sns.heatmap(
    correlation_matrix, 
    annot=True, 
    fmt=".2f", 
    cmap="coolwarm", 
    cbar=True, 
    ax=ax
)
ax.set_title("Korelasi antara parameter Meteorologi dengan Polusi", fontsize=16)
st.pyplot(fig)