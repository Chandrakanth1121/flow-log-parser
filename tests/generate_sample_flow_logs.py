import random
import time
import csv

FLOW_LOG_FILE = "../log-samples/flow_logs_10MB.txt"
MAX_FILE_SIZE = 10 * 1024 * 1024

with open('../maps/protocol_mapping.csv', 'r') as protocol_maps:
  reader = csv.DictReader(protocol_maps)
  data = {}
  for row in reader:
    for header, value in row.items():
      try:
        data[header].append(value)
      except KeyError:
        data[header] = [value]

PROTOCOLS = data['Decimal']

# Generate a random log entry
def generate_log_entry():
    version = 2
    account_id = 123456789012
    eni = f"eni-{random.randint(10000000, 99999999)}"
    src_addr = f"{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 255)}"
    dst_addr = f"{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 255)}"
    dst_port = random.randint(0,1023)
    src_port = random.randint(1024, 65535)
    protocol = random.choice(PROTOCOLS)
    packets = random.randint(1, 25)
    bytes_transferred = packets * random.randint(50, 1500)
    start_time = int(time.time())
    end_time = start_time + random.randint(1, 100)
    action = random.choice(["ACCEPT", "REJECT"])
    status = "OK"
    return f"{version} {account_id} {eni} {src_addr} {dst_addr} {dst_port} {src_port} {protocol} {packets} {bytes_transferred} {start_time} {end_time} {action} {status}\n"

# Generate and write flow log data to file
with open(FLOW_LOG_FILE, "w") as f:
    FILE_SIZE  = 0
    while FILE_SIZE <= MAX_FILE_SIZE:
        dummy_log = generate_log_entry()
        FILE_SIZE += len(dummy_log.encode('utf-8'))
        f.write(generate_log_entry())
