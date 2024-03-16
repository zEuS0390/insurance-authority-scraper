# Import necessary modules and functions
from modules.utils.details_utils import saveCSV  # Import custom function for saving data as CSV
from configparser import ConfigParser  # Import ConfigParser for reading configuration
from argparse import ArgumentParser  # Import ArgumentParser for command-line argument parsing
import logging, pymongo, json, os
from bson.json_util import dumps

# Initialize logger configuration
logger = logging.getLogger(__name__)
logging.basicConfig(format="%(asctime)s [%(levelname)s] --- %(message)s", level=logging.INFO)

# Read configuration from config.cfg file
cfg = ConfigParser()
cfg.read("config.cfg")

# Creat ArgumentParser instance
argparse = ArgumentParser()
argparse.add_argument("-t", "--type", type=str, default='csv', help="specify the output type (use 'csv' or 'json')")
argparse.add_argument("-d", "--output-dir", type=str, default=cfg.get("output", "data_dir"), help='specify the output directory')

if __name__=="__main__":

	# Parse command-line arguments
	args = argparse.parse_args() 

	# Check if the specified output type is valid
	if args.type not in ['csv', 'json']: 
		logger.error("invalid output type specified. please use 'csv' or 'json'.")

	else:
		# Create MongoDB client and access database
		client = pymongo.MongoClient(cfg.get('mongodb', 'uri'))  
		db = client[cfg.get('mongodb', 'db_name')]  

		# Iterate over collections in the database
		for collect_name in db.list_collection_names():  
			collection = db[collect_name]  # Access collection
			bson_data = collection.find({})  # Retrieve data from collection
			dict_obj = json.loads(dumps(bson_data))  # Convert BSON data to dictionary

			# Check if output type is CSV
			if args.type == 'csv':
				logger.info(f"generating csv files for '{collect_name}'")

				for item in dict_obj:
						saveCSV(item, os.path.join(args.output_dir, collect_name)) # Save data as CSV file

			# Check if output type is JSON
			elif args.type == 'json': 
				logger.info(f"generating json file for '{collect_name}'")

				# Construct the output directory path by joining the specified output directory, collection name, and json directory
				output_dir = os.path.join(args.output_dir, collect_name, "json")

				# Check if the output directory path does not exist; if not, create it recursively
				if not os.path.exists(output_dir):
						os.makedirs(output_dir)

				# Open a file with write ('w') mode and UTF-8 encoding to save the JSON data
				with open(os.path.join(output_dir, f'{collect_name}.json'), 'w', encoding='utf-8') as file:
						# Dump the dictionary object (dict_obj) to the file in JSON format, with indentation for readability
						json.dump(dict_obj, file, indent=4)
