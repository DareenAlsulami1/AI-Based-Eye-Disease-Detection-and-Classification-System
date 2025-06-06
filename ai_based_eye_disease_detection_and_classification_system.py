# -*- coding: utf-8 -*-
"""AI-Based Eye Disease Detection and Classification System.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1HwSIhcEdx7HnK0NnN-KGTPh6eP194rcV

# Install requiraments
"""

!pip install ultralytics

!pip install gradio

!git clone https://github.com/domingomery/balu3
!pip install ./balu3
!pip install opencv-contrib-python

!pip install gdown

# Replace with your actual Google Drive links
yolo_model_url = "https://drive.google.com/uc?id=1fvQIxLIss9VgnT60Cdl-vcTfNKDvUcn5"
svm_model_url = "https://drive.google.com/uc?id=1LLhUldbubPJOgm_2t6TDj1fLVKd4j9o7"
knn_model_url = "https://drive.google.com/uc?id=1J2kLvu4AlIOWwsu5KC1sHCEGgAt-Nr0I"
ann_model_url = "https://drive.google.com/uc?id=1BPk7p5Q36vuQRLHwLcjW9tW2TbfukbyS"
cnn1_model_url = "https://drive.google.com/uc?id=1RD1dn-59zF0VawbaN7eWSzLZIXYDRAvX"
cnn2_model_url = "https://drive.google.com/uc?id=1cZ8mgEdKqwxnHFBbv8-hHw3MhIa2CXcJ"
#yolo_seg_url =  "https://drive.google.com/uc?id=1-cCmSVRSNn2LO2N6hGBpO7vlAnC8tlCt"

# Download the models from Google Drive
import gdown

# Download YOLOv8 model
gdown.download(yolo_model_url, '/content/yolov8.pt', quiet=False)

# Download SVM model
gdown.download(svm_model_url, '/content/hog_svm_model.pkl', quiet=False)

# Download KNN model
gdown.download(knn_model_url, '/content/hog_knn_model.pkl', quiet=False)

# Download ANN model
gdown.download(ann_model_url, '/content/hog_ann_model.pkl', quiet=False)

# Download CNN no droput model
gdown.download(cnn1_model_url, '/content/cnn_without_dropout_model.h5', quiet=False)

# Download CNN with dropout model
gdown.download(cnn2_model_url, '/content/cnn_with_dropout_model.h5', quiet=False)

# Download YOLOv8-seg model
#gdown.download(yolo_seg_url, '/content/yolov8seg.pt', quiet=False)

"""# Program"""

from ultralytics import YOLO
import gradio as gr
import cv2
from tensorflow.keras.models import load_model
import numpy as np
from tensorflow.keras.models import load_model
from balu3.fx.chr import hog
from skimage.feature import local_binary_pattern
from   balu3.fx.chr      import hog,lbp
import tensorflow as tf
from skimage import color
import joblib
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import load_img, img_to_array
import torch

# Load the models
yolo_model = YOLO("/content/yolov8.pt")
svm_model = joblib.load('/content/hog_svm_model.pkl')
knn_model = joblib.load('/content/hog_knn_model.pkl')
ann_model = joblib.load('/content/hog_ann_model.pkl')
cnn_nodropout_model = load_model('/content/cnn_without_dropout_model.h5')
cnn_dropout_model = load_model('/content/cnn_with_dropout_model.h5')
yolo_seg_model=YOLO("/content/yolo_seg.pt")
#yolo_seg_model = torch.load('/content/yoloseg1 (1).pt', map_location=torch.device('cpu'))

def predict(image_path,model):
    img = cv2.imread(image_path)

    # Convert to RGB (OpenCV reads in BGR)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # Resize image
    img = cv2.resize(img, (224,224))
    img = np.array(img)
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    hog_features = hog(
        gray,
        orientations=9,
        pixels_per_cell=(16, 16),
        cells_per_block=(2, 2),
        )

    # Flatten the features to a 1D array
    x = np.array(hog_features)

    # Make a prediction
    if model == "SVM":
      y = svm_model.predict(x.reshape(1, -1))  # Reshape to match model input

    elif model == "KNN":
      y = knn_model.predict(x.reshape(1, -1))  # Reshape to match model input

    elif model == "ANN":
      y = ann_model.predict(x.reshape(1, -1))  # Reshape to match model input
    else:
      raise ValueError("Invalid model choice")

    return f"Prediction: {y[0]}"  # Adjust if the output needs decoding

def cnn (image_path,model):
  image = load_img(image_path, target_size=(224, 224))

  # Preprocess the image
  img_array = img_to_array(image)
  img_array = img_array / 255.0
  img_array = np.expand_dims(img_array, axis=0)

  # Predict with the model
  predictions = model.predict(img_array)
  predicted_class_index = np.argmax(predictions, axis=1)[0]

  #determine class
  if  predicted_class_index == 0 :
    return 'Cataract'

  elif predicted_class_index == 1 :
    return 'Diabetic_retinopathy'

  elif predicted_class_index == 2 :
    return 'Glaucoma'

  else:
    return 'Normal'

def process_image(image_path, model_choice):
    if model_choice == "YOLOv8":
        # Use YOLO model for prediction
        results = yolo_model(image_path)
        annotated_image = results[0].plot()  # Annotate the image
        return annotated_image, "No prediction label "

    elif model_choice == "SVM":
        # Use SVM model for prediction
        annotated_image = predict(image_path,"SVM")
        return image_path, annotated_image

    elif model_choice == "KNN":
        # Use KNN model for prediction
        annotated_image = predict(image_path,"KNN")
        return image_path, annotated_image

    elif model_choice == "ANN":
        # Use ANN model for prediction
        annotated_image = predict(image_path,"ANN")
        return image_path, annotated_image


    elif model_choice == "CNN no dropout":
        # Use CNN model for prediction
        annotated_image = cnn(image_path,cnn_nodropout_model)
        return image_path, annotated_image

    elif model_choice == "CNN dropout":
        # Use CNN model for prediction
        annotated_image = cnn(image_path,cnn_dropout_model)
        return image_path, annotated_image

    elif model_choice == "YOLOv8-seg":
        # Use YOLO model for prediction
        results = yolo_seg_model(image_path)
        annotated_image = results[0].plot()  # Annotate the image
        return annotated_image, "No prediction label "
    else:
        raise ValueError("Invalid model choice")
        return None,None


# Define the Gradio interface
interface = gr.Interface(
    fn=process_image,  # Function to handle input and output
    inputs=[
        gr.Image(type="filepath", label="Upload Image"),  # Input: Image
        gr.Radio(choices=["SVM","KNN","ANN","CNN no dropout","CNN dropout","YOLOv8","YOLOv8-seg"], label="Choose Model")  # Input: Model selection
    ],
    outputs=[
        gr.Image(type="numpy", label="Image"),  # Output: Annotated image
        gr.Textbox(label="Prediction Label")  # Output: Text label
    ],
    title="Eye Disease Classificatio and Detection",
    description="Upload an image and select a classification model (SVM, ANN, KNN,CNN) or Detection model (YOLOv8) or Segmentation model (YOLOv8-seg).",
    theme=gr.themes.Soft(),
)



# Launch the interface
interface.launch()