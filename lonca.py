import pymongo
import xml.etree.ElementTree as ET

def connect_to_mongodb():
    try:
        connection = pymongo.MongoClient("mongodb://localhost:27017")   # Connect to the MongoDB server
        db = connection["lonca"]    # Connect to the lonca database
        col = db["products"]    # Connect to the products collection
        print("Connected to MongoDB and ready to import XML data.")
        return connection, col
    except pymongo.errors.ConnectionFailure:    # If connection to the database fails
        print("Could not connect to MongoDB") 
        return None
    
def parse_xml_file(file_path):
    try:
        tree = ET.parse(file_path)     # Parse the XML file
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
            products_list.append(product_data)  # Add the product data to the list
        return products_list
    except ET.ParseError:       # If there is an error parsing the XML file
        print("Error parsing XML file")         # Print error message
        return None

def disconnect_from_mongodb(connection):
    connection.close()     # Close the connection to the MongoDB server

def import_data_to_mongodb(collection, data):
    try:
        collection.insert_many(data)      # Insert the products into the collection
        print("Data imported successfully.")   # Print success message
    except pymongo.errors.BulkWriteError as e:
        print(f"Error importing data: {e.details['writeErrors']}")

def update_data_in_mongodb(collection, data):
    import_datas = []
    for product_data in data:
        existing_product = collection.find_one({"ProductID": product_data["ProductID"]})   # Check if the product already exists in the collection
        if existing_product:    # If the product already exists
            collection.update_one({"ProductID": product_data["ProductID"]}, {"$set": product_data})
            print(f"Product {product_data['ProductID']} updated.")
        else:   # If the product does not exist
            print(f"Product {product_data['ProductID']} does not exist in the collection.")
            import_datas.append(product_data)   # Add the product data to the list of products to import
    
    if import_datas:    # If there are new products to import
        import_data_to_mongodb(collection, import_datas)    # Import the new products to the collection
            

def print_products_in_mongodb(collection):
    for product in collection.find():    # Find all the products in the collection
        print(product["ProductID"])      # Print the product data

def main():
    connection, col = connect_to_mongodb()
    if col:
        products = parse_xml_file("lonca-sample.xml")
        if products:
            update_data_in_mongodb(col, products)
            print_products_in_mongodb(col)
        else:
            print("No products to import.")
    else:
        print("Could not connect to MongoDB")
    disconnect_from_mongodb(connection)
        
if __name__ == "__main__":
    main()  # Run the main function