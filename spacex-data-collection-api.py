#!/usr/bin/env python
# coding: utf-8

# # **SpaceX  Falcon 9 First Stage Landing Prediction**
# Collecting the data

# ### Introduction

# In this capstone, we will predict if the Falcon 9 first stage will land successfully. SpaceX advertises Falcon 9 rocket launches on its website with a cost of 62 million dollars; other providers cost upward of 165 million dollars each, much of the savings is because SpaceX can reuse the first stage. Therefore if we can determine if the first stage will land, we can determine the cost of a launch. This information can be used if an alternate company wants to bid against SpaceX for a rocket launch. In this lab, you will collect and make sure the data is in the correct format from an API. The following is an example of a successful and launch.
# 

# ![](https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBMDeveloperSkillsNetwork-DS0701EN-SkillsNetwork/lab_v2/images/landing\_1.gif)
# 

# Several examples of an unsuccessful landing are shown here:
# 

# ![](https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBMDeveloperSkillsNetwork-DS0701EN-SkillsNetwork/lab_v2/images/crash.gif)
# 

# Most unsuccessful landings are planned. Space X performs a controlled landing in the oceans.
# 

# ## Objectives
# 
# *   Request to the SpaceX API
# *   Clean the requested data
# 

# ## Libraries and Auxiliary Functions
# 

# In[1]:


# Requests allows us to make HTTP requests which we will use to get data from an API
import requests
# Pandas is a software library written for the Python programming language for data manipulation and analysis.
import pandas as pd
# NumPy is a library for the Python programming language, adding support for large, multi-dimensional arrays and matrices, along with a large collection of high-level mathematical functions to operate on these arrays
import numpy as np
# Datetime is a library that allows us to represent dates
import datetime

# Setting this option will print all collumns of a dataframe
pd.set_option('display.max_columns', None)
# Setting this option will print all of the data in a feature
pd.set_option('display.max_colwidth', None)


# Below we will define a series of helper functions that will help us use the API to extract information using identification numbers in the launch data.
# 
# From the <code>rocket</code> column we would like to learn the booster name.
# 

# In[2]:


# Takes the dataset and uses the rocket column to call the API and append the data to the list
def getBoosterVersion(data):
    for x in data['rocket']:
        response = requests.get("https://api.spacexdata.com/v4/rockets/"+str(x)).json()
        BoosterVersion.append(response['name'])


# From the <code>launchpad</code> we would like to know the name of the launch site being used, the logitude, and the latitude.
# 

# In[3]:


# Takes the dataset and uses the launchpad column to call the API and append the data to the list
def getLaunchSite(data):
    for x in data['launchpad']:
        response = requests.get("https://api.spacexdata.com/v4/launchpads/"+str(x)).json()
        Longitude.append(response['longitude'])
        Latitude.append(response['latitude'])
        LaunchSite.append(response['name'])


# From the <code>payload</code> we would like to learn the mass of the payload and the orbit that it is going to.
# 

# In[4]:


# Takes the dataset and uses the payloads column to call the API and append the data to the lists
def getPayloadData(data):
    for load in data['payloads']:
        response = requests.get("https://api.spacexdata.com/v4/payloads/"+load).json()
        PayloadMass.append(response['mass_kg'])
        Orbit.append(response['orbit'])


# From <code>cores</code> we would like to learn the outcome of the landing, the type of the landing, number of flights with that core, whether gridfins were used, wheter the core is reused, wheter legs were used, the landing pad used, the block of the core which is a number used to seperate version of cores, the number of times this specific core has been reused, and the serial of the core.
# 

# In[5]:


# Takes the dataset and uses the cores column to call the API and append the data to the lists
def getCoreData(data):
    for core in data['cores']:
            if core['core'] != None:
                response = requests.get("https://api.spacexdata.com/v4/cores/"+core['core']).json()
                Block.append(response['block'])
                ReusedCount.append(response['reuse_count'])
                Serial.append(response['serial'])
            else:
                Block.append(None)
                ReusedCount.append(None)
                Serial.append(None)
            Outcome.append(str(core['landing_success'])+' '+str(core['landing_type']))
            Flights.append(core['flight'])
            GridFins.append(core['gridfins'])
            Reused.append(core['reused'])
            Legs.append(core['legs'])
            LandingPad.append(core['landpad'])


# Now let's start requesting rocket launch data from SpaceX API with the following URL:
# 

# In[6]:


spacex_url="https://api.spacexdata.com/v4/launches/past"
response = requests.get(spacex_url).json()


# Check the content of the response
# 

# In[7]:


response = requests.get(spacex_url)
response


# You should see the response contains massive information about SpaceX launches. Next, let's try to discover some more relevant information for this project.
# 

# In[ ]:





# ### Requesting and parsing the SpaceX launch data using the GET request
# 

# To make the requested JSON results more consistent, we will use the following static response object for this project:
# 

# In[8]:


static_json_url='https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DS0321EN-SkillsNetwork/datasets/API_call_spacex_api.json'


# We should see that the request was successful with the 200 status response code
# 

# In[9]:


response = requests.get(static_json_url)
response


