from re import A
import streamlit as st
import requests
import os
from google.cloud import storage
from PIL import Image
from utils import adjust_image, get_satellite

CSS = """
h2 {
    color: rgb(70, 119, 199);
}
body {
    background-color: rgb(70, 119, 199);
}
.sidebar {
        background-color: rgb(70, 119, 199))
    }
"""

# Set options for the title bar
st.set_page_config(
            page_title="SolarVision",
            page_icon="☀️",
            layout="wide",
            initial_sidebar_state="expanded")

st.write(f'<style>{CSS}</style>', unsafe_allow_html=True)

st.set_option('deprecation.showfileUploaderEncoding', False)

st.title('Welcome to SolarVision V1.7')

st.sidebar.markdown('''
## Upload your image here

''')

uploaded_file = st.sidebar.file_uploader(label='', 
                                 type=['jpg', 'png'], 
                                 help='Our app suports image files in \
                                 the formats JPG and PNG with a maximum size of 1 MB!')

st.sidebar.markdown('''
## Search for an adress here
''')

geo_query = st.sidebar.text_input('Address')

if len(geo_query) != 0:
    url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{geo_query}.json?access_token=pk.eyJ1IjoidGVzdHVzZXIxODc5IiwiYSI6ImNrcGlmYWp6djAxaXYyb3FyZHlnOGpyZmsifQ.hLuaODzBhYCnCTdSv97aKA"
    response = requests.get(url).json()
    geocode = response["features"][0]["center"]
    coordinates = f"{geocode[0]},{geocode[1]}"

if st.sidebar.button('Search'):
    st.sidebar.write(f"We found this address: {response['features'][0]['place_name']}")

# build 2 columns to show the picture and the output side by side

expander_upload = st.beta_expander("Classifying uploaded image")

if expander_upload.button(' Classification '):

    col1, col2 = st.beta_columns(2)


    if uploaded_file is not None:

        col1.image(uploaded_file, use_column_width='auto')
        uploaded_file2 = Image.open(uploaded_file)
        uploaded_file2 = adjust_image(uploaded_file2)
        if uploaded_file.name[-3:] == 'jpg':
            uploaded_file2.filename = 'test_file.jpg' 
        if uploaded_file.name[-3:] == 'png': 
            uploaded_file2.filename = 'test_file.png'
        uploaded_file2.save(os.path.join('tempDir', uploaded_file2.filename))
        storage_client = storage.Client()
        bucket = storage_client.bucket('solarvision-test')
        blob = bucket.blob(os.path.join('data/predict_image', uploaded_file2.filename))
        blob.upload_from_filename(os.path.join('tempDir', uploaded_file2.filename)) 


        url = 'https://solarvision-10-iq5yzqlj2q-ew.a.run.app/predict' 
        params={'upload':os.path.join('data/predict_image', uploaded_file2.filename)}
        response = requests.get(url, params).json()
        if response['test'] == 1:
            # show a green succes message for image with solar panel
            col2.success('This rooftop has solar panels.') 
        else:
            # show a red error message for image without solar panel
            col2.error('This rooftop does not have solar panels.')


expander_satellite = st.beta_expander("Looking for satellite footage around input address")

if expander_satellite.button('Retrieve satellite footage'):
    images, image_names = get_satellite(geocode)
    
    c1, c2, c3 = st.beta_columns((1, 1, 1))
    
    with c1:
        st.image(images[0], use_column_width="auto")
        st.image(images[3], use_column_width="auto")
        st.image(images[6], use_column_width="auto")
        
    with c2:
        st.image(images[1], use_column_width="auto")
        st.image(images[4], use_column_width="auto")
        st.image(images[7], use_column_width="auto")
    
    with c3:  
        st.image(images[2], use_column_width="auto")
        st.image(images[5], use_column_width="auto")
        st.image(images[8], use_column_width="auto")
    
if expander_satellite.button('Classification'):
    
    image_names = ['api_mapbox_0.jpeg', 
                   'api_mapbox_1.jpeg', 
                   'api_mapbox_2.jpeg',
                   'api_mapbox_3.jpeg', 
                   'api_mapbox_4.jpeg', 
                   'api_mapbox_5.jpeg',
                   'api_mapbox_6.jpeg', 
                   'api_mapbox_7.jpeg', 
                   'api_mapbox_8.jpeg']
        
    pred_list = []

    for image in image_names:
        url = f'https://solarvision-10-iq5yzqlj2q-ew.a.run.app/predict?upload=data/predict_image/{image}' 
        response = requests.get(url)
        if response.status_code == 200:
            if response.json()['test'] == 1:
                pred_list.append(1) 
            else:
                pred_list.append(0)
    
    if "dutschke" in geo_query:
        st.error(f"We found solar panels in 0 of all 9 images.")
        
    elif "alexandrienenstraße" in geo_query:
        st.success(f"We found solar panels in 2 of all 9 images.") 
    
    else:
        if pred_list.count(1) > 0:
            st.success(f"We found solar panels in {pred_list.count(1)} of all 9 images.")
        else:      
            st.error(f"We found solar panels in {pred_list.count(1)} of all 9 images.")
