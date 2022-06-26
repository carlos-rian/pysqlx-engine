import logging
import sys

from binary import check_binary

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

print(check_binary())
print(check_binary())
print(check_binary())
