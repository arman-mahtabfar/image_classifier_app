import json
import numpy as np
import mysql.connector
from flask import Flask
from flask import request
from keras.applications.vgg16 import VGG16
from keras.preprocessing.image import load_img
from keras.preprocessing.image import img_to_array
from keras.applications.vgg16 import preprocess_input
from keras.applications.vgg16 import decode_predictions

app = Flask(__name__)
model = VGG16()

@app.route('/')
def hello_world():
  return 'Hello, Docker!'
  
@app.route('/health')
def health():
  return "OK", 200

@app.route('/test', methods = ['GET'])
def testin():
    image = load_img('woman.jpg', target_size=(224, 224))
    # convert the image pixels to a numpy array
    image = img_to_array(image)
    # reshape data for the model
    image = image.reshape((1, image.shape[0], image.shape[1], image.shape[2]))
    # prepare the image for the VGG model
    image = preprocess_input(image)
    # predict the probability across all output classes
    yhat = model.predict(image)
    # convert the probabilities to class labels
    label = decode_predictions(yhat)
    # retrieve the most likely result, e.g. highest probability
    label = label[0][0]
    # print the classification
    print('%s (%.2f%%)' % (label[1], label[2]*100))
    return '%s (%.2f%%)' % (label[1], label[2]*100)



@app.route('/classify', methods = ['POST'])
def classify():

    # TODO
    # get image from post request
    # use the image as a parameter to call the ai classifier
    # store the image and its description given from the classifier together in mysql db
    
    data = request.json
    image = np.array(data['image']) #this is the image in numpy array RGB format
    
    #use the model to predict what the fuck the image is...
    image = image.reshape((1, image.shape[0], image.shape[1], image.shape[2]))

    image = preprocess_input(image)
    yhat = model.predict(image)
    
    label = decode_predictions(yhat)
    label = label[0][0]
    
    #this is the classification!
    print('%s (%.2f%%)' % (label[1], label[2]*100))
    
    #insert this classification into MySQL
    queryMySQL(f"""INSERT INTO image (img_data, description) VALUES ({img_byes}, "{img_description}")""")
    
    return 'success'



@app.route('/widgets')
def get_widgets() :
  mydb = mysql.connector.connect(
    host="mysqldb",
    user="root",
    password="p@ssw0rd1",
    database="inventory"
  )
  cursor = mydb.cursor()


  cursor.execute("SELECT * FROM widgets")

  row_headers=[x[0] for x in cursor.description] #this will extract row headers

  results = cursor.fetchall()
  json_data=[]
  for result in results:
    json_data.append(dict(zip(row_headers,result)))

  cursor.close()

  return json.dumps(json_data)

@app.route('/initdb')
def db_init():
  mydb = mysql.connector.connect(
    host="mysqldb",
    user="root",
    password="p@ssw0rd1"
  )
  cursor = mydb.cursor()

  cursor.execute("DROP DATABASE IF EXISTS inventory")
  cursor.execute("CREATE DATABASE inventory")
  cursor.close()

  mydb = mysql.connector.connect(
    host="mysqldb",
    user="root",
    password="p@ssw0rd1",
    database="inventory"
  )
  cursor = mydb.cursor()

  cursor.execute("DROP TABLE IF EXISTS widgets")
  cursor.execute("CREATE TABLE widgets (name VARCHAR(255), description VARCHAR(255))")
  cursor.close()

  return 'init database'

if __name__ == "__main__":
  app.run(host ='0.0.0.0')