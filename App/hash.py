import hashlib

# Data to be hashed
data = "Mhw630@alumni.ku.dk"

# Creating a hash object using SHA-256 algorithm
hash_object = hashlib.sha256()

# Encoding the data before hashing (SHA-256 works with bytes-like objects)
data_bytes = data.encode('utf-8')

# Updating the hash object with the data
hash_object.update(data_bytes)

# Obtaining the hashed value in hexadecimal format
hashed_data = hash_object.hexdigest()

print("Hashed value:", hashed_data)


#Dagholdet = 1df52b58de10dba53600c9230d50f6727661d2cbd7cae22049bef8e509d3277e
#Aftenholdet = 8a1162ca6bdf68dafd236a5f2acf8a33b144cc9ca67d2bcf0d59ddba125d6a5c
#Natholdet = a25c56aa35c63e9b8bfa8972c8f33097957a8985ccc863d9b1da206e6d154f8c

#Bxz911@alumni.ku.dk = 97927c4ecddc4d517037b5d83f2b8e46e68d1da2560bf0c75e26912619888d1f
#Hjg708@alumni.ku.dk = 619242b2652f336fd0e3b20ddab175535bf986503a4a5c14a0e9efb21bc58195
#Mhw630@alumni.ku.dk = c6660fabe0670cf8bad3d3b884de1ccf5531431edaefcf7a1e8cb212d5687299