import hashlib

# Data to be hashed
data = "@alumni.ku.dk"

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
#Admin = c1c224b03cd9bc7b6a86d77f5dace40191766c485cd55dc48caf9ac873335d6f

#bxz911@alumni.ku.dk = ba503eb877b82b0726d94dd6bd5d948e76d58da9f8c0fff9343f1a6b5630a742
#hjg708@alumni.ku.dk = f2fbc59ba4c7010a79b83a964daa28015ef21ecf27f12faae62da3b211494537
#mhw630@alumni.ku.dk = 1eb4f018f04e6531be595fe765203383a3e4a146592a258a52d2d8030ca4a3da
#trp313@alumni.ku.dk = cd3c68d11179c4c2986aee27e8c7d9bd8391daf7d5140c8b070be0c2c0bb9cf6


