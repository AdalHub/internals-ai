
from pymongo.mongo_client import MongoClient    
from pymongo.server_api import ServerApi    
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv("../../.env")
mongodb_username=os.getenv('MONGO_DB_USERNAME')
mongodb_password=os.getenv('MONGO_DB_PASSWORD')

uri =f"mongodb+srv://{mongodb_username}:{mongodb_password}@internal-ai.wmzdete.mongodb.net/?appName=internal-ai"


# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)



#automatically create a new db
db =client.internals_ai_db



#creating users collection
users_collection= db.users




user_test = {
    "name": "jose",
    "age":53,
    "access_level": "admin",
    "created_at": datetime.now()
}
result=users_collection.insert_one(user_test)
print(f"result from test user insert: {result.inserted_id}")

multiple_users = [
    {
        "name": "justin",
        "age":25,
        "access_level": "user",
        "created_at": datetime.now()
    },
    {
        "name": "sam",
        "age":25,
        "access_level": "user",
        "created_at": datetime.now()
    },
    {
        "name": "alex",
        "age":24,
        "access_level": "user",
        "created_at": datetime.now()
    },
]

result_1= users_collection.insert_many(multiple_users)
print(f"successfully inserted this many test users: {len(result_1.inserted_ids)}")

#listing database names
print(client.list_database_names())

#print all users
print("===ALL USERS===")
for user in users_collection.find():
    print(user)

#find a single docutment
print("===Finding a specific user/doc===")
user = users_collection.find_one({"name":"justin"})
print(user)

# Find one document
print("\n=== Find One ===")
user = users_collection.find_one({"name": "John Doe"})
print(user)

# Find with filter
print("\n=== Users older than 27 ===")
for user in users_collection.find({"age": {"$gt": 27}}):
    print(user)

# Find with projection (select specific fields)
print("\n=== Names and Emails only ===")
for user in users_collection.find({}, {"name": 1, "email": 1, "_id": 0}):
    print(user)

# Sorting
print("\n=== Sorted by age (descending) ===")
for user in users_collection.find().sort("age", -1):  # -1 = descending, 1 = ascending
    print(user)

# Limit results
print("\n=== First 2 users ===")
for user in users_collection.find().limit(2):
    print(user)

# Count documents
count = users_collection.count_documents({"age": {"$gte": 30}})
print(f"\nUsers 30 or older: {count}")

# ============================================
# 5. UPDATE Documents
# ============================================

# Update one document
users_collection.update_one(
    {"name": "John Doe"},  # Filter
    {"$set": {"age": 31, "city": "New York"}}  # Update
)
print("\nUpdated John's age and added city")

# Update multiple documents
users_collection.update_many(
    {"age": {"$lt": 30}},  # All users under 30
    {"$set": {"status": "young"}}
)
print("Added 'young' status to users under 30")

# Increment a value
users_collection.update_one(
    {"name": "Jane Smith"},
    {"$inc": {"age": 1}}  # Increment age by 1
)

# Add to array field
users_collection.update_one(
    {"name": "Bob Johnson"},
    {"$push": {"hobbies": "reading"}}  # Add to array
)

# Remove a field
users_collection.update_one(
    {"name": "Alice Williams"},
    {"$unset": {"status": ""}}  # Remove the 'status' field
)

# ============================================
# 6. DELETE Documents
# ============================================

# Delete one document
result = users_collection.delete_one({"name": "Test User"})
print(f"\nDeleted {result.deleted_count} document(s)")

# Delete multiple documents
result = users_collection.delete_many({"age": {"$lt": 25}})
print(f"Deleted {result.deleted_count} document(s) under age 25")

# ============================================
# 7. USEFUL QUERY OPERATORS
# ============================================

# Comparison operators
examples = {
    "$eq": "equal to",
    "$ne": "not equal to",
    "$gt": "greater than",
    "$gte": "greater than or equal",
    "$lt": "less than",
    "$lte": "less than or equal",
    "$in": "in array",
    "$nin": "not in array"
}

# Example: Find users with age 25, 30, or 35
users_collection.find({"age": {"$in": [25, 30, 35]}})

# Logical operators
users_collection.find({
    "$and": [
        {"age": {"$gte": 25}},
        {"age": {"$lte": 35}}
    ]
})

users_collection.find({
    "$or": [
        {"name": "John Doe"},
        {"email": "jane@example.com"}
    ]
})

# ============================================
# 8. INDEXES (for performance)
# ============================================

# Create an index on email for faster queries
users_collection.create_index("email", unique=True)

# Create compound index
users_collection.create_index([("name", 1), ("age", -1)])

# List indexes
print("\nIndexes:", users_collection.list_indexes())

# ============================================
# 9. AGGREGATION (Advanced queries)
# ============================================

# Group by and count
pipeline = [
    {"$group": {
        "_id": "$age",
        "count": {"$sum": 1}
    }},
    {"$sort": {"count": -1}}
]
results = users_collection.aggregate(pipeline)
print("\n=== Users grouped by age ===")
for result in results:
    print(result)

# ============================================
# 10. BEST PRACTICES
# ============================================

# Always close the connection when done
# client.close()  # Uncomment when you're finished


# Safe upsert (update if exists, insert if not)
users_collection.update_one(
    {"email": "john@example.com"},
    {"$set": {"name": "John Doe", "age": 30}},
    upsert=True
)

# Find and modify in one operation
updated_user = users_collection.find_one_and_update(
    {"name": "John Doe"},
    {"$inc": {"age": 1}},
    return_document=True  # Return the updated document
)

# Bulk operations for better performance
from pymongo import InsertOne, UpdateOne, DeleteOne

requests = [
    InsertOne({"name": "User1"}),
    UpdateOne({"name": "User2"}, {"$set": {"age": 25}}),
    DeleteOne({"name": "User3"})
]
result = users_collection.bulk_write(requests)