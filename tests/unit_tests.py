import unittest
import tempfile
import os
import sys
sys.path.append('../')
import parser

class TestParser(unittest.TestCase):
    # Create temporary test files before each test
    def setUp(self):
        self.lookup_file = tempfile.NamedTemporaryFile(delete=False, mode='w')
        self.lookup_file.write("dstport,protocol,tag\n")
        self.lookup_file.write("443,tcp,https\n")
        self.lookup_file.write("80,tcp,http\n")
        self.lookup_file.write("23,tcp,telnet\n")
        self.lookup_file.close()

        self.protocol_file = tempfile.NamedTemporaryFile(delete=False, mode='w')
        self.protocol_file.write("Decimal,Keyword,Protocol,IPv6 Extension Header,Reference\n")
        self.protocol_file.write("6,TCP,Transmission Control,,[RFC9293]\n")
        self.protocol_file.write("17,UDP,User Datagram,,[RFC768][Jon_Postel]\n")
        self.protocol_file.close()

        self.flow_log_file = tempfile.NamedTemporaryFile(delete=False, mode='w')
        self.flow_log_file.write("2 123456789012 eni-0a1b2c3d 10.0.1.201 198.51.100.2 49153 443 6 25 20000 1620140761 1620140821 ACCEPT OK\n")
        self.flow_log_file.write("2 123456789012 eni-0a1b2c3d 10.0.1.201 198.51.100.2 49153 80 6 25 20000 1620140761 1620140821 ACCEPT OK\n")
        self.flow_log_file.write("2 123456789012 eni-0a1b2c3d 10.0.1.201 198.51.100.2 49153 80 6 25 20000 1620140761 1620140821 ACCEPT OK\n")
        self.flow_log_file.write("2 123456789012 eni-0a1b2c3d 10.0.1.201 198.51.100.2 49153 80 6 25 20000 1620140761 1620140821 ACCEPT OK\n")
        self.flow_log_file.write("2 123456789012 eni-0a1b2c3d 10.0.1.201 198.51.100.2 49153 23 6 25 20000 1620140761 1620140821 ACCEPT OK\n")
        self.flow_log_file.write("2 123456789012 eni-0a1b2c3d 10.0.1.201 198.51.100.2 49153 80 6 25 20000 1620140761 1620140821 ACCEPT OK\n")
        self.flow_log_file.write("2 123456789012 eni-0a1b2c3d 10.0.1.201 198.51.100.2 49153 443 6 25 20000 1620140761 1620140821 ACCEPT OK\n")
        self.flow_log_file.close()

    def tearDown(self):
        os.unlink(self.lookup_file.name)
        os.unlink(self.protocol_file.name)
        os.unlink(self.flow_log_file.name)

    def test_load_lookup_table(self):
        lookup = parser.load_lookup_table(self.lookup_file.name)
        self.assertEqual(lookup.get(('443', 'tcp')), 'https')
        self.assertEqual(lookup.get(('80', 'tcp')), 'http')
        self.assertEqual(lookup.get(('23', 'tcp')), 'telnet')

    def test_load_protocol_map(self):
        protocol_map = parser.load_protocol_map(self.protocol_file.name)
        self.assertEqual(protocol_map.get('6'), 'tcp')
        self.assertEqual(protocol_map.get('17'), 'udp')

    def test_process_flow_logs(self):
        lookup = parser.load_lookup_table(self.lookup_file.name)
        protocol_map = parser.load_protocol_map(self.protocol_file.name)
        tag_counts, port_protocol_counts = parser.process_flow_logs(self.flow_log_file.name, lookup, protocol_map)

        self.assertEqual(tag_counts.get('https'), 2)
        self.assertEqual(tag_counts.get('http'), 4)
        self.assertEqual(tag_counts.get('telnet'), 1)
        self.assertEqual(port_protocol_counts.get(('443', 'tcp')), 2)
        self.assertEqual(port_protocol_counts.get(('80', 'tcp')), 4)
        self.assertEqual(port_protocol_counts.get(('23', 'tcp')), 1)

    def test_write_tag_counts(self):
        tag_counts = {'https': 2, 'http': 4, 'telnet': 1}
        output_file = tempfile.NamedTemporaryFile(delete=False, mode='w')
        output_file.close()
        
        parser.write_tag_counts(tag_counts, output_file.name)

        with open(output_file.name, 'r') as file:
            lines = file.readlines()
            self.assertEqual(lines[1].strip(), 'https,2')
            self.assertEqual(lines[2].strip(), 'http,4')
            self.assertEqual(lines[3].strip(), 'telnet,1')
        
        os.unlink(output_file.name)

    def test_write_port_protocol_counts(self):
        port_protocol_counts = {('443', 'tcp'): 2, ('80', 'tcp'): 4, ('23', 'tcp'): 1}
        output_file = tempfile.NamedTemporaryFile(delete=False, mode='w')
        output_file.close()

        parser.write_port_protocol_counts(port_protocol_counts, output_file.name)

        with open(output_file.name, 'r') as file:
            lines = file.readlines()
            self.assertEqual(lines[1].strip(), '443,tcp,2')
            self.assertEqual(lines[2].strip(), '80,tcp,4')
            self.assertEqual(lines[3].strip(), '23,tcp,1')
        
        os.unlink(output_file.name)

    def test_lookup_table_file_not_found(self):
        with self.assertRaises(FileNotFoundError):
            parser.load_lookup_table("non_existent_lookup.csv")

    def test_protocol_map_file_not_found(self):
        with self.assertRaises(FileNotFoundError):
            parser.load_protocol_map("non_existent_protocol_map.csv")

    def test_load_flow_logs_file_not_found(self):
        lookup = parser.load_lookup_table(self.lookup_file.name)
        protocol_map = parser.load_protocol_map(self.protocol_file.name)
        with self.assertRaises(FileNotFoundError):
            parser.process_flow_logs("non_existent_flow_logs.txt", lookup, protocol_map)

if __name__ == '__main__':
    unittest.main()
