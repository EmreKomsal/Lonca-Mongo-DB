import pymongo
import xml.etree.ElementTree as ET

class MongoDBClient:
    def __init__(self, host="localhost", port=27017):
        self.host = host
        self.port = port
        self.connection = None
        self.db = None
        self.col = None
        
    def connect(self, db_name, col_name):
        try:
            self.connection = pymongo.MongoClient(f"mongodb://{self.host}:{self.port}")   # Connect to the MongoDB server
            self.db = self.connection[db_name]    # Connect to the lonca database
            self.col = self.db[col_name]    # Connect to the products collection
            print("Connected to MongoDB and ready to import XML data.")
        except pymongo.errors.ConnectionFailure:    # If connection to the database fails
            print("Could not connect to MongoDB")
            
    def disconnect(self):
        self.connection.close()     # Close the connection to the MongoDB server
        
    def import_data(self, data):
        try:
            self.col.insert_many(data)      # Insert the products into the collection
            print("Data imported successfully.")   # Print success message
        except pymongo.errors.BulkWriteError as e:
            print(f"Error importing data: {e.details['writeErrors']}")
    
    def update_data(self, data):
        try:
            for product_data in data:
                existing_product = self.col.find_one({"ProductID": product_data["ProductID"]})   # Check if the product already exists in the collection
                if existing_product:    # If the product already exists
                    self.col.update_one({"ProductID": product_data["ProductID"]}, {"$set": product_data})
                    print(f"Product {product_data['ProductID']} updated.")
                else:   # If the product does not exist
                    print(f"Product {product_data['ProductID']} does not exist in the collection.")
                    self.import_data([product_data])   # Import the new product to the collection
        except pymongo.errors.BulkWriteError as e:
            print(f"Error updating data: {e.details['writeErrors']}")
    
    def print_products(self):
        for product in self.col.find():    # Find all the products in the collection
            print(product["ProductID"])      # Print the product data

class XMLParser:
    def __init__(self, file_path):  # Initialize the XMLParser class
        self.file_path = file_path  # Set the file path
        self.tree = None    # Initialize the tree variable
        self.products = None  # Initialize the products variable
        self.products_list = [] # Initialize the products list
    
    def parse(self):
        try:
            self.tree = ET.parse(self.file_path)     # Parse the XML file
            self.products = self.tree.findall(".//Product")   # Find all the products in the XML file
            for p in self.products:
                product_data = {
                    "ProductID": p.attrib["ProductId"],     # Get the product ID
                    "ProductName": p.attrib["Name"],       # Get the product name
                    "Images": [img.attrib["Path"] for img in p.findall("./Images/Image")],  # Get the images
                    "Details": {detail.attrib["Name"]: detail.attrib["Value"] for detail in p.findall("./ProductDetails/ProductDetail")},   # Get the product details
                    "Description": p.find("./Description").text     # Get the product description
                }
                self.products_list.append(product_data)  # Add the product data to the list
            return self.products_list
        except ET.ParseError:       # If there is an error parsing the XML file
            print("Error parsing XML file")         # Print error message
            return None
    

class ProductImporter:
    def __init__(self, file_path, db_client): # Initialize the ProductImporter class
        self.file_path = file_path  # Set the file path
        self.db_client = db_client  # Set the database client
        self.products = None   # Initialize the products variable
        
    def import_products(self):  # Import the products
        self.products = XMLParser(self.file_path).parse()   # Parse the XML file and get the products
        if self.products:   # If there are products to import
            self.db_client.update_data(self.products)   # Update the products in the collection
            self.db_client.print_products()     # Print the products in the collection
        else: 
            print("No products to import.")  # Print message if there are no products to import
            
def main():   
    db_client = MongoDBClient()
    db_client.connect("lonca", "products")
    importer = ProductImporter("lonca-sample.xml", db_client)
    importer.import_products()
    db_client.disconnect()

if __name__ == "__main__":  # If the script is run directly
    main()   # Run the main function