# Now we decode the response content as a Json using <code>.json()</code> and turn it into a Pandas dataframe using <code>.json_normalize()</code>
# 

# In[10]:


# Use json_normalize method to convert the json result into a dataframe
response = requests.get(static_json_url).json()
data = pd.json_normalize(response)


# Using the dataframe <code>data</code> print the first 5 rows
# 

# In[11]:


# Get the head of the dataframe
data.head()


# You will notice that a lot of the data are IDs. For example the rocket column has no information about the rocket just an identification number.
# 
# We will now use the API again to get information about the launches using the IDs given for each launch. Specifically we will be using columns <code>rocket</code>, <code>payloads</code>, <code>launchpad</code>, and <code>cores</code>.
# 

# In[12]:


# Lets take a subset of our dataframe keeping only the features we want and the flight number, and date_utc.
data = data[['rocket', 'payloads', 'launchpad', 'cores', 'flight_number', 'date_utc']]

# We will remove rows with multiple cores because those are falcon rockets with 2 extra rocket boosters and rows that have multiple payloads in a single rocket.
data = data[data['cores'].map(len)==1]
data = data[data['payloads'].map(len)==1]

# Since payloads and cores are lists of size 1 we will also extract the single value in the list and replace the feature.
data['cores'] = data['cores'].map(lambda x : x[0])
data['payloads'] = data['payloads'].map(lambda x : x[0])

# We also want to convert the date_utc to a datetime datatype and then extracting the date leaving the time
data['date'] = pd.to_datetime(data['date_utc']).dt.date

# Using the date we will restrict the dates of the launches
data = data[data['date'] <= datetime.date(2020, 11, 13)]


# *   From the <code>rocket</code> we would like to learn the booster name
# 
# *   From the <code>payload</code> we would like to learn the mass of the payload and the orbit that it is going to
# 
# *   From the <code>launchpad</code> we would like to know the name of the launch site being used, the longitude, and the latitude.
# 
# *   From <code>cores</code> we would like to learn the outcome of the landing, the type of the landing, number of flights with that core, whether gridfins were used, whether the core is reused, whether legs were used, the landing pad used, the block of the core which is a number used to seperate version of cores, the number of times this specific core has been reused, and the serial of the core.
# 
# The data from these requests will be stored in lists and will be used to create a new dataframe.
# 

# In[13]:


BoosterVersion = []
PayloadMass = []
Orbit = []
LaunchSite = []
Outcome = []
Flights = []
GridFins = []
Reused = []
Legs = []
LandingPad = []
Block = []
ReusedCount = []
Serial = []
Longitude = []
Latitude = []


# Now, let's apply <code> getBoosterVersion</code> function method to get the booster version
# 

# In[14]:


getBoosterVersion(data)


# the list has now been update
# 

# In[15]:


BoosterVersion[0:5]


# we can apply the rest of the  functions here:
# 

# In[16]:


getLaunchSite(data)
getPayloadData(data)
getCoreData(data)


# Finally lets construct our dataset using the data we have obtained. We we combine the columns into a dictionary.
# 

# In[17]:


launch_dict = {'FlightNumber': list(data['flight_number']),
'Date': list(data['date']),
'BoosterVersion':BoosterVersion,
'PayloadMass':PayloadMass,
'Orbit':Orbit,
'LaunchSite':LaunchSite,
'Outcome':Outcome,
'Flights':Flights,
'GridFins':GridFins,
'Reused':Reused,
'Legs':Legs,
'LandingPad':LandingPad,
'Block':Block,
'ReusedCount':ReusedCount,
'Serial':Serial,
'Longitude': Longitude,
'Latitude': Latitude}


# Then, we need to create a Pandas data frame from the dictionary launch_dict.
# 

# In[18]:


df = pd.DataFrame.from_dict(launch_dict)


# Show the summary of the dataframe
# 

# In[19]:


df.head()


# ### Filtering the dataframe to only include `Falcon 9` launches
# 

# In[20]:


data_falcon9 = df.loc[df['BoosterVersion']!="Falcon 1"]


# In[21]:


data_falcon9.loc[:,'FlightNumber'] = list(range(1, data_falcon9.shape[0]+1))
data_falcon9


# ## Data Wrangling
# 

# We can see below that some of the rows are missing values in our dataset.
# 

# In[22]:


data_falcon9.isnull().sum()


# Before we can continue we must deal with these missing values. The <code>LandingPad</code> column will retain None values to represent when landing pads were not used.
# 

# ### Dealing with Missing Values
# ##### We calculate mean of column and replace the none values with mean

# In[23]:


# Calculate the mean value of PayloadMass column
mean = data_falcon9['PayloadMass'].mean()
# Replace the np.nan values with its mean value
data_falcon9['PayloadMass'] = data_falcon9['PayloadMass'].fillna(mean)


# In[24]:


data_falcon9.isnull().sum()


# You should see the number of missing values of the <code>PayLoadMass</code> change to zero.
# 

# Now we should have no missing values in our dataset except for in <code>LandingPad</code>.
# 

# We can now export it to a <b>CSV</b> 
# 

# In[25]:


data_falcon9.to_csv('dataset_part_1.csv', index=False)


# ### Author : Ashlin Darius Govindasamy
