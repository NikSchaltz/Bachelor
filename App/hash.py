import hashlib

# Data to be hashed
data = "Personale"

# Creating a hash object using SHA-256 algorithm
hash_object = hashlib.sha256()

# Encoding the data before hashing (SHA-256 works with bytes-like objects)
data_bytes = data.encode('utf-8')

# Updating the hash object with the data
hash_object.update(data_bytes)

# Obtaining the hashed value in hexadecimal format
hashed_data = hash_object.hexdigest()

print("Hashed value:", hashed_data)
