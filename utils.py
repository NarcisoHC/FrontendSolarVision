import requests
import os
from PIL import Image
from google.cloud import storage


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


def get_satellite(geocode):  
    one_unit_lat = 47/111111
    one_unit_long = 31/111111
        
    coordinates_list = [f"{geocode[0]-one_unit_lat},{geocode[1]+one_unit_long}",
                        f"{geocode[0]},{geocode[1]+one_unit_long}",
                        f"{geocode[0]+one_unit_lat},{geocode[1]+one_unit_long}",
                        f"{geocode[0]-one_unit_lat},{geocode[1]}",
                        f"{geocode[0]},{geocode[1]}",
                        f"{geocode[0]+one_unit_lat},{geocode[1]}",
                        f"{geocode[0]-one_unit_lat},{geocode[1]-one_unit_long}",
                        f"{geocode[0]},{geocode[1]-one_unit_long}",
                        f"{geocode[0]+one_unit_lat},{geocode[1]-one_unit_long}"]
    
    image_names = []
    images = []
    for index, coordinates in enumerate(coordinates_list):
        
        api_request = f"https://api.mapbox.com/styles/v1/mapbox/satellite-v9/static/{coordinates},19/320x320?access_token=pk.eyJ1IjoidGVzdHVzZXIxODc5IiwiYSI6ImNrcGlmYWp6djAxaXYyb3FyZHlnOGpyZmsifQ.hLuaODzBhYCnCTdSv97aKA"
        
        image = Image.open(requests.get(api_request, stream=True).raw)
        image.filename = f'api_mapbox_{index}.jpeg'
        image.save(os.path.join('tempDir', image.filename))
        storage_client = storage.Client()
        bucket = storage_client.bucket('solarvision-test')
        blob = bucket.blob(os.path.join('data/predict_image', image.filename))
        blob.upload_from_filename(os.path.join('tempDir', image.filename))
        
        image_names.append(image.filename)
        images.append(image)
    
    return images, image_names