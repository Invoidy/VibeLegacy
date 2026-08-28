test_response = """I'll update the default port in main.py from 5000 to 8080.

File: 123/123
<<<<<<< SEARCH
DEFAULT_PORT = 5000
=======
DEFAULT_PORT = 8080
>>>>>>> REPLACE

File: 123/xd.txt
<<<<<<< SEARCH
DEFAULT_PORT = 5000
=======
DEFAULT_PORT = 8080
>>>>>>> REPLACE

Done — DEFAULT_PORT is now 8080 in main.py. Note: make sure nothing else on your machine is already using port 8080.
"""