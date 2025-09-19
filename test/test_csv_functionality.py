#!/usr/bin/env python3
"""
Test script to verify the new CSV functionality in RapidAPI Mode
"""

import sys
import os
import csv
import re
from datetime import datetime
from typing import List, Dict

def extract_terabox_links(text: str) -> List[str]:
    """Extract all TeraBox/TeraShare links from text"""
    # Pattern to match various TeraBox link formats
    patterns = [
        r'https://terasharelink\.com/s/[A-Za-z0-9_-]+',
        r'https://www\.terabox\.app/sharing/link\?surl=[A-Za-z0-9_-]+',
        r'https://terabox\.com/s/[A-Za-z0-9_-]+',
        r'https://1024terabox\.com/s/[A-Za-z0-9_-]+',
        r'https://www\.terabox\.com/sharing/link\?surl=[A-Za-z0-9_-]+',
        r'https://teraboxapp\.com/s/[A-Za-z0-9_-]+',
        r'https://1024tera\.com/s/[A-Za-z0-9_-]+',
        r'https://www\.1024tera\.com/s/[A-Za-z0-9_-]+',
        r'https://terabox\.app/s/[A-Za-z0-9_-]+',
        r'https://www\.terabox\.app/s/[A-Za-z0-9_-]+'
    ]
    
    all_links = []
    for pattern in patterns:
        links = re.findall(pattern, text, re.IGNORECASE)
        all_links.extend(links)
    
    # Remove duplicates while preserving order
    unique_links = []
    seen = set()
    for link in all_links:
        if link not in seen:
            unique_links.append(link)
            seen.add(link)
    
    return unique_links

def save_links_to_csv(links: List[str], csv_path: str = "utils/terebox.csv") -> bool:
    """Save extracted TeraBox links to CSV file"""
    try:
        # Ensure the directory exists
        dir_path = os.path.dirname(csv_path)
        if dir_path:  # Only create directory if path has a directory component
            os.makedirs(dir_path, exist_ok=True)
        
        # Prepare data for CSV
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Read existing data if file exists
        existing_links = set()
        if os.path.exists(csv_path):
            try:
                with open(csv_path, 'r', newline='', encoding='utf-8') as file:
                    reader = csv.DictReader(file)
                    for row in reader:
                        existing_links.add(row.get('Link', ''))
            except Exception:
                pass  # If file is corrupted or empty, start fresh
        
        # Prepare new data
        new_rows = []
        for i, link in enumerate(links, 1):
            if link not in existing_links:  # Only add new links
                # Extract SURL from link for easier identification
                surl = link.split('/')[-1] if '/' in link else link
                domain = link.split('/')[2] if '/' in link else 'Unknown'
                
                new_rows.append({
                    'ID': len(existing_links) + len(new_rows) + 1,
                    'Link': link,
                    'SURL': surl,
                    'Domain': domain,
                    'Extracted_At': timestamp,
                    'Status': 'Pending',
                    'Processed': 'No'
                })
        
        # Write to CSV
        file_exists = os.path.exists(csv_path) and os.path.getsize(csv_path) > 0
        
        with open(csv_path, 'a', newline='', encoding='utf-8') as file:
            fieldnames = ['ID', 'Link', 'SURL', 'Domain', 'Extracted_At', 'Status', 'Processed']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            
            # Write header if file is new or empty
            if not file_exists:
                writer.writeheader()
            
            # Write new rows
            writer.writerows(new_rows)
        
        return True
    except Exception as e:
        print(f"❌ Error saving to CSV: {str(e)}")
        return False

def load_links_from_csv(csv_path: str = "utils/terebox.csv") -> List[Dict]:
    """Load TeraBox links from CSV file"""
    try:
        if not os.path.exists(csv_path):
            return []
        
        links_data = []
        with open(csv_path, 'r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                links_data.append(dict(row))
        
        return links_data
    except Exception as e:
        print(f"❌ Error loading from CSV: {str(e)}")
        return []

def test_csv_functionality():
    """Test the CSV functionality with sample data"""
    
    print("🧪 Testing CSV Functionality for TeraBox Links")
    print("=" * 50)
    
    # Test data - sample text with TeraBox links
    sample_text = """
    Here are some TeraBox links to test:
    Video 1 👉 https://terasharelink.com/s/1FQd8x4-bpyTN8TnV6APOLA
    Document 👉 https://www.terabox.app/sharing/link?surl=ABC123DEF456
    Another file 👉 https://terabox.com/s/sample_link_123
    Music 👉 https://1024terabox.com/s/music_file_xyz
    """
    
    print("📝 Sample text:")
    print(sample_text)
    print("\n" + "=" * 50)
    
    # Test 1: Extract links
    print("🔍 Step 1: Extracting TeraBox links...")
    extracted_links = extract_terabox_links(sample_text)
    print(f"✅ Found {len(extracted_links)} links:")
    for i, link in enumerate(extracted_links, 1):
        print(f"   {i}. {link}")
    
    print("\n" + "=" * 50)
    
    # Test 2: Save to CSV
    print("💾 Step 2: Saving links to CSV...")
    csv_path = "test_terebox.csv"
    success = save_links_to_csv(extracted_links, csv_path)
    
    if success:
        print("✅ Links saved successfully!")
        
        # Check if file exists
        if os.path.exists(csv_path):
            print(f"📁 CSV file created: {csv_path}")
            
            # Show file size
            file_size = os.path.getsize(csv_path)
            print(f"📏 File size: {file_size} bytes")
        else:
            print("❌ CSV file not found!")
    else:
        print("❌ Failed to save links!")
        return False
    
    print("\n" + "=" * 50)
    
    # Test 3: Load from CSV
    print("📊 Step 3: Loading links from CSV...")
    loaded_data = load_links_from_csv(csv_path)
    
    if loaded_data:
        print(f"✅ Loaded {len(loaded_data)} entries from CSV:")
        for entry in loaded_data:
            print(f"   ID: {entry.get('ID')}, SURL: {entry.get('SURL')}, Domain: {entry.get('Domain')}")
    else:
        print("❌ Failed to load links from CSV!")
        return False
    
    print("\n" + "=" * 50)
    
    # Test 4: Test duplicate handling
    print("🔄 Step 4: Testing duplicate link handling...")
    # Try to save the same links again
    success2 = save_links_to_csv(extracted_links, csv_path)
    
    if success2:
        # Load again to check if duplicates were avoided
        loaded_data2 = load_links_from_csv(csv_path)
        if len(loaded_data2) == len(loaded_data):
            print("✅ Duplicate handling works - no new entries added")
        else:
            print(f"⚠️ Expected {len(loaded_data)} entries, got {len(loaded_data2)}")
    
    print("\n" + "=" * 50)
    
    # Cleanup
    print("🧹 Cleanup: Removing test file...")
    try:
        os.remove(csv_path)
        print("✅ Test file removed")
    except:
        print("⚠️ Could not remove test file")
    
    print("\n🎉 CSV functionality test completed!")
    return True

if __name__ == "__main__":
    try:
        test_csv_functionality()
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
