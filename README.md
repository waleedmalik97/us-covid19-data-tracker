# US Covid-19 Data Tracker

The purpose of this web app is to perform data analysis of US covid-19 statistics through various exploratory data analysis techniques like geospatial analysis, time-series analysis etc. and have an overview of the situation of Covid-19 in US at both State and County Level.

The app is developed using Dash Python framework which is built on top of React.js and Flask, which enables you to build web-applications using pure Python and for the graphs Plotly graphing library is used, which is a high-level library and is built on top of D3.js and Stack.gl.

## Description:

The app basically consist of two sections.
The first section consist of a US state-level map with two radio buttons in order to filter the data for fully vaccinated persons or persons vaccinated with atleast one dose.
Below that map there is a slider that represents the timeline since the first covid case was recorded

The second section consist of two dropdown menus for selecting State and County, county level map with the same funtionality as of the state-level map but with the map filtered down to each state's counties and two time-serires graphs where one represents the total number of new cases per 100,000 persons within the last 7 days and the other represents the Percentage of positive diagnostic and screening nucleic acid amplification tests (NAAT) during the last 7 days both of which can be filtered down futher with a range slider to select the dates ranges from the dataset.

## Dataset Utilized:

COVID-19 Vaccinations in the United States,Jurisdiction: https://data.cdc.gov/Vaccinations/COVID-19-Vaccinations-in-the-United-States-Jurisdi/unsk-b7fc
COVID-19 Vaccinations in the United States,County: https://data.cdc.gov/Vaccinations/COVID-19-Vaccinations-in-the-United-States-County/8xkx-amqh
United States COVID-19 County Level of Community Transmission as Originally Posted: https://data.cdc.gov/Public-Health-Surveillance/United-States-COVID-19-County-Level-of-Community-T/8396-v7yb


https://user-images.githubusercontent.com/31138706/150209244-2699b6e5-6e7b-4ddd-947a-5e950b3e6560.mp4
