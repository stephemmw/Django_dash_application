Dashboard Application for Data Visualization


Overview

This application is a Django-based data dashboard designed to visualize and analyze PostgreSQL database records in interactive tables and graphs. The app uses Dash to generate dynamic plots and graphs, while Django handles the backend, including data fetching and user interactions. The primary goal is to offer an interface that allows users to filter data and visualize statistical summaries, and download insights.

Features

Interactive Data Tables: Dynamically loaded and filterable tables with various attributes.
Data Visualization with Dash: Interactive graphs created using Dash for Plotly, rendering data from PostgreSQL dynamically.
Data Fetching from PostgreSQL: Efficiently retrieves data based on user-selected criteria, supporting large datasets.
Frontend Interactions: Custom HTML/CSS for responsive design and seamless interaction with the data and visualizations.


Folder Structure

Dashboard/
This folder contains the core configuration files for Django, including URL routing, settings, and WSGI configurations.

asgi.py: Handles ASGI configuration.
settings.py: Django settings, including PostgreSQL integration.
urls.py: Routes for the application, including integration with the Dash app and Django views.
wsgi.py: Web Server Gateway Interface configuration for deploying the app.
myapp/
This folder holds the main Django app components, including models, views, and templates.

Subfolders:
migrations/: Database migrations for the Django models.
static/: CSS, JS, and other static assets used in the frontend.
templates/: Contains the HTML templates used to render the web pages.

Main Files:
admin.py: Django admin configurations.
apps.py: Configuration for the Django app.
data_analysis.py: Logic for performing complex data filtering and analysis on PostgreSQL data.
models.py: Defines the structure of the data loaded from PostgreSQL using Django's ORM.
views.py: Handles HTTP requests, fetches data from the database, and renders HTML templates with data.
dash_app.py
This file contains the Dash application logic that renders the graphs and allows interactive data filtering. Dash components interact with the Django backend to fetch data based on user input.

Dash Layout: Defined using html and dcc components for dropdowns, graphs, and other interactive elements.
Callbacks: Dash callbacks are used to update graphs and tables dynamically based on user input.
Data Loading: Calls the data loading logic to fetch and process PostgreSQL records.

How the Components Interact
User Interface:

The frontend, rendered by Django’s index.html, includes buttons, tables, and dropdowns for data selection (years, arrondissements, etc.).
Dash, integrated via Django, handles dynamic plots embedded in the page.


Data Fetching:

When users select filters or data ranges (years, arrondissements) inside the dash app, the data is fetched from PostgreSQL using Django's ORM (see models.py).
The DynamicTableLoader class in models.py is responsible for querying PostgreSQL dynamically based on these filters.

Data Analysis:

Data fetched is analyzed in data_analysis.py. This module applies custom filters (e.g., date ranges, quote names) and returns results in the form of Pandas DataFrames.
The analyzed data is then passed back to the views, where it's converted into JSON to be displayed in tables or graphs.
Interactive Dashboards:

Dash uses the data from Django’s backend to render interactive graphs, such as time-series plots of specific quote values over time. These graphs are dynamically updated based on user selections (handled in dash_app.py).# Django_dash_application
Django app that takes in data from a postgresql database and displays the data in interactive graphs and tables using html, css, dash.
