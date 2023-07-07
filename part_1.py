# implementing a toy DNS resolver
# expected behavior:
# $ python3 resolve.py example.com
# 93.184.216.34

from dataclasses import dataclass
import dataclasses
import struct


# DNS queries have 2 parts: a header and a question

# First the DNS header consists of:
# a) query ID
# b) some flags (mostly ignored for poc)
# c) 4 counts telling you how many records to expect in DNS packet
    # num_questions
    # num_answers
    # num_authorities
    # num_additionals

@dataclass
class DNSHeader:
    id: int
    flags: int
    num_questions: int = 0
    num_answers: int = 0
    num_authorities: int = 0
    num_additionals: int = 0

# Next a DNS question has 3 fields:
# a) name (like example.com)
# b) type (like A)
# c) class (always the same)

@dataclass
class DNSQuestion:
    name: bytes
    # type() is function
    type_: int 
    # class is reserved
    class_: int

# Next these classes need to turn into byte strings
def header_to_bytes(header):
    fields = dataclasses.astuple(header)
    # there are 6 'H's because 6 fields from DNSHeader
    # the ! at the beginning is for big endian for network packets
    return struct.pack("!HHHHHH", *fields)

def question_to_bytes(question):
    return question.name + struct.pack("!HH", question.type_, question.class_)

# Encodes the domain name
# google.com -> b"\x06google\x03com\x00"
def encode_dns_name(domain_name):
    encoded = b""
    for part in domain_name.encode("ascii").split(b'.'):
        encoded += bytes([len(part)]) + part
        return encoded + b"\x00"

# Building the DNS Query
import random
random.seed(1)

TYPE_A = 1
CLASS_IN = 1

def build_query(domain_name, record_type):
    name = encode_dns_name(domain_name)
    id = random.randint(0, 65535)
    RECURSION_DESIRED = 1 << 8
    header = DNSHeader(id=id, num_questions=1, flags=RECURSION_DESIRED)
    question = DNSQuestion(name=name, type_=record_type, class_=CLASS_IN)
    return header_to_bytes(header) + question_to_bytes(question)

# time to test if this code works properly
import socket
query = build_query("www.example.com", 1)

# create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# send our query to 8.8.8.8, port 53 (DNS port)
sock.sendto(query, ("8.8.8.8", 53))

# read the respond. UDP DNS responses are typically < 512 bytes
response, _ = sock.recvfrom(1024)

# by running tcpdump we can see our program making its DNS query
print(response)











