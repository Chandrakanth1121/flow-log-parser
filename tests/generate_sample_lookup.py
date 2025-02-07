import random
import csv

LOOKUP_FILE = "lookup_10000.csv"

with open('../maps/protocol_mapping.csv', 'r') as protocol_maps:
  reader = csv.DictReader(protocol_maps)
  data = {}
  for row in reader:
    for header, value in row.items():
      try:
        data[header].append(value)
      except KeyError:
        data[header] = [value]

PROTOCOLS = data['Keyword']

# Generate and write lookup maps to file
with open(LOOKUP_FILE, "w") as f:
    f.write("dstport,protocol,tag\n")
    for _ in range(10000):
        dstport = f"{random.randint(0,1023)}"
        protocol = random.choice(PROTOCOLS)
        tag = f"sv_{random.randint(1,99)}"
        f.write(dstport + "," + protocol + "," + tag + "\n")
