import pymongo
import xml.etree.ElementTree as ET

# Connect to the database
try:
    connection = pymongo.MongoClient("mongodb://localhost:27017")   # Connect to the MongoDB server
    db = connection["lonca"]    # Connect to the lonca database
    col = db["products"]    # Connect to the products collection
    print("Connected to MongoDB and ready to import XML data.")
except pymongo.errors.ConnectionFailure:    # If connection to the database fails
    print("Could not connect to MongoDB") 

# Load and parse the XML file
try:
    tree = ET.parse("lonca-sample.xml")     # Parse the XML file
    products = tree.findall(".//Product")   # Find all the products in the XML file
    products_list = [] # List to store the products
    for p in products:
        product_data = {
            "ProductID": p.attrib["ProductId"],     # Get the product ID
            "ProductName": p.attrib["Name"],       # Get the product name
            "Images": [img.attrib["Path"] for img in p.findall("./Images/Image")],  # Get the images
            "Details": {detail.attrib["Name"]: detail.attrib["Value"] for detail in p.findall("./ProductDetails/ProductDetail")},   # Get the product details
            "Description": p.find("./Description").text     # Get the product description
        }
        
        existing_product = col.find_one({"ProductID": product_data["ProductID"]})   # Check if the product already exists in the collection
        if existing_product:    # If the product already exists
            col.update_one({"ProductID": product_data["ProductID"]}, {"$set": product_data})
            print(f"Product {product_data['ProductID']} updated.")
        else:   # If the product does not exist
            products_list.append(product_data)  # Add the product data to the list

    # Insert data into the collection
    if products_list:   # If there are products in the list
        col.insert_many(products_list)      # Insert the products into the collection
        print("Data imported successfully.")   # Print success message
except ET.ParseError:       # If there is an error parsing the XML file
    print("Error parsing XML file")         # Print error message

# Display the data in the collection 
for product in col.find():    # Find all the products in the collection
    print(product["ProductID"])      # Print the product data
# Close the connection
connection.close()     # Close the connection to the MongoDB server