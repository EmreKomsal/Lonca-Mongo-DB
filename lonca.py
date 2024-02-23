import pymongo
import xml.etree.ElementTree as ET
import re
import pprint


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
                existing_product = self.col.find_one({"stock_code": product_data["stock_code"]})   # Check if the product already exists in the collection
                if existing_product:    # If the product already exists
                    self.col.update_one({"stock_code": product_data["stock_code"]}, {"$set": product_data})
                    print(f"Product {product_data['stock_code']} updated.")
                else:   # If the product does not exist
                    print(f"Product {product_data['stock_code']} does not exist in the collection.")
                    self.import_data([product_data])   # Import the new product to the collection
        except pymongo.errors.BulkWriteError as e:
            print(f"Error updating data: {e.details['writeErrors']}")
    
    def print_products(self):
        for product in self.col.find():    # Find all the products in the collection
            pprint.pprint(product)      # Print the product data

class XMLParser:
    def __init__(self, file_path):  # Initialize the XMLParser class
        self.file_path = file_path  # Set the file path
        self.tree = None    # Initialize the tree variable
        self.products = None  # Initialize the products variable
        self.products_list = [] # Initialize the products list
    
    def parse(self):
        try:
            self.tree = ET.parse(self.file_path)
            self.products = self.tree.findall(".//Product")

            for p in self.products:
                images = [img.get("Path") for img in p.findall("./Images/Image")]
                details = {detail.get("Name"): detail.get("Value") for detail in p.findall("./ProductDetails/ProductDetail")}
                

                # Extracting specific details
                description_cdata = p.find("Description").text
                fabric_info = self.extract_info(description_cdata, "Kumaş Bilgisi")     # Extract the fabric information
                model_measurements = self.extract_info(description_cdata, "Model Ölçüleri")     # Extract the model measurements
                product_measurements = self.extract_info(description_cdata, "Ürün Ölçüleri")       # Extract the product measurements

                product_data = {
                    "stock_code": p.get("ProductId"),
                    "color": [details.get("Color")],
                    "discounted_price": float(details.get("DiscountedPrice").replace(",", ".")) if details.get("DiscountedPrice") else None,
                    "images": images,
                    "is_discounted": details.get("DiscountedPrice") is not None and float(details.get("DiscountedPrice").replace(",", ".")) < float(details.get("Price").replace(",", ".")),
                    "name": p.get("Name"),
                    "price": float(details.get("Price").replace(",", ".")),
                    "price_unit": "USD",  # Assuming this is constant
                    "product_type": details.get("ProductType"),
                    "quantity": int(details.get("Quantity")),
                    "sample_size": None,  # Will get this from the XML later
                    "series": details.get("Series"),
                    "status": "Active",  # Assuming this is constant
                    "fabric": fabric_info,  # Will get this from the XML later
                    "model_measurements": model_measurements,  # Will get this from the XML later
                    "product_measurements": product_measurements,  # Will get this from the XML later
                    "createdAt": None,  # Will get this from the XML later
                    "updatedAt": None   # Will get this from the XML later
                }
                self.products_list.append(product_data)

            return self.products_list
        except ET.ParseError:
            print("Error parsing XML file")
            return None
        
    def extract_info(self, text, info_type): # Extract the information from the description
        pattern = rf"<strong>{info_type}:</strong>(.*?)<"   # Define the pattern to search for
        match = re.search(pattern, text)    # Search for the pattern in the description
        return match.group(1).strip() if match else None    # Return the extracted information if found, otherwise return None

    

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