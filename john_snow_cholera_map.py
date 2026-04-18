#developed by Fouad Zablith

import streamlit as st
import pandas as pd
import pydeck as pdk
import altair as alt
from PIL import Image

#load the data from excel in a dateframe
#a similar (with cleaner ) dataset is accessible online at https://docs.google.com/file/d/0B1k6zmQ4NXQlZ0dBcjFrNWhUSTA/edit
data = pd.read_excel(r'CholeraPumps_Deaths.xls')
df = pd.DataFrame(data, columns=['count','geometry'])

#clean and replace the coordinates data to fit the PyDeck map 
df = df.replace({'<Point><coordinates>': ''},regex=True )
df = df.replace({'</coordinates></Point>': ''},regex=True )

#create new longitude and latitude columns in dataframe
split = df['geometry'].str.split(',',n=1, expand=True)
df['lon'] = split[0].astype(float)
df['lat'] = split[1].astype(float)

df.drop(columns=['geometry'], inplace = True)

#st.write(df)

st.header('John Snow\'s 1854 Cholera Deaths Map in London')
st.subheader('This is a recreation of Snow\'s famous map that helped identifying the source of cholera oubreak in London')

#create a slider to filter the number of deaths
death_to_filter = st.slider('Number of Deaths', 0, 15, 2)  # min: 0 death, max: 15 deaths, default: 7 deaths
filtered_df = df[df['count'] >= death_to_filter]
st.subheader(f'Map of more than {death_to_filter} deaths')

#function to assign color based on count severity
def get_color(count):
    if count <= 3:
        return [255, 255, 0, 160]  # yellow
    elif count <= 7:
        return [255, 140, 0, 160]  # orange
    else:
        return [200, 30, 0, 160]  # red

#assign colors to filtered_df based on count
filtered_df = filtered_df.copy()
filtered_df['color'] = filtered_df['count'].apply(lambda x: get_color(x))
filtered_df['tooltip'] = filtered_df['count'].apply(lambda x: f"Deaths: {x}")

#get the pumps location from the last 8 entries in the data (in the original data source, pumps were noted as having -999 death as a differentiator)
pumps_df = df[df['count'] == -999].copy()
pumps_df['tooltip'] = "Water Pump"

#checkbox to enable seeing the location of pumps
if(st.checkbox('Show pumps',value=True)):
    pump_radius = 10.5
else:
    pump_radius = 0

#checkbox to enable seeing the heatmap
show_heatmap = st.checkbox('Show Heatmap', value=True)

#checkbox to enable 3D view
view_3d = st.checkbox('3D View', value=False)

#sidebar statistics
st.sidebar.title('Statistics')
st.sidebar.metric('Death Locations Shown', len(filtered_df))
st.sidebar.metric('Total Deaths Shown', int(filtered_df['count'].sum()))
st.sidebar.metric('Highest Death Count', int(filtered_df['count'].max()))
st.sidebar.metric('Number of Pumps', len(pumps_df))

st.pydeck_chart(pdk.Deck(
    map_style='mapbox://styles/mapbox/light-v9',
    initial_view_state=pdk.ViewState(
        latitude=51.5134,
        longitude=-0.1365,
        zoom=15.5,
        pitch=45 if view_3d else 0,
    ),
    layers=([pdk.Layer(
            'HeatmapLayer',
            data=filtered_df,
            get_position='[lon, lat]',
            get_weight='count',
        )] if show_heatmap else []) + ([pdk.Layer(
            'ColumnLayer',
            data=filtered_df,
            get_position='[lon, lat]',
            get_elevation='count * 2',
            get_fill_color='color',
            elevation_scale=5,
            radius=7,
        ), pdk.Layer(
            'ColumnLayer',
            data=pumps_df,
            get_position='[lon, lat]',
            get_elevation=3,
            get_fill_color='[0, 100, 255, 255]',
            elevation_scale=5,
            radius=5,
        )] if view_3d else [pdk.Layer(
            'ScatterplotLayer',
            data=filtered_df,
            get_position='[lon, lat]',
            get_color='color',
            get_radius='[count]',
        )]) + [
        pdk.Layer(
            'ScatterplotLayer',
            data=pumps_df,
            get_position='[lon, lat]',
            get_color='[0, 100, 255, 255]',
            get_radius=pump_radius,
        ),
    ],
))

st.markdown('**Red dots show death count and Blue dots show water pumps**')

st.markdown('**Legends:**')
st.markdown('- 🟡 1-3 deaths')
st.markdown('- 🟠 4-7 deaths')
st.markdown('- 🔴 8+ deaths')


st.write('')
st.write('')
st.write('')

st.subheader('Death Count Distribution')
distribution = df[df['count'] > 0]['count'].value_counts().sort_index()
dist_df = pd.DataFrame({'Death Count': distribution.index, 'Number of Locations': distribution.values})

bar_chart = alt.Chart(dist_df).mark_bar().encode(
    x=alt.X('Death Count:O', axis=alt.Axis(title='Death Count', grid=False)),
    y=alt.Y('Number of Locations:Q', axis=alt.Axis(title='Number of Locations', grid=False)),
    tooltip=['Death Count', 'Number of Locations']
).properties(height=350)

st.altair_chart(bar_chart, use_container_width=True)
st.caption('Each bar represents how many locations recorded that number of deaths (full dataset, independent of slider)')

with st.expander('📖 About John Snow & the 1854 Cholera Outbreak'):
    st.markdown("### Who was John Snow?\nJohn Snow was a British physician who is widely considered one of the founders of epidemiology, the field that studies how diseases spread through populations.")
    st.divider()
    st.markdown("### The 1854 Outbreak\nIn 1854, a devastating cholera outbreak struck the Soho district of London and killed over 600 people in just a few weeks.")
    st.divider()
    st.markdown("### The Investigation\nSnow carefully mapped the locations of cholera deaths and traced the outbreak's source to the Broad Street water pump, showing a clear pattern in the data.")
    st.divider()
    st.markdown("### The Impact\nHis work helped challenge the miasma theory of disease and laid important groundwork for the acceptance of germ theory and modern public health practices.")
    st.divider()
    st.markdown("### Why This Map Matters\nThis map is considered one of the earliest and most influential examples of data visualization being used to solve a real public health crisis.")

image = Image.open('Snow-cholera-map-1.jpg')

st.subheader('Original map of John Snow')
st.image(image,caption='Original map by John Snow showing the clusters of cholera cases in the London epidemic of 1854, drawn and lithographed by Charles Cheffins',use_column_width='always')

st.markdown('The source of the above map and more details on John Snow\'s work can be found here: [https://en.wikipedia.org/wiki/John_Snow](https://en.wikipedia.org/wiki/John_Snow)')

st.markdown("Developed by [Fouad Zablith](http://fouad.zablith.org). If you have any question about this simple app, you can reach me through: [@fzablith](https://twitter.com/fzablith)")