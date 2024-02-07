Simple way to get backend data (python flask) display on the frontend (next.js)

Directory setup:

1. create a server directory for our backend
2. create a virtual environment for our python dependencies
3. create a client directory for our frontend
4. run the following next.js command to populate our client directory - npx create-next-app .
    - typescript = yes
    - eslint = yes
    - tailwind css = yes
    - src directory = no
    - app router = no
    - import alias = no
    above are the chosen options for the particular project

Code:

5. in the server directory create server.py - this is where our flask code will reside:

from flask import Flask, jsonify
from flask_cors import CORS

# app instance
app = Flask(__name__)
CORS(app)

@app.route("/api/home", methods=['GET'])
def return_home():
    return jsonify({
        'message': "Hello world!"
    })

if __name__ == "__main__":
    app.run(debug=True, port=5001) 
    # port 5001 because 5000 seems to have an issue with CORS when getting frontend requests

The above code is very simple and does the following:

- imports flask, jsonify and flask_cors - the latter is crucial in enabling the frontend to interact with the backend
- creates an app instance
- returns a simple "Hello world!" json message in the /api/home endpoint
- assigns port 5001 to our code therefore the full endpoint address is - http://localhost:5001/api/home

6. in the client directory go to styles -> globals.css and remove everything except the first 3 lines (optional)
7. still in the client directory go to pages -> index.tsx and write the following:

import React, { useEffect, useState } from 'react'

function index() {
  const [message, setMessage] = useState("Loading");

  useEffect(() => {
    fetch("http://localhost:5001/api/home")
      .then((response) => response.json())
      .then((data) => {
        setMessage(data.message);
        // console.log(data); // to show the log in the browser console
      });
  }, []);

  return (
    <div>{message}</div>
  )
}

export default index

- we create a message variable and temporarily assign it the "Loading" value, this will automatically be changed when we return the backend data we want
- the above code tells our frontend where to fetch the backend data (http://localhost:5001/api/home), notice this is the api endpoint we set in our backend
- once the api endpoint is accessed the data is returned in json and stored in data.message
- console.log(data) - this shows our data in the browser console
- return (<div>{message}</div>) - this displays the backend data on our frontend, in this case the following is grabbed from the backend and displayed to us on the frontend which runs on http://localhost:3000/

Hello world!

and this is a simple example of how to enable the frontend to get and display data from the backend

NOTE: below are the commands to run our local environments

for flask   - python3 server.py
for next.js - npm run dev

Running the app in Docker containers:

8. create a Dockerfile for both frontend & backend

frontend Dockerfile:

# Use the official lightweight Node.js 16 image as a base
FROM node:21-alpine

# Set the working directory in the container
WORKDIR /app

# Copy the package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the remaining application code
COPY . .

# Build the Next.js application
RUN npm run build

# Expose port 3000 to the outside world
EXPOSE 3000

# Command to run the application
CMD ["npm", "start"]

--------------------------------

backend Dockerfile:

# Use a base Python image
FROM python:3.8-slim

# Set working directory
WORKDIR /app

# Copy the application code into the container
COPY . /app

# Install dependencies into the virtual environment
RUN pip install --no-cache-dir -r requirements.txt

# Expose any necessary ports
EXPOSE 5001

# Define environment variable
ENV FLASK_APP=server.py
ENV FLASK_RUN_HOST=0.0.0.0

# Set the command to run your application
CMD ["python", "server.py"]

the frontend and backend should then be running in localhost on their respective ports, in this instance:

http://localhost:3000/
http://127.0.0.1:5001/api/home

Run the app in docker-compose

9. in the project's root directory create a file called docker-compose.yml:

version: '3'

services:
  umrahdeals-frontend:
    build: ./client
    ports:
      - "3000:3000"
    restart: always

  umrahdeals-backend:
    build: ./server
    ports:
      - "5001:5001"
    restart: always

10. run the containers with this command - docker-compose up -d