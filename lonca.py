import pymongo
import xml.etree.ElementTree as ET

# Connect to the database
try:
    connection = pymongo.MongoClient("mongodb://localhost:27017")
    db = connection["lonca"]
    col = db["products"]
    print("Connected to MongoDB and ready to import XML data.")
except pymongo.errors.ConnectionFailure:
    print("Could not connect to MongoDB")

# Load and parse the XML file
try:
    tree = ET.parse("lonca-sample.xml")
    products = tree.findall(".//Product")
    products_list = [{"ProductID": p.attrib["ProductId"], "ProductName": p.attrib["Name"]} for p in products]


    # Insert data into the collection
    if products_list:
        col.insert_many(products_list)
        print("Data imported successfully.")
except ET.ParseError:
    print("Error parsing XML file")

# Display the data in the collection
for product in col.find():
    print(product)

# Close the connection
connection.close()