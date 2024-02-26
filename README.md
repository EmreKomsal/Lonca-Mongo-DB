Lonca Scraper Pipeline: Product Entry

Overview

This Python script is part of the Lonca Scraper Pipeline, focusing on the Product Entry aspect. It extracts product data from an XML file and stores it into a MongoDB collection, ensuring no duplication of data in subsequent runs.

Features

MongoDB Integration: Connects to MongoDB for data storage.
XML Parsing: Extracts data from XML files containing product information.
Data Consistency: Implements formatting rules such as capitalizing the first letter of product names.
Periodic Execution: Designed to run periodically without duplicating entries.
Requirements

Python 3.x
pymongo library
MongoDB instance (local or remote)

Installation

Ensure Python 3.x and MongoDB are installed.
Install pymongo using pip:
Copy code
pip install pymongo
Usage

Update the MongoDB connection details in the script if necessary.
Run the script with the XML file containing product data:
Copy code
python lonca.py
XML File Structure

The script expects the following XML structure for products:

Product ID
Name
Images
Various product details (e.g., price, discounted price)
Evaluation Criteria

The script is evaluated based on:

Modularity
Readability
Robustness
Efficiency
Object-Oriented Approach
Git Usage
