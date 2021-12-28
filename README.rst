COVID-19 Dashboard
====================================



Introduction
------------------------------------


This Python project that creates a Covid-19 dashboard in the form of an executable html file. It uses the Public Health England Covid-19 API 
and News API to import necessary COVID-19 data and news data for the dashboards. 

The dashboard's features: 
   > Is integrated with the configuration file (config.json)
   > Displays the following data:
      - Total Cases in the past week (National and Local)
      - Total Hospital Cases (National)
      - Total Deaths (National)
      - News articles filtered to the provided covid_terms in the configuration file 
      - Scheduled Updates 
   > Scheduling updates to the News and Covid-data separately. 
   > Removing articles and Cancelling Scheduled Updates. 

This is combined with a numerous of tests and logging to make the program accountable and makes it possible to trace behaviour and recover state. 


Requirements
------------------------------------


This module requires the following modules:

   * [uk_covid19] (add links)
   * [flask] (add links)
   * [requests] (add links)
   * [json] 
   * [multiprocessing] or [sched] or [threading]
   * [time]
   * [datetime]
 

Recommended Modules:
------------------------------------


*[multiprocessing] 
Allows for concurrency; easier execution of Scheduled updates without interfering with the main/root thread. 
   
* [logging]
Makes the progam accountable and makes it possible to trace behaviour and recover state. 
   
* [pytest]
Helps to write simple and scalable test cases, and also makes testing process organised and efficient. 


Installation
------------------------------------


Required Installations
....................................


Using Terminal or Command Prompt, navigate to the downloaded COVID DASHBOARD folder.
 ```
 C:\Users\username> cd Desktop\Covid Dashboard
```

If done correctly, it should look like this:
```
 C:\Users\username> cd Desktop\Covid Dashboard> 
```

Before installing the dependencies, it is recommended to create a Virtual Environment. When you are using a virtual environment, 
you only see the packages that you have installed in that environment.  This helps prevent version conflicts between different projects. 

To set up the Virtual Environment refer to instructions in the next section.


To install all the required dependencies, please run:
```
 C:\Users\username> cd Desktop\Covid Dashboard> pip install - r requirements.txt 
```


Setting up your Virtual Environment
.....................................


To install, please run: 
```
C:\Users\username> cd Deskop/foldername
```

Create a virtual environment in the Project Folder using :
```
C:\Users\username\foldername> python -m venv *name of virtual environment*
```

Activating Virtual Environment:
 
```
C:\Users\username\foldername> source *name of virtual environment*/bin/activate (FOR MAC AND LINUX)

C:\Users\username\foldername> *name of virtual environment*\Scripts\activate.bat  (FOR WINDOWS)
```
   
Deactivating Virtual Environment:
```
C:\Users\username\foldername> deactivate
```


How to use Covid Dashboard Package
-------------------------------------

config.json
.....................................

This is the configuration file which can be used to change any of the basic input data, such as the Local and National locations, or the filters
for the news articles. 


Using all the modules 
.....................................


Visit the documentation 




   









