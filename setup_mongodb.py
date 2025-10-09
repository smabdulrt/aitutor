#!/usr/bin/env python3
"""
MongoDB Setup Script

This script initializes the MongoDB database with skills template from JSON.
Run this once to migrate from JSON to MongoDB.

Usage:
    python3 setup_mongodb.py
"""

from db_config import mongodb
from mongo_skills_manager import mongo_skills

def main():
    print("=" * 60)
    print("MongoDB Setup Script for AI Tutor")
    print("=" * 60)
    print()

    # Check MongoDB connection
    if not mongodb.is_connected():
        print("❌ MongoDB is not connected!")
        print()
        print("Please ensure:")
        print("  1. MongoDB is running (mongod)")
        print("  2. .env file is configured with correct MONGODB_URI")
        print()
        print("For local MongoDB:")
        print("  MONGODB_URI=mongodb://localhost:27017/")
        print()
        return

    print("✅ MongoDB connection successful!")
    print(f"   Database: {mongodb.db.name}")
    print()

    # Initialize skills template
    print("Initializing skills template from JSON...")
    skills_json_path = "QuestionsBank/skills.json"

    success = mongo_skills.initialize_skills_template_from_json(skills_json_path)

    if success:
        print()
        print("=" * 60)
        print("✅ MongoDB setup complete!")
        print("=" * 60)
        print()
        print("Skills template has been loaded into MongoDB.")
        print("You can now run the AI Tutor with MongoDB storage.")
        print()
    else:
        print()
        print("❌ Failed to initialize MongoDB")
        print()
        print("Please check:")
        print("  1. skills.json file exists at:", skills_json_path)
        print("  2. JSON file is properly formatted")
        print("  3. MongoDB has write permissions")
        print()

if __name__ == "__main__":
    main()
