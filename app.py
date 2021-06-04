import streamlit as st
import requests
import os
from google.cloud import storage
from PIL import Image
import pickle


st.set_option('deprecation.showfileUploaderEncoding', False)

st.title('SolarVision V1.0')

st.markdown('''
Please upload an image of a rooftop and we will classify if there are solar panels or not.
''')

def adjust_image(image):
    if image.size[0]==image.size[1]:
        if image.size[0]!=320:
            image=image.resize((320,320))
        else:
            image=image
    else:
        if image.size[0]>image.size[1]:        
            width = int(round(image.size[0]*(320/image.size[1])))
            image=image.resize((width,320))
            left = (image.size[0]-image.size[1])/2
            top = 0
            right = (image.size[0]-image.size[1])/2 +image.size[1]
            bottom = image.size[1]
            image = image.crop((left, top, right, bottom))
        
        else:
            image=image.rotate(90, expand=True)
            width = int(round(image.size[0]*(320/image.size[1])))
            image=image.resize((width,320))
            left = (image.size[0]-image.size[1])/2
            top = 0
            right = (image.size[0]-image.size[1])/2 +image.size[1]
            bottom = image.size[1]
            image = image.crop((left, top, right, bottom))
            image=image.rotate(270)
    
    return image 


uploaded_file = st.file_uploader(label='upload .jpg or .png file', 
                                 type=['jpg', 'png'])

if uploaded_file is not None: 

    st.image(uploaded_file, use_column_width='auto')
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

    # Button to click to start prediction
    if st.button('Make Prediction'):
        url = 'https://solarvision-10-iq5yzqlj2q-ew.a.run.app/predict' 
        params={'upload':os.path.join('data/predict_image', uploaded_file2.filename)}
        response = requests.get(url, params).json()
        if response['test'] == 1:
            st.write('This rooftop has solar panels.') 
        else:
            st.write('This rooftop does not have solar panels.')

else:
    st.write('Please upload a file.')
