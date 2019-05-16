# import this module into your file using - from color_extractor import *
# call function as - colors, percentage = extract_colors(img)



import numpy as np
import cv2
from sklearn.cluster import DBSCAN

def detect_colors(img):
    
    data = cv2.resize(img, (28, 28), interpolation=cv2.INTER_LINEAR)
    data = data.reshape(data.shape[0]*data.shape[1], data.shape[2])
    data = data/255

    clustering = DBSCAN(eps=0.03, min_samples=4).fit(data)

    labels, counts = np.unique(clustering.labels_, return_counts=True)

    colors = []
    for i in labels:
        rgb = np.mean(data[clustering.labels_==i], axis=0)
        rgb = rgb*255
        rgb = rgb.astype(int)
        colors.append(rgb)

    percentage = np.around((counts/len(clustering.labels_))*100, decimals=2)
    
    colors  = colors[1:]
    percentage = percentage[1:]
    
    return colors, percentage

def process_colors(colors, percentage, dist=40):
    
    final_colors = []
    final_percentage = []
        
    for i in range(len(colors)):
        if type(colors[i]) != np.ndarray:
            continue
        temp_color = colors[i]
        temp_percentage = percentage[i]
        for j in range(i+1,len(colors)):
            if type(colors[j]) != np.ndarray:
                continue
            distance = np.sum(abs(colors[i]-colors[j]))
            if  distance<=dist:
                if(percentage[i]>percentage[j]):
                    temp_color = colors[i]                   
                else:
                    temp_color = colors[j]
                temp_percentage = round(percentage[i]+percentage[j], 2)
                colors[j] = None
                percentage[j] = None

        final_colors.append(temp_color)
        final_percentage.append(temp_percentage)  
                       
    return np.asarray(final_colors), np.asarray(final_percentage)

def extract_colors(img):
    
    # input : RGB image with channels_last 
    # output : numpy.ndarray of colors and percentage
    
    colors, percentage = detect_colors(img)
    final_colors, final_percentage = process_colors(colors, percentage)
    
    return final_colors, final_percentage
    
