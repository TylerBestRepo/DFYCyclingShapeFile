# DFYCyclingShapeFile
The purpose of this repository is to take various files and collate them into a shapefile for easy viewing on the open source software QGIS

To start, make sure to have Python 3 installed https://www.python.org/downloads/.
You will also need to install the open source software QGIS https://qgis.org/en/site/forusers/download.html Only the QGIS Standalone installer version is required, not the network installer.

After downloading and installing pyhton and QGIS you will need to download Garmin's FIT SDK. The WAHOO ELEMNT GPS device used in this study outputs files in a .fit format and this SDK allows for easy and quick conversion to the more useful CSV format. https://developer.garmin.com/fit/download/

# Connecting the Python project to use the QGIS python as the interpretor
It is necessary to use the QGIS Python otherwise the script would not be able to create the necessary shapefiles.

Navigate to settings in your Python IDE, then Project, then Python interpretor. A virtual environment is not required for this. Choose add interpretor next to the drop down and then choose system interpretor. You will then need to know where you installed QGIS to navigate to the necessary file. We are linking **python-qgis.bat** located in **OSGeo4W\bin** as seen below. This file links to the python as well as the necessary libraries. 
![image](https://user-images.githubusercontent.com/93167220/143323841-98ce157c-0c7d-4b88-a13d-fa9e1700e2f2.png)

# Retrieving data from the WAHOO ELEMNT
To retrieve the files from the GPS plug it in using a USB-C cable and turn the device on otherwise it will stay in charging mode. It will be called "MTP USB DEVIC", access internal storage and then the exports folder and there all of the recorded rides will be present. They are named by the date and time the rides were recorded. Copy and paste all rides to local storage for analysis.
![image](https://user-images.githubusercontent.com/93167220/143325560-3e26cfd6-073c-488a-a3fb-2be2d30da734.png)

Alternatively the data can also be sent from the mobile phone the device is paired to by navigating to the ELEMNT app. Select the history tab and then choose the ride you wish to export. 

<img src="Screenshots/1.jpg" width = "300">

Select the kebab menu then choose **upload workout** 

<img src="Screenshots/2.jpg" width = "300">

Then select **Share file to...** 

<img src="Screenshots/4.jpg" width = "300">

At this point you have many options to email the file or store it on a variety of different cloud storage options that are installed on the phone. Now you have a .fit file that reads as complete jargon so before anything useful can be done with it it must be converted into a readable csv file using Garmins APK.

# Using the FIT SDK to convert to CSV files
After unpacking the files there is only one file that needs to be used to convert to a .csv format. Navigate to the files you have unpacked and enter the java folder. There you will find many FitToCSV files however the required one is **FitToCSV.bat**. To easily convert a .fit file simply drag and drop a fit file onto the .bat file and a second file will be made in the .csv format. They dont even need to be in the same directory so it is encourage to leave them separated. 
![image](https://user-images.githubusercontent.com/93167220/143324603-b43b6121-df76-4f34-9181-52becfcd85e1.png)

