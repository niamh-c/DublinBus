# COMP47360 Research Practicum: Predicting Dublin Bus Journey Times

## Table of Contents

- [Introduction](#intro)
- [Features](#features)
- [Prerequisites](#pre)
- [Installation](#install)
- [Running the Application](#run)
- [Contributions](#contr)

## <a name="intro">Introduction</a>
Route 13 is an eay to use application that accurately estimates the travel time of buses ran by Dublin Bus. If you want accurate estimations of bus arrival times that consider the affect weather and historical traffic patterns have on travel times, clone and launch.

Our homepage allows you to choose from three features, Search by Stop, Search by Destination and Tourist Journey Planner. Search by Stop will give you arrurate arrival times for all buses that serve your stop. Search by Destination will find a bus stop near your destination and departure points and plan your journey for you. Tourist Journey Planner provides a list of popular Dublin Tourist destinations from which you can select your preferred destinations and the application will provide you with the best route to travel to each starting and ending at a point of your choice!

## <a name="features">Features</a>

__UX Design:__ Simple and easy to use interface which includes common user features such as a home button.
__Prediction Models:__ Premade prediction models which can be used with Dublin Bus GTFS data to accurately predict bus arrival time.
__Routing:__ Does not rely on APIs for routing.

## <a name="pre">Prerequisites</a>

### Git
Used to clone the repository and navigate its branches.

### Anaconda
Anaconda is a Python distibution used to create virtual environments and will be used to both create and manage virtual environments and install some Python libraries.

### Pip
Pip is a package management system for installing python software packages and will be used to install the necessary Python libraries for running the application.

### Nodejs
Nodejs is a Javascript run-time environment used to execute Javascript outside of a browser and will be used to install, build and provide test runs of the React application.

### Redis
Redis is an in-memory data store used as a cache in the application.

### MySQL
MySQL is a relational database management system used to store the data which drives the application.

## <a name="install">Installation</a>

1. Clone the git repository, master is the stable branch and is immutable.

        git clone https://github.com/johnmcl001/DublinBusProject.git

2. Change into the DublinBusProject directory

        cd DublinBusProject

3. (Optional) Create a virtual environment using conda.

        conda create -n DublinBus python=3.7

4. (Optional) Activate the environment created in the previous step.

        conda activate DublinBus

5. Install the required python libraries using pip.

        pip install -r requirements

6. Install mysqlclient with conda.

        conda install mysqlclient

7. Change into the frontend directory.

        cd DublinBus/frontend

8. Install the required node packages.

        npm install

9. Install npx.

        npm install npx

## <a name="run">Running the Application</a>

1. Start the Django backend.

        cd ~/DublinBusProject/DublinBus
        python manage.py runserver

2. Start the redis server.

        redis-server

3. Start the MySQL database.

        sudo systemctl start mysql
        
4. Create a dotenv file.

        USER = mysql username e.g root
        PASSWORD = mysql database password
        HOST = lcoalhost e.g. '127.0.0.1'
        
5. Unzip the pickles file and update your database with neccessary GTFS data. This usually takes 30-35 minutes.

        unzip GTFS/pickles_random_forest.zip 
        unzip GTFS/pickles_random_forest1.zip 
        mv GTFS/pickle_random_forest1/* GTFS/pickle_random_forest
        python GTFS/data_update.py

4. Start a development build of the React frontend.

        cd ~/DublinBusProject/DublinBus/frontend
        npm run dev

5. Navigate to localhost:1234 in a browser.

5. (Optional) Make a production build of the React frontend.

        cd ~/DublinBusProject/DublinBus/frontend
        npm run build

6. (Optional) Start a production build of the React frontend.

        cd ~/DublinBusProject/DublinBus/frontend
        npm run start

7. (Optional) Navigate to localhost:5000 in a browser

## <a name="contr">Contributions</a>

- John McLoughlin
- Niamh Crowley
- Deyan Chen
- Nonty Dazana 




