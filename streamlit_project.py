import json 

import streamlit as st 
import pandas as pd 
import matplotlib.pyplot as plt
import numpy as np 

from mplsoccer import VerticalPitch, Pitch
from matplotlib.colors import LinearSegmentedColormap

# --- Streamlit Interface ---
st.title('FIFA World Cup 2022 - Shot Map & Heatmap')
st.subheader('Filter by team/player to see their shots and movement on the field!')

# --- Carregar Dados ---
df = pd.read_parquet('copa22_events.parquet')

df['location'] = df['location'].apply(lambda x: json.loads(x) if isinstance(x, str) else None)
df = df.dropna(subset=['location'])

# DataFrame apenas com chutes
shots_df = df[df['type'] == 'Shot'].reset_index(drop=True)

# --- Filtros ---
team = st.selectbox('Select a team', shots_df['team'].sort_values().unique(), index=None)

if team:
    player = st.selectbox('Select a player', shots_df[shots_df['team'] == team]['player'].sort_values().unique(), index=None)
else:
    player = None

# --- Filtrar Dados ---
def filter_data(df, team, player, event_type=None):
    """Filtra os dados pelo time, jogador e opcionalmente pelo tipo de evento."""
    if team:
        df = df[df['team'] == team]
    if player:
        df = df[df['player'] == player]
    if event_type:
        df = df[df['type'] == event_type]
    return df

filtered_shots = filter_data(shots_df, team, player, event_type="Shot")
filtered_events = filter_data(df, team, player)  # Todos os eventos do jogador

col1, col2 = st.columns(2)

# --- SHOTMAP ---
with col1:
    if not filtered_shots.empty:
        pitch = VerticalPitch(pitch_type='statsbomb', half=True, pitch_color='#15242e')
        fig, ax = pitch.draw(figsize=(10, 6))
        fig.set_facecolor('#15242e')

        for shot in filtered_shots.to_dict(orient='records'):
            pitch.scatter(
            x=shot['location'][0],
            y=shot['location'][1],
            ax=ax,
            s=1000 * shot['shot_statsbomb_xg'],
            color='green' if shot['shot_outcome'] == 'Goal' else 'white',
            edgecolors='black',
            alpha=1 if shot['shot_outcome'] == 'Goal' else 0.5,
            zorder=2 if shot['shot_outcome'] == 'Goal' else 1
        )

        ax.set_title(f"Shotmap de {player}", fontsize=25, color="white")
        st.pyplot(fig)
    else:
        st.write("⚠️ Esse jogador não tem finalizações registradas.")

# --- HEATMAP ---
with col2:
    if not filtered_events.empty:
        valid_locations = [loc for loc in filtered_events['location'] if isinstance(loc, list) and len(loc) == 2]

        if valid_locations:
            x, y = np.array(valid_locations).T

            pitch = Pitch(line_color='#cfcfcf', line_zorder=2, pitch_color='#15242e')
            fig, ax = pitch.draw(figsize=(10, 6))
            fig.set_facecolor('#15242e')

            # Criar colormap
            pearl_earring_cmap_100 = LinearSegmentedColormap.from_list("pearl_earring", ["#15242e", "#00aaff", "#ffffff"], N=100)

            # Criar heatmap
            pitch.kdeplot(x, y, ax=ax, cmap=pearl_earring_cmap_100, fill=True, levels=100)

            ax.set_title(f"Heatmap de {player}", fontsize=25, color="white")
            st.pyplot(fig)
        else:
            st.write("⚠️ Não há dados de movimentação para esse jogador.")
    else:
        st.write("⚠️ Selecione um jogador válido.")
