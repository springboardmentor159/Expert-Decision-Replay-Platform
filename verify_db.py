#!/usr/bin/env python
"""Verify database changes in PostgreSQL"""

from sqlalchemy import create_engine, text
from app.core.config import settings

# Create database engine
engine = create_engine(settings.database_url)

print("=" * 80)
print("PostgreSQL Database Verification - Decision Management")
print("=" * 80)

with engine.connect() as conn:
    # Query the decisions table
    print("\n1. Checking Decisions Table Schema:")
    print("-" * 80)
    result = conn.execute(text("""
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns
        WHERE table_name = 'decisions'
        ORDER BY ordinal_position
    """))
    for row in result:
        print(f"  {row[0]:20} | {row[1]:15} | Nullable: {row[2]:5} | Default: {row[3]}")
    
    # Query the most recent decisions
    print("\n2. Recent Decisions in Database:")
    print("-" * 80)
    result = conn.execute(text("""
        SELECT id, title, status, category, created_by, created_at, updated_at
        FROM decisions
        ORDER BY created_at DESC
        LIMIT 5
    """))
    for row in result:
        print(f"\n  ID: {row[0]}")
        print(f"  Title: {row[1]}")
        print(f"  Status: {row[2]}")
        print(f"  Category: {row[3]}")
        print(f"  Created By: {row[4]}")
        print(f"  Created At: {row[5]}")
        print(f"  Updated At: {row[6]}")
    
    # Verify status values
    print("\n3. Unique Status Values in Database:")
    print("-" * 80)
    result = conn.execute(text("""
        SELECT DISTINCT status, COUNT(*) as count
        FROM decisions
        GROUP BY status
        ORDER BY status
    """))
    for row in result:
        print(f"  {row[0]:20} : {row[1]} decisions")
    
    # Verify category values
    print("\n4. Unique Category Values in Database:")
    print("-" * 80)
    result = conn.execute(text("""
        SELECT DISTINCT category, COUNT(*) as count
        FROM decisions
        GROUP BY category
        ORDER BY category
    """))
    for row in result:
        print(f"  {row[0]:20} : {row[1]} decisions")
    
    # Verify created_by and created_at are NOT NULL
    print("\n5. Data Integrity Checks:")
    print("-" * 80)
    result = conn.execute(text("""
        SELECT 
            COUNT(*) as total,
            COUNT(created_by) as has_created_by,
            COUNT(created_at) as has_created_at,
            COUNT(updated_at) as has_updated_at
        FROM decisions
    """))
    for row in result:
        print(f"  Total decisions: {row[0]}")
        print(f"  Decisions with created_by: {row[1]} (should be {row[0]})")
        print(f"  Decisions with created_at: {row[2]} (should be {row[0]})")
        print(f"  Decisions with updated_at: {row[3]} (should be {row[0]})")
        if row[0] == row[1] == row[2] == row[3]:
            print("  ✓ All data integrity checks passed")
        else:
            print("  ✗ Data integrity issue detected")
    
    # Verify that updated_at changes when decision is updated
    print("\n6. Verify Updated Timestamp Changes:")
    print("-" * 80)
    result = conn.execute(text("""
        SELECT id, title, created_at, updated_at,
               (updated_at > created_at) as timestamp_changed
        FROM decisions
        WHERE id IN (4, 5)
        ORDER BY id
    """))
    for row in result:
        print(f"  ID {row[0]}: '{row[1]}'")
        print(f"    Created: {row[2]}")
        print(f"    Updated: {row[3]}")
        print(f"    Changed: {'Yes ✓' if row[4] else 'No'}")

print("\n" + "=" * 80)
print("✓ PostgreSQL Verification Complete")
print("=" * 80)
