import csv
import config
import logging
import time

logging.basicConfig(level=logging.DEBUG)

# Load the lookup table and create a dictionary with (dstport,protocol) as key to allow lookup in constant time
def load_lookup_table(lookup_file):
    lookup = {}

    logging.info(f"Loading lookup table from {lookup_file}")

    try:
        with open(lookup_file, 'r') as file:
            reader = csv.reader(file)
            next(reader)  # Skip csv file header
            for row in reader:
                dstport, protocol, tag = row
                lookup[(dstport.strip(), protocol.strip().lower())] = tag.strip().lower()  # convert all attributes to same case for case insensitive matching
    except FileNotFoundError:
        logging.error(f"{lookup_file} file not found")
        raise
    return lookup

# Load the protocol mapping csv and create a dictionary to map internet protocol numbers to names
def load_protocol_map(protocol_file):
    protocol_map = {}

    logging.info(f"Loading protocol mapping table from {protocol_file}")
    
    try:
        with open(protocol_file, 'r') as file:
            reader = csv.reader(file)
            next(reader)  # Skip header
            for row in reader:
                protocol_num, protocol_name, _, _, _ = row
                protocol_map[protocol_num.strip()] = protocol_name.strip().lower()  # convert protocol name to lowercase for case insensitive matching
    except FileNotFoundError:
        logging.error(f"{protocol_file} file not found")
        raise

    return protocol_map

# Parse the flow log file and count tags and port,protocol combinations based on maps
def process_flow_logs(flow_log_file, lookup, protocol_map):
    tag_counts = {}  # Dictionary to store count of the occurences of tags
    port_protocol_counts = {}  # Dictionary to store the count of occurences of port-protocol combinations

    logging.info(f"Processing flow logs from {flow_log_file}")
    
    try:
        with open(flow_log_file, 'r') as file:
            for line in file:
                parts = line.strip().split()
                if len(parts) < 14:
                    logging.warning(f"Less than 14 fields in the log entry. Skipping")
                    continue  # Skip invalid lines
                
                dstport, protocol_num = parts[6], parts[7]
                protocol = protocol_map.get(protocol_num, protocol_num)  # Convert number to protocol name if possible
                key = (dstport, protocol.lower())
                tag = lookup.get(key, 'untagged')
                
                tag_counts[tag] = tag_counts.get(tag,0) + 1
                port_protocol_counts[key] = port_protocol_counts.get(key,0) + 1
    except FileNotFoundError:
        logging.error(f"{flow_log_file} file not found")
        raise
    
    return tag_counts, port_protocol_counts

# Write the tag counts to a CSV file
def write_tag_counts(tag_counts, output_file):
    try:
        with open(output_file, 'w') as file:
            file.write("Tag,Count\n")
            for key, value in tag_counts.items():
                tag = key
                count = value
                file.write(f"{tag},{count}\n")
    except Exception as e:
        logging.error(f"Could not write tag counts to the {output_file} file: {e}")
        raise

# Write the port/protocol combination counts to a CSV file
def write_port_protocol_counts(port_protocol_counts, output_file):
    try:
        with open(output_file, 'w') as file:
            file.write("Port,Protocol,Count\n")
            for key, value in port_protocol_counts.items():
                (port, protocol) = key
                count = value
                file.write(f"{port},{protocol},{count}\n")
    except Exception as e:
        logging.error(f"Could not write port/protocol combination counts to the {output_file} file: {e}")
        raise

if __name__ == "__main__":
    start_time = time.time()
    lookup_table = load_lookup_table(config.LOOKUP_FILE)
    protocol_map = load_protocol_map(config.PROTOCOL_FILE)
    tag_counts, port_protocol_counts = process_flow_logs(config.FLOW_LOG_FILE, lookup_table, protocol_map)
    
    write_tag_counts(tag_counts, config.TAG_OUTPUT_FILE)
    write_port_protocol_counts(port_protocol_counts, config.PORT_PROTOCOL_OUTPUT_FILE)
    
    logging.info(f"Output saved to {config.TAG_OUTPUT_FILE} and {config.PORT_PROTOCOL_OUTPUT_FILE}")
    end_time = time.time()
    logging.info(f"Time taken : {round((end_time - start_time),4)}s")