# FLow Log Parser
This program parses AWS VPC flow logs and maps each entry to a tag based on a lookup table. The program generates two reports:

* **Tag Counts:** The count of occurrences of each tag based on destination port and protocol.
* **Port/Protocol Combination Counts:** The count of occurrences for each (dstport, protocol) combination.
---
### Assumptions:
* The program only supports default log format and version 2 of AWS VPC flow logs.
* The lookup table contains three columns: dstport, protocol, and tag, and is stored as a CSV file.
* The flow log file size can be up to 10 MB.
* The lookup table can have up to 10,000 mappings.
* Tags can map to more than one port-protocol combination.
* Case-insensitive matching is applied to protocol and tag names.
* If no match is found for a (dstport, protocol), the entry is labeled as "Untagged".
* Protocol numbers can be mapped to names based on (https://www.iana.org/assignments/protocol-numbers/protocol-numbers.xhtml).
* Improper logs(logs with less than 14 fields) are skipped.
---
### Instructions to run the script:
#### Requirements:
* Python 3.13.2 and above
#### Steps:
1. Clone the repo
```
git clone https://github.com/Chandrakanth1121/flow-log-parser.git
cd flow-log-parser
```

2. Run unit tests to make sure everything is working as expected. All 8 tests should pass
```
python3 -m unittest ./tests/unit_tests.py
```

3. Execute the script
```
python3 parser.py
```
This script reads the lookup table from `./maps/lookup_table.csv`, protocol map from `./maps/protocol_mapping.csv`, flow log file from `./log-samples/flow_logs.txt`, create dictionaries for lookup table and protocol map and then iterate over all logs to count the tags based on port/protocol combination. It also simultaneously counts the combinations of port/protocols.

4. You wiil see the outputs in:

```
./outputs/tag_counts.csv
./outputs/port_protocol_counts.csv
```

5. The lookup file path, protocol map file path, flow log file path and output files are configured in `config.py`. This file can be changed to use custom files.
---
### Testing
#### Unit tests:
* Correct loading of lookup table.
* Correct loading of protocol map.
* Correct processing of flow logs.
* Handling of missing files.
* Proper generation of output files.
* Proper output format.
* Case insensitivity
* Test tag mapping to multiple port/protocol combinations
```
Ran 8 tests in 0.037s

OK
```
#### Stress tests:
* Wrote script to generate 10MB sample flow log file. (`./tests/generate_sample_flow_logs.py`)
* Wrote script to generate lookup table with 10000 mappings. (`./tests/generate_sample_lookup.py`)
* These generated files are stored in log-samples folder and maps folder respectively.
* The parsing script takes around 0.24 seconds to execute.
```
INFO:root:Time taken : 0.2375s
```
---
### Code Analysis
#### Features:
* Efficiency: The program efficiently processes logs using dictionary lookups for quick tagging.

* Modular Design: Each function performs a specific task, making it easy to maintain and extend.

* Case-Insensitive Matching: Ensures accurate mappings regardless of case variations.

* Comprehensive Testing: The unit tests cover various edge cases, including missing files and malformed data.

* Minimal Dependencies: Runs with just Python, avoiding external package requirements.
---
### Further Improvements
* Parallel Processing: The current implementation processes logs sequentially. Using multiple parallel systems can significantly improve performance on large datasets.

* Custom Log Format Support: Extending the parser to support additional flow log formats beyond the default AWS format 2.

* Database Integration: Storing processed log data in a database for easier querying and long-term analysis.

* Real-time Processing: 
    - The script can be deployed as a serverless application (e.g. AWS Lambda) to process VPC logs in real-time. 
    - AWS SQS or similar message queueing service can be used to stream the logs to this service.
    - The results can be stored in a database or served via an API, enabling users to retrieve log insights dynamically with API calls.
