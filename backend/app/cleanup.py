from database import db
#EXECUTE THIS PROGRAM TO CLEAR OUT USERS
print("starting cleanup...")

#delete ALL users (safest for development)
result = db['users'].delete_many({})
print(f"deleted {result.deleted_count} user documents")

#drop all indexes
db['users'].drop_indexes()
print("Dropped all indexes")

print("\n Database cleaned! Now you can restart your app.")