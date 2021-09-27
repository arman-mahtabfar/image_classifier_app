import os
import json
import numpy as np
import mysql.connector
from flask import Flask
from PIL import Image
from flask import request, jsonify
from keras.applications.vgg16 import VGG16
from keras.preprocessing.image import load_img
from keras.preprocessing.image import img_to_array
from keras.applications.vgg16 import preprocess_input
from keras.applications.vgg16 import decode_predictions

app = Flask(__name__)
model = VGG16()

def initializeDB():
  mydb = mysql.connector.connect(
    host="mysqldb",
    user="root",
    password="password1"
  )
  cursor = mydb.cursor()

  cursor.execute("DROP DATABASE IF EXISTS classification")
  cursor.execute("CREATE DATABASE classification")
  cursor.close()

  mydb = mysql.connector.connect(
    host="mysqldb",
    user="root",
    password="password1",
    database="classification"
  )
  cursor = mydb.cursor()

  cursor.execute("DROP TABLE IF EXISTS classifier")
  cursor.execute("CREATE TABLE classifier (imageName VARCHAR(255), output VARCHAR(255))")
  cursor.close()

  return 'initialized db'


initializeDB()


@app.route('/')
def hello_world():
  return 'Hello, Docker!'
  
@app.route('/health')
def health():
  return "OK", 200

@app.route('/test-model', methods = ['GET'])
def testin():
    image = load_img('test.jpg', target_size=(224, 224))
    image = img_to_array(image)
    image = image.reshape((1, image.shape[0], image.shape[1], image.shape[2]))
    image = preprocess_input(image)
    yhat = model.predict(image)
    label = decode_predictions(yhat)
    label = label[0][0]
    print('%s (%.2f%%)' % (label[1], label[2]*100))
    return '%s (%.2f%%)' % (label[1], label[2]*100)


@app.route('/classify', methods = ['POST'])
def classify():

    file = request.files['image']
    imageName = request.form['name']
    # Read the image via file.stream
    img = Image.open(file.stream)
    
    filePath = 'images/' + imageName
    img.save(filePath, format='jpeg')

    # predict image classification using model
    image = load_img(filePath, target_size=(224, 224))
    image = img_to_array(image)
    image = image.reshape((1, image.shape[0], image.shape[1], image.shape[2]))
    image = preprocess_input(image)
    yhat = model.predict(image)
    label = decode_predictions(yhat)
    label = label[0][0]

    mydb = mysql.connector.connect(
    host="mysqldb",
    user="root",
    password="password1",
    database="classification"
    )
    cursor = mydb.cursor()


    cursor.execute("INSERT INTO classifier (imageName, output) VALUES ('" + imageName + "','" + label[1] + "')")
    mydb.commit()
    cursor.close()
    
    return jsonify({'msg': 'success', 'size': [img.width, img.height], 'image': imageName, 'classification': label[1]})


@app.route('/list-classifications', methods = ['GET'])
def get_classifications() :
  mydb = mysql.connector.connect(
    host="mysqldb",
    user="root",
    password="password1",
    database="classification"
  )
  cursor = mydb.cursor()


  cursor.execute("SELECT * FROM classifier")

  row_headers=[x[0] for x in cursor.description] #this will extract row headers

  results = cursor.fetchall()
  json_data=[]
  for result in results:
    json_data.append(dict(zip(row_headers,result)))

  cursor.close()

  return json.dumps(json_data)

@app.route('/resetdb')
def db_init():
  initializeDB()
  os.system('rm -rf images')
  os.system('mkdir images')
  return 'reset database'


if __name__ == "__main__":
  app.run()