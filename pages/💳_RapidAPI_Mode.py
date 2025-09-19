"""
RapidAPI Mode Page - Commercial TeraBox Service Interface

This page provides access to the commercial RapidAPI TeraBox service, offering
professional-grade reliability and support for business applications.

Page Features:
- API key validation and management
- Single file processing with direct links
- Bulk file processing for multiple URLs
- Text processing to extract TeraBox links
- CSV database management for link collections
- Cache management and optimization
- Comprehensive testing and debugging tools

UI Architecture:
- Tab-based interface for organized functionality
- Real-time validation feedback
- Progress tracking for long operations
- Detailed error reporting and troubleshooting
- Browser integration for direct file access

State Management:
- Session state for API client persistence
- Validation status tracking
- Processing result caching
- User preference storage
"""

import streamlit as st
import time
import re
import csv
import os
import pandas as pd
from datetime import datetime
from utils.terabox_rapidapi import TeraBoxRapidAPI
from typing import Dict, Any, List
from utils.browser_utils import open_direct_file_link, display_browser_open_result, create_browser_selection_ui
from utils.terabox_config import get_config_manager
from utils.state_manager import StateManager, BatchStateUpdate
from utils.config import log_info, log_error
import json

def extract_terabox_links(text: str) -> List[str]:
    """
    Extract all TeraBox/TeraShare links from text using comprehensive pattern matching
    
    This function implements a robust link extraction system that can identify
    TeraBox links in various formats from any text input.
    
    Args:
        text: Input text containing potential TeraBox links
        
    Returns:
        List of unique TeraBox links found in the text
        
    Pattern Matching Strategy:
    - Multiple regex patterns for different TeraBox domains
    - Case-insensitive matching for flexibility
    - Support for both /s/ and ?surl= URL formats
    - Comprehensive domain coverage for all TeraBox variants
    
    Deduplication Algorithm:
    - Preserves original order of links
    - Removes exact duplicates
    - Uses set-based tracking for O(1) duplicate detection
    """
    log_info(f"Starting TeraBox link extraction from text - Length: {len(text)} characters")
    
    # Comprehensive TeraBox URL Patterns
    # Purpose: Match all known TeraBox domain and URL format variations
    # Strategy: Use specific regex patterns for each domain/format combination
    # Maintenance: Add new patterns as TeraBox introduces new domains
    # 
    # Pattern Categories:
    # 1. Official TeraBox domains (terabox.com, terabox.app)
    # 2. Mirror domains (1024terabox.com, 1024tera.com)
    # 3. Share link domains (terasharelink.com, terafileshare.com)
    # 4. Alternative domains (teraboxapp.com, freeterabox.com)
    patterns = [
        # Official TeraBox Domains
        r'https://www\.terabox\.app/sharing/link\?surl=[A-Za-z0-9_-]+',  # Official app sharing format
        r'https://terabox\.com/s/[A-Za-z0-9_-]+',  # Standard TeraBox short links
        r'https://www\.terabox\.com/sharing/link\?surl=[A-Za-z0-9_-]+',  # Official sharing links
        r'https://terabox\.app/s/[A-Za-z0-9_-]+',  # App domain short links
        r'https://www\.terabox\.app/s/[A-Za-z0-9_-]+',  # WWW app domain
        
        # Mirror and Alternative Domains
        r'https://1024terabox\.com/s/[A-Za-z0-9_-]+',  # 1024 TeraBox variant
        r'https://1024tera\.com/s/[A-Za-z0-9_-]+',  # 1024 Tera variant
        r'https://www\.1024tera\.com/s/[A-Za-z0-9_-]+',  # WWW 1024 Tera
        r'https://teraboxapp\.com/s/[A-Za-z0-9_-]+',  # App domain variant
        r'https://freeterabox\.com/s/[A-Za-z0-9_-]+',  # Free TeraBox variant
        r'https://nephobox\.com/s/[A-Za-z0-9_-]+',  # Nepho Box variant
        
        # Share Link Domains
        r'https://terasharelink\.com/s/[A-Za-z0-9_-]+',  # TeraShare link format
        r'https://terafileshare\.com/s/[A-Za-z0-9_-]+',  # TeraFile share format (NEW)
        r'https://www\.terafileshare\.com/s/[A-Za-z0-9_-]+',  # WWW TeraFile share (NEW)
        
        # Additional Variants (case-insensitive matching will handle variations)
        r'https://[a-zA-Z0-9.-]*terabox[a-zA-Z0-9.-]*/s/[A-Za-z0-9_-]+',  # Generic TeraBox pattern
        r'https://[a-zA-Z0-9.-]*terabox[a-zA-Z0-9.-]*/sharing/link\?surl=[A-Za-z0-9_-]+',  # Generic sharing pattern
    ]
    
    log_info(f"Using {len(patterns)} regex patterns for comprehensive link detection")
    
    # Text Preprocessing for Better Link Detection
    # Purpose: Clean text and prepare for pattern matching
    # Strategy: Handle Unicode, emojis, and formatting characters
    # Benefits: More reliable pattern matching, better link detection
    
    # Remove excessive whitespace and normalize line breaks
    cleaned_text = re.sub(r'\s+', ' ', text.strip())
    log_info(f"Text preprocessing - Original length: {len(text)}, Cleaned length: {len(cleaned_text)}")
    
    # Count emojis and special characters for analysis
    emoji_count = len(re.findall(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]', text))
    log_info(f"Text analysis - Emojis detected: {emoji_count}, Contains Unicode formatting: {any(ord(c) > 127 for c in text)}")
    
    # Pattern Matching Execution
    # Algorithm: Apply each pattern to find all matches
    # Strategy: Collect all matches first, then deduplicate and validate
    all_links = []
    pattern_stats = {}
    
    for i, pattern in enumerate(patterns):
        pattern_name = _get_pattern_description(pattern, i)
        log_info(f"Applying pattern {i+1}/{len(patterns)} ({pattern_name}): {pattern}")
        
        # Execute regex with case-insensitive matching
        pattern_start = time.time()
        links = re.findall(pattern, cleaned_text, re.IGNORECASE)
        pattern_duration = time.time() - pattern_start
        
        all_links.extend(links)
        pattern_stats[pattern_name] = {
            'matches': len(links),
            'duration_ms': round(pattern_duration * 1000, 2),
            'links': links[:3] if links else []  # Store first 3 for debugging
        }
        
        log_info(f"Pattern {i+1} ({pattern_name}) found {len(links)} links in {pattern_duration*1000:.2f}ms")
        
        # Log individual links found by this pattern
        for link in links:
            log_info(f"  Pattern {i+1} match: {link}")
    
    log_info(f"Pattern matching completed - Total links found: {len(all_links)}")
    log_info(f"Pattern statistics: {json.dumps(pattern_stats, indent=2)}")
    
    # Link Validation and Filtering
    # Purpose: Validate found links and filter out invalid ones
    # Strategy: Check link format, domain, and accessibility
    validated_links = []
    invalid_links = []
    
    for link in all_links:
        validation_result = _validate_terabox_link(link)
        if validation_result['valid']:
            validated_links.append(link)
            log_info(f"Link validated: {link} - Domain: {validation_result['domain']}")
        else:
            invalid_links.append(link)
            log_info(f"Link invalid: {link} - Reason: {validation_result['reason']}")
    
    log_info(f"Link validation completed - Valid: {len(validated_links)}, Invalid: {len(invalid_links)}")
    
    # Deduplication Algorithm
    # Purpose: Remove duplicate links while preserving order
    # Strategy: Use set for O(1) lookup, list for order preservation
    # Benefit: Maintains user's original link ordering
    unique_links = []
    seen = set()
    duplicate_count = 0
    
    for link in validated_links:
        if link not in seen:
            unique_links.append(link)
            seen.add(link)
            log_info(f"Added unique link: {link}")
        else:
            duplicate_count += 1
            log_info(f"Skipped duplicate link: {link}")
    
    # Final Statistics and Summary
    extraction_summary = {
        'total_patterns': len(patterns),
        'raw_matches': len(all_links),
        'validated_links': len(validated_links),
        'invalid_links': len(invalid_links),
        'unique_links': len(unique_links),
        'duplicates_removed': duplicate_count,
        'text_length': len(text),
        'emoji_count': emoji_count
    }
    
    log_info(f"Link extraction completed successfully")
    log_info(f"Extraction summary: {json.dumps(extraction_summary, indent=2)}")
    
    return unique_links

def _get_pattern_description(pattern: str, index: int) -> str:
    """
    Get human-readable description for regex pattern
    
    Args:
        pattern: Regex pattern string
        index: Pattern index for fallback naming
        
    Returns:
        Human-readable pattern description
    """
    # Pattern Description Mapping
    # Purpose: Provide clear names for debugging and logging
    pattern_descriptions = {
        'terasharelink': 'TeraShare Links',
        'terafileshare': 'TeraFile Share Links',
        'terabox\.app.*sharing': 'Official App Sharing',
        'terabox\.com.*sharing': 'Official Sharing Links',
        'terabox\.com/s': 'Standard Short Links',
        'terabox\.app/s': 'App Short Links',
        '1024terabox': '1024 TeraBox Mirror',
        '1024tera': '1024 Tera Mirror',
        'teraboxapp': 'TeraBox App Domain',
        'freeterabox': 'Free TeraBox Mirror',
        'nephobox': 'Nepho Box Mirror',
        'terabox.*s/': 'Generic TeraBox Pattern',
        'terabox.*sharing': 'Generic Sharing Pattern'
    }
    
    # Find matching description
    for key, description in pattern_descriptions.items():
        if key in pattern.lower():
            return description
    
    # Fallback to generic description
    return f"Pattern {index + 1}"

def _validate_terabox_link(link: str) -> Dict[str, Any]:
    """
    Validate TeraBox link format and domain
    
    Args:
        link: URL to validate
        
    Returns:
        Dict with validation result and details
        
    Validation Checks:
    1. URL format validation (proper HTTP/HTTPS)
    2. Domain validation (known TeraBox domains)
    3. Path validation (proper /s/ or sharing format)
    4. Parameter validation (surl format if applicable)
    """
    log_info(f"Validating TeraBox link: {link}")
    
    # Basic URL Format Validation
    if not link or not isinstance(link, str):
        return {'valid': False, 'reason': 'Empty or invalid link format', 'domain': None}
    
    # Protocol Validation
    if not link.lower().startswith(('http://', 'https://')):
        return {'valid': False, 'reason': 'Missing HTTP/HTTPS protocol', 'domain': None}
    
    # Extract Domain for Validation
    try:
        from urllib.parse import urlparse
        parsed = urlparse(link)
        domain = parsed.netloc.lower()
        log_info(f"Link validation - Domain extracted: {domain}")
    except Exception as e:
        log_error(e, "_validate_terabox_link")
        return {'valid': False, 'reason': 'Invalid URL format', 'domain': None}
    
    # Known TeraBox Domains
    # Purpose: Validate against known legitimate TeraBox domains
    # Security: Prevent processing of malicious or unrelated links
    valid_domains = [
        'terabox.com', 'www.terabox.com',
        'terabox.app', 'www.terabox.app', 
        '1024terabox.com', 'www.1024terabox.com',
        '1024tera.com', 'www.1024tera.com',
        'terasharelink.com', 'www.terasharelink.com',
        'terafileshare.com', 'www.terafileshare.com',  # NEW DOMAIN SUPPORT
        'teraboxapp.com', 'www.teraboxapp.com',
        'freeterabox.com', 'www.freeterabox.com',
        'nephobox.com', 'www.nephobox.com'
    ]
    
    # Domain Validation
    if domain not in valid_domains:
        log_info(f"Domain validation failed - {domain} not in valid domains list")
        return {'valid': False, 'reason': f'Unknown domain: {domain}', 'domain': domain}
    
    # Path Validation
    # Purpose: Ensure URL has proper TeraBox path structure
    path = parsed.path
    query = parsed.query
    
    # Valid path patterns
    valid_path_patterns = [
        r'/s/[A-Za-z0-9_-]+$',  # Short link format
        r'/sharing/link$'  # Sharing link format (with surl parameter)
    ]
    
    path_valid = any(re.match(pattern, path) for pattern in valid_path_patterns)
    
    # Additional validation for sharing links
    if '/sharing/link' in path and 'surl=' not in query:
        log_info(f"Sharing link missing surl parameter: {link}")
        return {'valid': False, 'reason': 'Sharing link missing surl parameter', 'domain': domain}
    
    if not path_valid:
        log_info(f"Path validation failed - Invalid path structure: {path}")
        return {'valid': False, 'reason': f'Invalid path structure: {path}', 'domain': domain}
    
    # Successful Validation
    log_info(f"Link validation successful - Domain: {domain}, Path: {path}")
    return {'valid': True, 'reason': 'Valid TeraBox link', 'domain': domain}

def save_links_to_csv(links: List[str], csv_path: str = "utils/terebox.csv") -> bool:
    """
    Save extracted TeraBox links to CSV database with comprehensive validation and logging
    
    Args:
        links: List of TeraBox links to save
        csv_path: Path to CSV database file
        
    Returns:
        bool: True if saved successfully, False otherwise
        
    CSV Database Schema:
    - ID: Unique identifier for each link
    - Link: Full TeraBox URL
    - SURL: Short URL identifier extracted from link
    - Domain: Domain name for categorization
    - Extracted_At: Timestamp when link was extracted
    - Status: Processing status (Pending, Processed, Failed)
    - Processed: Whether link has been processed (Yes/No)
    - File_Name: Name of the file (from API response)
    - File_Size: Size of the file (from API response)
    - File_Type: Type of the file (from API response)
    - Download_Link: Direct download link (from API response)
    - Thumbnail: Thumbnail URL (from API response)
    - Response_Data: Full API response as JSON (from API response)
    - Processed_At: Timestamp when link was processed
    - Error_Message: Error message if processing failed
    
    Features:
    - Duplicate detection and prevention
    - Automatic ID assignment
    - Domain extraction and validation
    - Timestamp tracking for audit trail
    - Error recovery for corrupted files
    - Extended schema for API response data
    """
    log_info(f"Starting CSV save operation - Links to save: {len(links)}, Target file: {csv_path}")
    
    try:
        # Directory Preparation
        # Purpose: Ensure CSV file directory exists
        # Strategy: Create directory structure if missing
        csv_dir = os.path.dirname(csv_path)
        os.makedirs(csv_dir, exist_ok=True)
        log_info(f"CSV directory confirmed/created: {csv_dir}")
        
        # Timestamp Generation
        # Purpose: Record when links were extracted for audit trail
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_info(f"Extraction timestamp generated: {timestamp}")
        
        # Existing Data Loading
        # Purpose: Read existing links to prevent duplicates
        # Strategy: Load all existing links into a set for O(1) lookup
        existing_links = set()
        existing_count = 0
        
        if os.path.exists(csv_path):
            log_info(f"CSV file exists, loading existing links for duplicate detection")
            try:
                with open(csv_path, 'r', newline='', encoding='utf-8') as file:
                    reader = csv.DictReader(file)
                    for row in reader:
                        link = row.get('Link', '')
                        if link:
                            existing_links.add(link)
                            existing_count += 1
                
                log_info(f"Loaded {existing_count} existing links from CSV database")
                
            except Exception as e:
                # File Corruption Recovery
                # Purpose: Handle corrupted or invalid CSV files
                # Strategy: Log error and start fresh if file is corrupted
                log_error(e, "save_links_to_csv - reading existing file")
                log_info("CSV file appears corrupted, starting fresh database")
                existing_links = set()
        else:
            log_info("CSV file does not exist, creating new database")
        
        # New Link Processing
        # Purpose: Process new links and prepare CSV rows
        # Strategy: Only add links that don't already exist
        new_rows = []
        skipped_duplicates = 0
        
        for i, link in enumerate(links, 1):
            log_info(f"Processing link {i}/{len(links)}: {link}")
            
            if link not in existing_links:
                # Link Metadata Extraction
                # Purpose: Extract useful metadata from link for database
                # Strategy: Parse URL components for categorization
                
                # Extract SURL (Short URL identifier)
                if '/s/' in link:
                    surl = link.split('/s/')[-1].split('?')[0]  # Handle query parameters
                elif 'surl=' in link:
                    surl = link.split('surl=')[-1].split('&')[0]  # Handle multiple parameters
                else:
                    surl = link.split('/')[-1] if '/' in link else link
                
                # Extract domain for categorization
                try:
                    from urllib.parse import urlparse
                    parsed = urlparse(link)
                    domain = parsed.netloc
                except:
                    domain = link.split('/')[2] if '/' in link else 'Unknown'
                
                # Create CSV row with comprehensive metadata
                row_data = {
                    'ID': existing_count + len(new_rows) + 1,  # Auto-increment ID
                    'Link': link,
                    'SURL': surl,
                    'Domain': domain,
                    'Extracted_At': timestamp,
                    'Status': 'Pending',  # Initial status
                    'Processed': 'No',  # Not processed yet
                    'File_Name': '',  # Will be populated when processed
                    'File_Size': '',  # Will be populated when processed
                    'File_Type': '',  # Will be populated when processed
                    'Download_Link': '',  # Will be populated when processed
                    'Thumbnail': '',  # Will be populated when processed
                    'Response_Data': '',  # Will be populated when processed
                    'Processed_At': '',  # Will be populated when processed
                    'Error_Message': ''  # Will be populated if error occurs
                }
                
                new_rows.append(row_data)
                log_info(f"Added new link to database - ID: {row_data['ID']}, SURL: {surl}, Domain: {domain}")
                
            else:
                # Duplicate Detection
                # Purpose: Track and skip duplicate links
                # Benefits: Prevents database bloat and duplicate processing
                skipped_duplicates += 1
                log_info(f"Skipped duplicate link: {link}")
        
        log_info(f"Link processing completed - New links: {len(new_rows)}, Duplicates skipped: {skipped_duplicates}")
        
        # CSV File Writing
        # Purpose: Write new links to CSV database
        # Strategy: Append to existing file or create new file with headers
        
        # Check if file exists and has content
        file_exists = os.path.exists(csv_path) and os.path.getsize(csv_path) > 0
        log_info(f"CSV file status - Exists: {file_exists}, Will append: {file_exists}")
        
        if new_rows:
            # Write New Data
            # Purpose: Append new links to CSV database
            # Strategy: Use DictWriter for structured CSV output
            with open(csv_path, 'a', newline='', encoding='utf-8') as file:
                fieldnames = ['ID', 'Link', 'SURL', 'Domain', 'Extracted_At', 'Status', 'Processed', 
                            'File_Name', 'File_Size', 'File_Type', 'Download_Link', 'Thumbnail', 
                            'Response_Data', 'Processed_At', 'Error_Message']
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                
                # Write header if file is new or empty
                if not file_exists:
                    writer.writeheader()
                    log_info("CSV header written to new file")
                
                # Write new rows
                writer.writerows(new_rows)
                log_info(f"Successfully wrote {len(new_rows)} new rows to CSV database")
            
            # File Size Tracking
            # Purpose: Monitor database growth for maintenance
            final_size = os.path.getsize(csv_path)
            log_info(f"CSV database updated - File size: {final_size} bytes, Total new entries: {len(new_rows)}")
            
        else:
            log_info("No new links to save - all links were duplicates")
        
        # Operation Success
        log_info(f"CSV save operation completed successfully - File: {csv_path}")
        return True
        
    except Exception as e:
        # Error Handling
        # Purpose: Handle and log any errors during CSV operations
        # Strategy: Provide detailed error information for debugging
        log_error(e, "save_links_to_csv")
        log_info(f"CSV save operation failed - Error: {str(e)}, File: {csv_path}")
        st.error(f"❌ Error saving to CSV: {str(e)}")
        return False

def load_links_from_csv(csv_path: str = "utils/terebox.csv") -> List[Dict]:
    """
    Load TeraBox links from CSV database with comprehensive validation and logging (with auto-migration)
    
    Args:
        csv_path: Path to CSV database file
        
    Returns:
        List of dictionaries containing link data, empty list if error
        
    Loading Process:
    1. Validate file existence and accessibility
    2. Migrate CSV schema if needed (automatic)
    3. Read CSV data with proper encoding
    4. Validate data integrity and format
    5. Filter and clean invalid entries
    6. Return structured data for processing
    
    Data Validation:
    - Check required fields are present
    - Validate link formats and domains
    - Handle corrupted or incomplete rows
    - Log statistics for monitoring
    """
    log_info(f"Starting CSV load operation - Source file: {csv_path}")
    
    try:
        # File Existence Check
        # Purpose: Validate file exists before attempting to read
        # Strategy: Early return if file doesn't exist
        if not os.path.exists(csv_path):
            log_info(f"CSV file does not exist: {csv_path}")
            return []
        
        # File Size and Status Check
        file_size = os.path.getsize(csv_path)
        log_info(f"CSV file found - Size: {file_size} bytes")
        
        if file_size == 0:
            log_info("CSV file is empty, returning empty list")
            return []
        
        # Automatic Schema Migration
        # Purpose: Ensure CSV schema is compatible with current application version
        # Strategy: Migrate schema before loading data to prevent errors
        log_info("Performing automatic CSV schema migration check")
        if not migrate_csv_schema(csv_path):
            log_error(Exception("CSV schema migration failed during load"), "load_links_from_csv")
            # Continue with loading even if migration fails - might still work with old schema
        else:
            log_info("CSV schema migration check completed successfully")
        
        # CSV Data Loading
        # Purpose: Read and parse CSV data with error handling
        # Strategy: Use DictReader for structured data access
        links_data = []
        invalid_rows = 0
        
        log_info("Starting CSV data parsing")
        
        with open(csv_path, 'r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            # Log CSV structure information
            fieldnames = reader.fieldnames
            log_info(f"CSV structure - Fields: {fieldnames}")
            
            # Process each row with validation
            for row_num, row in enumerate(reader, 1):
                log_info(f"Processing CSV row {row_num}: ID={row.get('ID', 'N/A')}")
                
                # Row Validation
                # Purpose: Ensure row has required fields and valid data
                # Strategy: Check for required fields and data integrity
                if _validate_csv_row(row, row_num):
                    links_data.append(dict(row))
                    log_info(f"Row {row_num} validated and added - Link: {row.get('Link', 'N/A')[:50]}...")
                else:
                    invalid_rows += 1
                    log_info(f"Row {row_num} invalid, skipping")
        
        # Loading Statistics
        # Purpose: Provide comprehensive loading statistics
        # Benefits: Monitor data quality and file integrity
        loading_stats = {
            'file_size_bytes': file_size,
            'total_rows_processed': row_num if 'row_num' in locals() else 0,
            'valid_rows': len(links_data),
            'invalid_rows': invalid_rows,
            'csv_fields': fieldnames,
            'load_timestamp': datetime.now().isoformat()
        }
        
        log_info(f"CSV loading completed successfully")
        log_info(f"Loading statistics: {json.dumps(loading_stats, indent=2)}")
        
        # Data Quality Analysis
        if links_data:
            # Analyze loaded data for quality metrics
            domains = [row.get('Domain', 'Unknown') for row in links_data]
            unique_domains = set(domains)
            status_counts = {}
            
            for row in links_data:
                status = row.get('Status', 'Unknown')
                status_counts[status] = status_counts.get(status, 0) + 1
            
            log_info(f"Data quality analysis - Unique domains: {len(unique_domains)}, Status distribution: {status_counts}")
        
        return links_data
        
    except Exception as e:
        # Error Handling
        # Purpose: Handle and log any errors during CSV loading
        # Strategy: Provide detailed error information for debugging
        log_error(e, "load_links_from_csv")
        log_info(f"CSV load operation failed - Error: {str(e)}, File: {csv_path}")
        st.error(f"❌ Error loading from CSV: {str(e)}")
        return []

def _validate_csv_row(row: Dict[str, str], row_num: int) -> bool:
    """
    Validate CSV row data for integrity and completeness
    
    Args:
        row: CSV row data as dictionary
        row_num: Row number for logging
        
    Returns:
        bool: True if row is valid, False otherwise
        
    Validation Checks:
    - Required fields present
    - Link format validation
    - Domain validation
    - Data type validation
    """
    # Required Fields Check
    # Purpose: Ensure essential fields are present
    required_fields = ['Link', 'SURL', 'Domain']
    missing_fields = [field for field in required_fields if not row.get(field)]
    
    if missing_fields:
        log_info(f"Row {row_num} missing required fields: {missing_fields}")
        return False
    
    # Link Format Validation
    # Purpose: Ensure link is a valid URL format
    link = row.get('Link', '')
    if not link.startswith(('http://', 'https://')):
        log_info(f"Row {row_num} has invalid link format: {link}")
        return False
    
    # Domain Validation
    # Purpose: Ensure domain is a known TeraBox domain
    domain = row.get('Domain', '').lower()
    valid_domains = [
        'terabox.com', 'www.terabox.com',
        'terabox.app', 'www.terabox.app',
        '1024terabox.com', '1024tera.com',
        'terasharelink.com', 'terafileshare.com',
        'teraboxapp.com', 'freeterabox.com', 'nephobox.com'
    ]
    
    if domain not in valid_domains:
        log_info(f"Row {row_num} has unknown domain: {domain}")
        return False
    
    log_info(f"Row {row_num} validation successful")
    return True

def migrate_csv_schema(csv_path: str = "utils/terebox.csv") -> bool:
    """
    Migrate CSV from old schema to new extended schema
    
    Args:
        csv_path: Path to CSV database file
        
    Returns:
        bool: True if migration successful or not needed, False if failed
    """
    log_info("Checking CSV schema for migration needs")
    
    try:
        if not os.path.exists(csv_path):
            log_info("CSV file does not exist, no migration needed")
            return True
        
        # Check current schema
        with open(csv_path, 'r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            current_fieldnames = reader.fieldnames or []
        
        # Expected new schema
        expected_fieldnames = [
            'ID', 'Link', 'SURL', 'Domain', 'Extracted_At', 'Status', 'Processed',
            'File_Name', 'File_Size', 'File_Type', 'Download_Link', 'Thumbnail',
            'Response_Data', 'Processed_At', 'Error_Message'
        ]
        
        # Check if migration is needed
        if set(current_fieldnames) == set(expected_fieldnames):
            log_info("CSV schema is already up to date")
            return True
        
        log_info(f"CSV migration needed - Current fields: {len(current_fieldnames)}, Expected: {len(expected_fieldnames)}")
        
        # Read existing data
        existing_data = []
        with open(csv_path, 'r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                existing_data.append(dict(row))
        
        log_info(f"Read {len(existing_data)} existing records for migration")
        
        # Create backup
        backup_path = csv_path + f".backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        import shutil
        shutil.copy2(csv_path, backup_path)
        log_info(f"Created backup at: {backup_path}")
        
        # Migrate data to new schema
        migrated_data = []
        for row in existing_data:
            migrated_row = {}
            
            # Copy existing fields
            for field in expected_fieldnames:
                if field in row:
                    migrated_row[field] = row[field]
                else:
                    # Set default values for new fields
                    migrated_row[field] = ''
            
            migrated_data.append(migrated_row)
        
        # Write migrated data
        with open(csv_path, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=expected_fieldnames)
            writer.writeheader()
            writer.writerows(migrated_data)
        
        log_info(f"CSV schema migration completed successfully - Migrated {len(migrated_data)} records")
        return True
        
    except Exception as e:
        log_error(e, "migrate_csv_schema")
        return False

def update_csv_with_response(link: str, response_data: Dict[str, Any], csv_path: str = "utils/terebox.csv") -> bool:
    """
    Update CSV record with API response data (with automatic schema migration)
    
    Args:
        link: The TeraBox link that was processed
        response_data: API response data or error information
        csv_path: Path to CSV database file
        
    Returns:
        bool: True if updated successfully, False otherwise
    """
    log_info(f"Updating CSV with response data for link: {link[:50]}...")
    
    try:
        if not os.path.exists(csv_path):
            log_info("CSV file does not exist, cannot update")
            return False
        
        # Ensure CSV schema is up to date before updating
        if not migrate_csv_schema(csv_path):
            log_error(Exception("CSV schema migration failed"), "update_csv_with_response")
            return False
        
        # Read all existing data
        updated_rows = []
        found_link = False
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Expected fieldnames after migration
        expected_fieldnames = [
            'ID', 'Link', 'SURL', 'Domain', 'Extracted_At', 'Status', 'Processed',
            'File_Name', 'File_Size', 'File_Type', 'Download_Link', 'Thumbnail',
            'Response_Data', 'Processed_At', 'Error_Message'
        ]
        
        with open(csv_path, 'r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            fieldnames = reader.fieldnames
            
            for row in reader:
                if row['Link'] == link:
                    found_link = True
                    # Update row with response data - only update specific fields
                    if 'error' in response_data:
                        # Handle error response - only update status-related fields
                        row['Status'] = 'Failed'
                        row['Processed'] = 'Yes'
                        if 'Error_Message' in row:  # Only update if field exists
                            row['Error_Message'] = response_data['error']
                        if 'Processed_At' in row:  # Only update if field exists
                            row['Processed_At'] = timestamp
                        log_info(f"Updated CSV row with error: {response_data['error']}")
                    else:
                        # Handle successful response - update all relevant fields
                        row['Status'] = 'Processed'
                        row['Processed'] = 'Yes'
                        
                        # Only update extended fields if they exist in the schema
                        if 'File_Name' in row:
                            row['File_Name'] = response_data.get('file_name', '')
                        if 'File_Size' in row:
                            row['File_Size'] = response_data.get('size', '')
                        if 'File_Type' in row:
                            row['File_Type'] = response_data.get('file_type', '')
                        if 'Download_Link' in row:
                            row['Download_Link'] = response_data.get('direct_link', '')
                        if 'Thumbnail' in row:
                            row['Thumbnail'] = response_data.get('thumb', response_data.get('thumbnail', ''))
                        if 'Response_Data' in row:
                            row['Response_Data'] = json.dumps(response_data)
                        if 'Processed_At' in row:
                            row['Processed_At'] = timestamp
                        if 'Error_Message' in row:
                            row['Error_Message'] = ''
                        
                        log_info(f"Updated CSV row with successful response: {response_data.get('file_name', 'Unknown')}")
                
                updated_rows.append(row)
        
        if not found_link:
            log_info(f"Link not found in CSV database: {link}")
            return False
        
        # Write back updated data using the current fieldnames
        with open(csv_path, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(updated_rows)
        
        log_info("CSV update completed successfully")
        return True
        
    except Exception as e:
        log_error(e, "update_csv_with_response")
        return False

def update_csv_link_status(link: str, status: str, processed: str = "Yes", csv_path: str = "utils/terebox.csv") -> bool:
    """
    Update only Status and Processed columns for a specific link (minimal update)
    
    Args:
        link: The TeraBox link to update
        status: New status value (e.g., 'Opened', 'Failed', 'Processed')
        processed: Processed status (default 'Yes')
        csv_path: Path to CSV database file
        
    Returns:
        bool: True if updated successfully, False otherwise
    """
    log_info(f"Updating CSV link status for: {link[:50]}... -> Status: {status}, Processed: {processed}")
    
    try:
        if not os.path.exists(csv_path):
            log_info("CSV file does not exist, cannot update")
            return False
        
        # Read all existing data
        updated_rows = []
        found_link = False
        
        with open(csv_path, 'r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            fieldnames = reader.fieldnames
            
            for row in reader:
                if row['Link'] == link:
                    found_link = True
                    # Only update Status and Processed columns
                    row['Status'] = status
                    row['Processed'] = processed
                    log_info(f"Updated link status - Status: {status}, Processed: {processed}")
                
                updated_rows.append(row)
        
        if not found_link:
            log_info(f"Link not found in CSV database: {link}")
            return False
        
        # Write back updated data using the existing fieldnames (no schema changes)
        with open(csv_path, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(updated_rows)
        
        log_info("CSV link status update completed successfully")
        return True
        
    except Exception as e:
        log_error(e, "update_csv_link_status")
        return False

def download_file_with_progress(file_info: Dict[str, Any]):
    """
    Download file with enhanced progress tracking and comprehensive error handling
    
    Args:
        file_info: File information dictionary from RapidAPI response
        
    Features:
    - Real-time progress tracking with speed calculation
    - ETA (Estimated Time of Arrival) calculation
    - Multiple download URL fallback support
    - Comprehensive error handling and recovery
    - Detailed logging for debugging and monitoring
    
    Progress Tracking Algorithm:
    - Updates every 0.5 seconds to avoid UI lag
    - Calculates download speed in MB/s
    - Estimates remaining time based on current speed
    - Provides visual progress bar and status updates
    
    Error Recovery:
    - Validates file info before starting download
    - Handles network errors with detailed feedback
    - Provides debug information for failed downloads
    - Offers alternative download options when available
    """
    log_info("Starting enhanced download with progress tracking")
    log_info(f"File info - Name: {file_info.get('file_name', 'Unknown')}, Size: {file_info.get('sizebytes', 0)} bytes")
    
    # Pre-download Validation
    # Purpose: Validate file info before starting download process
    # Strategy: Check for errors and required fields early
    if 'error' in file_info:
        error_msg = file_info['error']
        log_error(Exception(f"Download cancelled due to file info error: {error_msg}"), "download_file_with_progress")
        st.error(f"Cannot download: {error_msg}")
        return
    
    # Download Link Validation
    # Purpose: Ensure we have at least one download URL available
    # Strategy: Check multiple possible link fields
    available_links = []
    link_fields = ['direct_link', 'download_link', 'link']
    
    for field in link_fields:
        if file_info.get(field):
            available_links.append((field, file_info[field]))
    
    if not available_links:
        error_msg = "No download links available in file information"
        log_error(Exception(error_msg), "download_file_with_progress")
        st.error(f"❌ {error_msg}")
        return
    
    log_info(f"Download links available: {len(available_links)} URLs")
    
    # Enhanced progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    speed_text = st.empty()
    
    # Progress callback function
    start_time = time.time()
    last_update = start_time
    
    def progress_callback(downloaded: int, total: int, percentage: float):
        nonlocal last_update
        current_time = time.time()
        
        # Update every 0.5 seconds to avoid too frequent updates
        if current_time - last_update >= 0.5:
            elapsed = current_time - start_time
            if elapsed > 0 and downloaded > 0:
                speed = downloaded / elapsed  # bytes per second
                speed_mb = speed / (1024 * 1024)  # MB per second
                
                # Estimate remaining time
                if speed > 0 and total > downloaded:
                    remaining_bytes = total - downloaded
                    eta_seconds = remaining_bytes / speed
                    eta_min = int(eta_seconds // 60)
                    eta_sec = int(eta_seconds % 60)
                    eta_str = f"{eta_min}m {eta_sec}s" if eta_min > 0 else f"{eta_sec}s"
                    
                    speed_text.text(f"⚡ Speed: {speed_mb:.1f} MB/s | ETA: {eta_str}")
                else:
                    speed_text.text(f"⚡ Speed: {speed_mb:.1f} MB/s")
            
            progress_bar.progress(percentage / 100)
            last_update = current_time
    
    try:
        status_text.text("📥 Initializing download...")
        
        # Use the enhanced RapidAPI client's download method with callback
        result = st.session_state.rapidapi_client.download_file(
            file_info, 
            save_path=None,  # Will use default download/ directory
            callback=progress_callback
        )
        
        progress_bar.progress(100)
        status_text.text("✅ Download completed!")
        speed_text.empty()
        
        time.sleep(1)
        progress_bar.empty()
        status_text.empty()
        
        if 'error' in result:
            st.error(f"❌ Download failed: {result['error']}")
            
            # Show debug information for failed downloads
            with st.expander("🔍 Debug Information"):
                st.text("File Info:")
                st.json(file_info)
                st.text("Download Result:")
                st.json(result)
        else:
            st.success(f"✅ Downloaded successfully!")
            
            # Show detailed download info
            col_info1, col_info2 = st.columns(2)
            with col_info1:
                st.info(f"📁 File saved to: {result['file_path']}")
                st.info(f"📏 Downloaded size: {result['size']:,} bytes")
            
            with col_info2:
                if result.get('original_filename') != result.get('sanitized_filename'):
                    st.info(f"📝 Original: {result.get('original_filename', 'N/A')}")
                    st.info(f"📝 Saved as: {result.get('sanitized_filename', 'N/A')}")
                
                if result.get('download_url_used'):
                    st.caption(f"🔗 Used: {result['download_url_used'][:50]}...")
            
            # Offer Streamlit download button
            try:
                with open(result['file_path'], 'rb') as f:
                    file_data = f.read()
                    
                st.download_button(
                    label=f"💾 Download {result.get('sanitized_filename', file_info['file_name'])}",
                    data=file_data,
                    file_name=result.get('sanitized_filename', file_info['file_name']),
                    mime="application/octet-stream",
                    width='stretch'
                )
                
                # Show file size confirmation
                st.success(f"🎉 File ready for download ({len(file_data):,} bytes)")
                
            except Exception as e:
                st.warning(f"⚠️ Could not create download button: {e}")
                st.info("💡 The file was downloaded to the server, but couldn't be prepared for browser download.")
                
    except Exception as e:
        progress_bar.empty()
        status_text.empty()
        speed_text.empty()
        st.error(f"❌ Unexpected error: {str(e)}")
        
        # Show debug information for unexpected errors
        with st.expander("🔍 Debug Information"):
            st.text("Error Details:")
            st.code(str(e))
            st.text("File Info:")
            st.json(file_info)

st.set_page_config(
    page_title="RapidAPI Mode",
    page_icon="💳",
    layout="wide"
)

# st.title("💳 RapidAPI TeraBox Service")
# st.markdown("Commercial TeraBox API service for reliable, professional-grade file extraction")

# Configuration and State Initialization
# Purpose: Set up RapidAPI mode with proper configuration and state management
# Pattern: Defensive initialization with configuration loading
log_info("RapidAPI Mode page loaded - initializing configuration and state")

# Configuration Manager Setup
# Purpose: Load RapidAPI-specific configuration settings
# Benefits: Centralized configuration, secure credential handling
config_mgr = get_config_manager()
rapidapi_config = config_mgr.get_rapidapi_config()
log_info("RapidAPI configuration loaded from config manager")

# Session State Initialization
# Purpose: Initialize RapidAPI-specific session state variables
# Pattern: Defensive initialization to prevent KeyError exceptions
# Strategy: Only initialize if not present to preserve user data
log_info("Initializing RapidAPI session state variables")

if 'rapidapi_client' not in st.session_state:
    st.session_state.rapidapi_client = None
    log_info("Initialized rapidapi_client state")

if 'rapidapi_validated' not in st.session_state:
    st.session_state.rapidapi_validated = False
    log_info("Initialized rapidapi_validated state")

if 'current_rapidapi_key' not in st.session_state:
    # API Key Initialization Strategy
    # Purpose: Load existing API key from configuration if available
    # Security: Use empty string as fallback to avoid None issues
    initial_key = rapidapi_config.api_key or ""
    st.session_state.current_rapidapi_key = initial_key
    log_info(f"Initialized current_rapidapi_key state - Has key: {bool(initial_key)}")

# Log current session state for debugging
log_info(f"RapidAPI session state - Client: {bool(st.session_state.rapidapi_client)}, Validated: {st.session_state.rapidapi_validated}, Key length: {len(st.session_state.current_rapidapi_key)}")

# Header with service info
col1, col2 = st.columns([3, 1])

# with col1:
#     st.info("""
#     **💳 RapidAPI Mode** provides commercial-grade TeraBox access:
#     - ✅ Professional reliability and uptime
#     - ✅ No complex setup or authentication
#     - ✅ Direct download links guaranteed
#     - ✅ Commercial support and SLA
#     - 💰 Requires RapidAPI subscription
#     """)

# with col2:
#     if st.button("🔄 Switch to Other Modes"):
#         st.switch_page("pages/📊_Mode_Comparison.py")

# Service Overview
# st.header("🏢 RapidAPI TeraBox Service Overview")

# col1, col2, col3 = st.columns(3)

# with col1:
#     st.markdown("""
#     **🎯 What it is:**
#     - Commercial API service
#     - Hosted on RapidAPI marketplace
#     - Professional TeraBox integration
#     - Pay-per-use or subscription model
#     """)

# with col2:
#     st.markdown("""
#     **✅ Benefits:**
#     - Guaranteed uptime
#     - No anti-bot issues
#     - Simple API integration
#     - Professional support
#     """)

# with col3:
#     st.markdown("""
#     **📊 Use Cases:**
#     - Business applications
#     - High-volume processing
#     - Reliability requirements
#     - Commercial projects
#     """)

# API Key Configuration
# st.header("🔑 RapidAPI Configuration")

# with st.expander("📋 How to Get RapidAPI Key", expanded=not st.session_state.rapidapi_validated):
#     st.markdown("""
#     ### Step 1: Create RapidAPI Account
#     1. Go to [RapidAPI.com](https://rapidapi.com)
#     2. Sign up for a free account
#     3. Verify your email address
    
#     ### Step 2: Subscribe to TeraBox Service
#     1. Search for "terabox-downloader-direct-download-link-generator2"
#     2. Choose a subscription plan:
#        - **Basic Plan**: Limited requests per month
#        - **Pro Plan**: Higher request limits
#        - **Ultra Plan**: Unlimited requests
#     3. Subscribe to your chosen plan
    
#     ### Step 3: Get Your API Key
#     1. Go to your RapidAPI dashboard
#     2. Find the TeraBox service in your subscriptions
#     3. Copy your X-RapidAPI-Key
#     4. Paste it in the configuration below
    
#     ### Step 4: Test Your Setup
#     1. Enter your API key below
#     2. Click "Validate API Key"
#     3. Test with sample URLs
#     4. Start using the service!
    
#     **💡 Tip:** Keep your API key secure and don't share it publicly.
#     """)

# API Key Input
# col1, col2 = st.columns([2, 1])

# with col1:

# with col2:
if st.session_state.rapidapi_client:
        # st.success("💳 **API Status: Active**")
        
        # Show API status
        api_status = st.session_state.rapidapi_client.get_api_status()
        
        if api_status['api_key_status'] == 'success':
            st.success("✅ Valid API Key")
        else:
            st.error("❌ Invalid API Key")
        
        # with st.expander("🔍 API Details"):
        #     st.json(api_status)
else:
    api_key_input = st.text_input(
            "Enter your RapidAPI Key:",
            type="password",
            value=st.session_state.current_rapidapi_key,
            placeholder=rapidapi_config.api_key or "298bbd7e09msh8c672d04ba26de4p154bc9jsn9de6459d8a13",
            help="Your X-RapidAPI-Key from the RapidAPI dashboard (Format: [alphanumeric]msh[alphanumeric]jsn[alphanumeric], 50 characters)"
    )
    
    # Real-time format validation
    if api_key_input.strip():
        temp_client = TeraBoxRapidAPI()
        format_check = temp_client.quick_validate_api_key_format(api_key_input.strip())
        
        if format_check['status'] == 'success':
            st.success("✅ API key format is valid")
            with st.expander("📋 Format Details", expanded=False):
                st.json(format_check['details'])
        else:
            st.warning(f"⚠️ Format Issue: {format_check['message']}")
            if 'details' in format_check:
                st.info(f"💡 {format_check['details']}")
                
            # Show format requirements
            with st.expander("📋 RapidAPI Key Format Requirements", expanded=True):
                st.markdown("""
                **Valid RapidAPI Key Format:**
                - **Length**: Exactly 50 characters
                - **Pattern**: Contains 'msh' and 'jsn' markers
                - **Characters**: Only letters (a-z, A-Z) and numbers (0-9)
                - **Example**: `298bbd7e09msh8c672d04ba26de4p154bc9jsn9de6459d8a13`
                
                **Common Issues:**
                - ❌ Wrong length (not 50 characters)
                - ❌ Missing 'msh' or 'jsn' markers
                - ❌ Contains special characters or spaces
                - ❌ Copy-paste errors or truncated key
                """)
        
    col_a, col_b, col_c = st.columns(3)
        
    with col_a:
            if st.button("🔍 Validate API Key", type="primary"):
                # API Key Validation User Action
                # Purpose: Validate user-provided RapidAPI key
                # Process: Format validation + live API testing
                log_info("User initiated API key validation")
                
                if api_key_input.strip():
                    user_key = api_key_input.strip()
                    log_info(f"Validating API key - Length: {len(user_key)} characters")
                    
                    with st.spinner("Validating RapidAPI key..."):
                        # Create RapidAPI client for validation
                        # Purpose: Test the provided API key with actual service
                        # Strategy: Create temporary client for validation
                        validation_start = time.time()
                        client = TeraBoxRapidAPI(user_key)
                        validation_result = client.validate_api_key()
                        validation_duration = time.time() - validation_start
                    
                    log_info(f"API key validation completed in {validation_duration:.2f}s - Status: {validation_result['status']}")
                    
                    if validation_result['status'] == 'success':
                        # Successful Validation Processing
                        # Purpose: Store validated client and update session state
                        # Benefits: Immediate availability for file processing
                        log_info("API key validation successful - updating session state")
                        
                        st.session_state.rapidapi_client = client
                        st.session_state.rapidapi_validated = True
                        st.session_state.current_rapidapi_key = user_key
                        
                        log_info("RapidAPI client stored in session state successfully")
                        st.success("✅ API key is valid and working!")
                        
                        # Validation Details Display
                        # Purpose: Show detailed validation results for transparency
                        # Educational: Help users understand the validation process
                        with st.expander("🔍 Validation Details", expanded=False):
                            st.write("**Format Validation:**")
                            st.json(validation_result.get('format_check', {}))
                            st.write("**Live API Test:**")
                            st.json(validation_result.get('live_test', {}))
                        
                        # State Management for UI Updates
                        # Purpose: Signal successful validation to other components
                        # Pattern: Use StateManager for clean state updates
                        StateManager.update_state('api_validation_completed', True)
                        log_info("API validation completion state updated")
                    elif validation_result['status'] == 'warning':
                        # Handle warnings (like network issues)
                        st.warning(f"⚠️ {validation_result['message']}")
                        if 'details' in validation_result:
                            st.info(f"Details: {validation_result['details']}")
                        
                        # Ask user if they want to proceed anyway
                        if st.button("✅ Use API Key Anyway"):
                            client = TeraBoxRapidAPI(api_key_input.strip())
                            st.session_state.rapidapi_client = client
                            st.session_state.rapidapi_validated = True
                            st.session_state.current_rapidapi_key = api_key_input.strip()
                            st.success("✅ API key configured (with warnings)")
                            # API key configured - using state manager for clean updates
                            StateManager.update_state('api_key_configured_with_warnings', True)
                    else:
                        st.error(f"❌ {validation_result['message']}")
                        if 'details' in validation_result:
                            st.info(f"Details: {validation_result['details']}")
                else:
                    st.error("Please enter an API key")
    
    with col_b:
        if st.button("⚡ Quick Format Check"):
            if api_key_input.strip():
                temp_client = TeraBoxRapidAPI()
                format_result = temp_client.quick_validate_api_key_format(api_key_input.strip())
                
                if format_result['status'] == 'success':
                    st.success("✅ Format is valid!")
                else:
                    st.error(f"❌ {format_result['message']}")
            else:
                st.error("Please enter an API key")
        
    with col_c:
            if st.button("🗑️ Clear API Key"):
                st.session_state.rapidapi_client = None
                st.session_state.rapidapi_validated = False
                st.session_state.current_rapidapi_key = ""
                st.success("API key cleared!")
                # API key cleared - using state manager for clean updates
                StateManager.update_multiple_states({
                    'rapidapi_client': None,
                    'rapidapi_validated': False,
                    'current_rapidapi_key': ''
                })
    st.warning("💳 **API Status: Not Configured**")
    st.caption("Enter and validate your API key above")


# File Processing Section
if st.session_state.rapidapi_client and st.session_state.rapidapi_validated:
    st.header("📁 File Processing")
    
    # Browser Selection Section
    with st.expander("🌐 Browser Settings", expanded=False):
        col_browser, col_info = st.columns([2, 1])
        
        with col_browser:
            selected_browser = create_browser_selection_ui()
            if selected_browser:
                st.success(f"✅ Browser configured")
        
        with col_info:
            st.info("""
            **Browser Selection:**
            Choose which browser to use when opening direct file links.
            The selected browser will be used for all "Open Direct File Link" operations.
            """)
    
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(["🔗 Single File", "📋 Multiple Files", "📝 Text Processor", "📊 CSV Manager", "🧪 Test & Debug", "📊 Usage Info", "💾 Cache Manager"])
    
    with tab1:
        st.subheader("🔗 Single File Processing")
        
        # col1, col2 = st.columns([2, 1])
        
        # with col1:
        terabox_url = st.text_input(
                "TeraBox URL:",
                placeholder="https://www.terabox.app/sharing/link?surl=...",
                help="Paste any TeraBox share link"
        )
        
        # with col2:
        if st.button("📊 Get File Info", type="primary"):
                if terabox_url:
                    # Check if force refresh is enabled
                    force_refresh = st.session_state.get('force_refresh_next', False)
                    
                    if force_refresh:
                        st.info("🔄 Force refresh enabled - bypassing cache")
                        st.session_state.force_refresh_next = False  # Reset after use
                    
                    with st.spinner("Processing via RapidAPI..."):
                        file_info = st.session_state.rapidapi_client.get_file_info(terabox_url, force_refresh=force_refresh)
                    
                    if 'error' in file_info:
                        st.error(f"❌ Error: {file_info['error']}")
                    else:
                        # Check if response was from cache
                        if file_info.get('_cache_info', {}).get('cached', False):
                            cache_age_hours = file_info['_cache_info'].get('cache_age_hours', 0)
                            st.success(f"✅ File information retrieved from cache! (Age: {cache_age_hours:.1f}h)")
                            st.info("🚀 **Lightning fast response from cache!** This saved time and API usage.")
                        else:
                            st.success("✅ File information retrieved from RapidAPI!")
                            st.info("💾 **Response cached for future requests** - Next time will be instant!")
                        
                        # Store in session state for download
                        st.session_state.current_file_info = file_info
                        
                        # Display file info in enhanced cards
                        col_a, col_b, col_c = st.columns(3)
                        
                        with col_a:
                            st.metric("📄 File Name", file_info.get('file_name', 'Unknown'))
                            st.metric("📏 File Size", file_info.get('size', 'Unknown'))
                        
                        with col_b:
                            st.metric("📁 File Type", file_info.get('file_type', 'Unknown').title())
                            st.metric("💾 Size (bytes)", f"{file_info.get('sizebytes', 0):,}")
                        
                        with col_c:
                            if file_info.get('thumbnail'):
                                try:
                                    st.image(file_info['thumbnail'], caption="Thumbnail", width=150)
                                except:
                                    st.caption("📷 Thumbnail available")
                            
                            # Show service indicator with cache status
                            if file_info.get('_cache_info', {}).get('cached', False):
                                st.info("💾 **Cached Response**")
                                surl = file_info['_cache_info'].get('surl', 'Unknown')
                                st.caption(f"SURL: {surl}")
                            else:
                                st.info("🚀 **RapidAPI Service**")
                                st.caption("Fresh API response")
                            
                            # Show validation status
                            if file_info.get('direct_link') and file_info.get('download_link'):
                                st.success("✅ Multiple download links")
                            elif file_info.get('direct_link'):
                                st.success("✅ Direct link ready")
                            else:
                                st.warning("⚠️ Limited download options")
                        
                        # Enhanced download section
                        st.markdown("---")
                        st.subheader("📥 Enhanced Download Options")
                        
                        # Show all available download URLs
                        download_urls = []
                        if file_info.get('direct_link'):
                            download_urls.append(('Direct Link', file_info['direct_link']))
                        if file_info.get('download_link') and file_info.get('download_link') != file_info.get('direct_link'):
                            download_urls.append(('Alternative Link', file_info['download_link']))
                        if file_info.get('link') and file_info.get('link') not in [file_info.get('direct_link'), file_info.get('download_link')]:
                            download_urls.append(('Backup Link', file_info['link']))
                        
                        # Display download URLs
                        for i, (label, url) in enumerate(download_urls):
                            col_url, col_btn = st.columns([3, 1])
                            with col_url:
                                st.text_input(f"{label}:", value=url, key=f"rapid_url_{i}")
                            with col_btn:
                                if st.button(f"📥 Use {label.split()[0]}", key=f"rapid_btn_{i}"):
                                    download_file_with_progress(file_info)
                        
                        # Main download button
                        st.markdown("---")
                        col_download, col_debug = st.columns([2, 1])
                        
                        with col_download:
                            if st.button("🚀 Smart Download (Try All URLs)", type="primary", key="smart_download"):
                                download_file_with_progress(file_info)
                        
                        with col_debug:
                            if st.button("🔍 Debug Info", key="debug_info"):
                                st.json(file_info.get('raw_response', {}))
                else:
                    st.error("Please enter a TeraBox URL")
        if st.button("📥 Open Direct File Link", key="open_direct_file_link"):
                        # Open Direct File Link after fetch Direct Link
                        if 'current_file_info' in st.session_state and st.session_state.current_file_info:
                            file_info = st.session_state.current_file_info
                            
                            # Get preferred browser
                            preferred_browser = st.session_state.get('preferred_browser', None)
                            
                            with st.spinner("🌐 Opening direct file link in browser..."):
                                result = open_direct_file_link(file_info, browser=preferred_browser)
                            
                            # Display result
                            display_browser_open_result(result, show_details=True)
                            
                            # Log the action for debugging
                            if result['status'] == 'success':
                                st.balloons()  # Celebrate success!
                        else:
                            st.error("❌ No file information available. Please get file info first.")
    with tab2:
        st.subheader("📋 Bulk File Processing")
        
        urls_input = st.text_area(
            "Enter multiple TeraBox URLs (one per line):",
            height=150,
            placeholder="https://www.terabox.app/sharing/link?surl=link1\nhttps://terabox.com/s/link2\nhttps://1024terabox.com/s/link3"
        )
        
        # Check if bulk processing is in progress
        bulk_processing_key = 'processing_bulk_files'
        
        if st.button("📊 Process All Files", type="primary"):
            if urls_input.strip():
                urls = [url.strip() for url in urls_input.strip().split('\n') if url.strip()]
                
                if urls:
                    # Set processing flag
                    st.session_state[bulk_processing_key] = True
                    
                    processing_container = st.container()
                    
                    with processing_container:
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        status_text.text(f"🔄 Processing {len(urls)} files via RapidAPI...")
                        
                        try:
                            with st.spinner("Processing multiple files..."):
                                results = st.session_state.rapidapi_client.get_multiple_files_info(urls)
                            
                            progress_bar.progress(100)
                            status_text.text("✅ Processing completed!")
                            
                            # Store results using StateManager
                            StateManager.update_multiple_states({
                                'bulk_processing_results': results,
                                bulk_processing_key: False,
                                'bulk_processing_completed': True
                            })
                            
                            time.sleep(0.5)
                            progress_bar.empty()
                            status_text.empty()
                            
                            st.success(f"✅ Successfully processed {len(results)} files!")
                            
                        except Exception as e:
                            progress_bar.empty()
                            status_text.empty()
                            st.error(f"❌ Processing failed: {str(e)}")
                            st.session_state[bulk_processing_key] = False
                    
        # Show processing status if in progress
        elif st.session_state.get(bulk_processing_key, False):
            st.info("⏳ Bulk processing in progress... Please wait.")
        
        # Display bulk processing results if available
        if st.session_state.get('bulk_processing_completed', False):
            st.balloons()
            st.success("🎉 Bulk processing completed!")
            st.session_state['bulk_processing_completed'] = False
        
        if 'bulk_processing_results' in st.session_state and st.session_state.bulk_processing_results:
            results = st.session_state.bulk_processing_results
            
            # Display results
            successful = [r for r in results if 'error' not in r]
            failed = [r for r in results if 'error' in r]
            
            col_a, col_b = st.columns(2)
            with col_a:
                st.metric("✅ Successful", len(successful))
            with col_b:
                st.metric("❌ Failed", len(failed))
            
            # Show successful files with enhanced display
            if successful:
                        st.subheader("✅ Successfully Processed Files")
                        for i, result in enumerate(successful):
                            with st.expander(f"📄 {result.get('file_name', f'File {i+1}')} - {result.get('size', 'Unknown')}"):
                                col_info, col_links, col_actions = st.columns([2, 2, 1])
                                
                                with col_info:
                                    st.text(f"📄 Name: {result.get('file_name', 'Unknown')}")
                                    st.text(f"📏 Size: {result.get('size', 'Unknown')}")
                                    st.text(f"📁 Type: {result.get('file_type', 'Unknown')}")
                                    st.text(f"💾 Bytes: {result.get('sizebytes', 0):,}")
                                    
                                    # Show thumbnail if available
                                    if result.get('thumbnail'):
                                        try:
                                            st.image(result['thumbnail'], caption="Preview", width=100)
                                        except:
                                            st.caption("📷 Thumbnail available")
                                
                                with col_links:
                                    # Show all available download URLs
                                    if result.get('direct_link'):
                                        st.text_input("Direct Link:", value=result['direct_link'], key=f"bulk_direct_{i}")
                                    if result.get('download_link') and result.get('download_link') != result.get('direct_link'):
                                        st.text_input("Alt Link:", value=result['download_link'], key=f"bulk_alt_{i}")
                                    
                                    # Show service info
                                    st.caption(f"🚀 Service: {result.get('service', 'RapidAPI')}")
                                
                                with col_actions:
                                    if st.button(f"📥 Download", key=f"rapid_dl_{i}"):
                                        download_file_with_progress(result)
                                    
                                    if st.button(f"🌐 Open Link", key=f"rapid_open_{i}"):
                                        preferred_browser = st.session_state.get('preferred_browser', None)
                                        with st.spinner("🌐 Opening link..."):
                                            open_result = open_direct_file_link(result, browser=preferred_browser)
                                        display_browser_open_result(open_result, show_details=False)
                                        if open_result['status'] == 'success':
                                            st.balloons()
                                    
                                    if st.button(f"🔍 Debug", key=f"rapid_debug_{i}"):
                                        st.json(result.get('raw_response', result))
                    
            # Show failed files
            if failed:
                st.subheader("❌ Failed Files")
                for result in failed:
                    st.error(f"URL: {result['original_url'][:50]}... - Error: {result['error']}")
                else:
                    st.error("No valid URLs found")
            else:
                st.error("Please enter at least one URL")
    
    with tab3:
        st.subheader("📝 Text Processing - Extract TeraBox Links")
        
        # Description
        st.info("""
        **📝 Text Processor** - Extract TeraBox links from any text:
        - ✅ Paste text containing TeraBox links
        - ✅ Automatically extract all valid TeraBox URLs
        - ✅ Get file info for all extracted links
        - ✅ Open direct links for all files
        - ✅ Bulk processing of multiple links
        """)
        
        # Text input area
        text_input = st.text_area(
            "📝 Paste your text containing TeraBox links:",
            height=300,
            placeholder="""Example:
Video 👉https://terasharelink.com/s/1FQd8x4-bpyTN8TnV6APOLA

Click and watch 👇👇
Another video 🔥
Video 👉https://terasharelink.com/s/1OpCNKFvSE7dWu55KvT3w-g

Or any other text with TeraBox links...""",
            help="Paste any text containing TeraBox links. The system will automatically extract all valid links."
        )
        
        # Process button
        col_process, col_clear = st.columns([3, 1])
        
        with col_process:
            if st.button("🔍 Extract & Process Links", type="primary", key="extract_links_btn"):
                if text_input.strip():
                    # Extract links
                    with st.spinner("🔍 Extracting TeraBox links from text..."):
                        extracted_links = extract_terabox_links(text_input)
                    
                    if extracted_links:
                        st.success(f"✅ Found {len(extracted_links)} TeraBox links!")
                        
                        # Save to CSV
                        with st.spinner("💾 Saving links to terebox.csv..."):
                            csv_saved = save_links_to_csv(extracted_links)
                        
                        if csv_saved:
                            st.success("💾 Links saved to terebox.csv successfully!")
                        
                        # Store in session state using StateManager for cleaner updates
                        StateManager.update_multiple_states({
                            'extracted_links': extracted_links,
                            'text_processor_results': None,
                            'links_extracted': True,
                            'csv_saved': csv_saved
                        })
                        
                        # Display extracted links in table format
                        st.subheader("🔗 Extracted Links")
                        
                        # Create table data
                        import pandas as pd
                        
                        table_data = []
                        for i, link in enumerate(extracted_links, 1):
                            # Extract SURL from link for easier identification
                            surl = link.split('/')[-1] if '/' in link else link
                            
                            table_data.append({
                                '#': i,
                                'SURL': surl,
                                'Full Link': link,
                                'Domain': link.split('/')[2] if '/' in link else 'Unknown'
                            })
                        
                        # Display as dataframe table
                        df = pd.DataFrame(table_data)
                        st.dataframe(
                            df,
                            width='stretch',
                            hide_index=True,
                            column_config={
                                "#": st.column_config.NumberColumn("No.", width="small"),
                                "SURL": st.column_config.TextColumn("SURL", width="medium"),
                                "Full Link": st.column_config.LinkColumn("Full Link", width="large"),
                                "Domain": st.column_config.TextColumn("Domain", width="medium")
                            }
                        )
                        
                        # Summary info
                        col_summary1, col_summary2, col_summary3 = st.columns(3)
                        with col_summary1:
                            st.metric("📊 Total Links", len(extracted_links))
                        with col_summary2:
                            unique_domains = len(set(row['Domain'] for row in table_data))
                            st.metric("🌐 Unique Domains", unique_domains)
                        with col_summary3:
                            st.metric("🔗 Ready to Process", len(extracted_links))
                        
                        # Process all links button
                        st.markdown("---")
                        # Check if processing is in progress
                        processing_key = 'processing_extracted_links'
                        
                        if st.button("📊 Get File Info for All Links", type="primary", key="process_all_extracted"):
                            # Set processing flag to prevent multiple clicks
                            st.session_state[processing_key] = True
                            
                            # Create a placeholder for the processing area
                            processing_container = st.container()
                            
                            with processing_container:
                                progress_bar = st.progress(0)
                                status_text = st.empty()
                                
                                status_text.text(f"🔄 Processing {len(extracted_links)} extracted links via RapidAPI...")
                                
                                try:
                                    with st.spinner("Processing all extracted links..."):
                                        results = st.session_state.rapidapi_client.get_multiple_files_info(extracted_links)
                                    
                                    progress_bar.progress(100)
                                    status_text.text("✅ Processing completed!")
                                    
                                    # Store results using StateManager for cleaner state management
                                    StateManager.update_multiple_states({
                                        'text_processor_results': results,
                                        processing_key: False,
                                        'processing_completed': True
                                    })
                                    
                                    # Brief pause to show completion
                                    time.sleep(0.5)
                                    progress_bar.empty()
                                    status_text.empty()
                                    
                                    # Show immediate success message with scroll indicator
                                    st.success(f"✅ Successfully processed {len(results)} links! Scroll down to see results.")
                                    
                                    # Add a visual separator
                                    st.markdown("---")
                                    st.markdown("👇 **Results are displayed below** 👇")
                                    st.markdown("---")
                                    
                                except Exception as e:
                                    progress_bar.empty()
                                    status_text.empty()
                                    st.error(f"❌ Processing failed: {str(e)}")
                                    st.session_state[processing_key] = False
                        
                        # Show processing status if in progress
                        elif st.session_state.get(processing_key, False):
                            st.info("⏳ Processing in progress... Please wait.")
                    else:
                        st.warning("⚠️ No TeraBox links found in the provided text.")
                        st.info("""
                        **Supported link formats:**
                        - `https://terasharelink.com/s/...`
                        - `https://terabox.com/s/...`
                        - `https://www.terabox.app/sharing/link?surl=...`
                        - `https://1024terabox.com/s/...`
                        - And other TeraBox variations
                        """)
                else:
                    st.error("Please enter some text to process")
        
        with col_clear:
            if st.button("🗑️ Clear", key="clear_text_btn"):
                # Data cleared - using state manager for clean updates
                StateManager.update_multiple_states({
                    'extracted_links': None,
                    'text_processor_results': None,
                    'data_cleared': True
                })
                st.success("🗑️ Text processor data cleared!")
        
        # Display processing results if available
        # Show completion message if processing just finished
        if st.session_state.get('processing_completed', False):
            st.balloons()  # Celebrate successful processing
            st.success("🎉 Processing completed! Results are shown below.")
            st.session_state['processing_completed'] = False  # Clear the flag
        
        if 'text_processor_results' in st.session_state and st.session_state.text_processor_results:
            results = st.session_state.text_processor_results
            
            # Summary statistics
            successful = [r for r in results if 'error' not in r]
            failed = [r for r in results if 'error' in r]
            
            st.markdown("---")
            st.subheader("📊 Processing Results")
            
            col_success, col_fail, col_total = st.columns(3)
            with col_success:
                st.metric("✅ Successful", len(successful))
            with col_fail:
                st.metric("❌ Failed", len(failed))
            with col_total:
                st.metric("📊 Total Links", len(results))
            
            # Display successful files
            if successful:
                st.subheader("✅ Successfully Processed Files")
                
                # Bulk actions
                col_bulk1, col_bulk2 = st.columns(2)
                
                with col_bulk1:
                    if st.button("🌐 Open All Direct Links", key="open_all_text_links"):
                        preferred_browser = st.session_state.get('preferred_browser', None)
                        success_count = 0
                        
                        progress_bar = st.progress(0)
                        
                        for i, result in enumerate(successful):
                            progress_bar.progress((i + 1) / len(successful))
                            
                            with st.spinner(f"Opening link {i+1}/{len(successful)}..."):
                                open_result = open_direct_file_link(result, browser=preferred_browser)
                            
                            if open_result['status'] == 'success':
                                success_count += 1
                            
                            time.sleep(0.5)  # Small delay between opens
                        
                        progress_bar.empty()
                        
                        if success_count == len(successful):
                            st.success(f"✅ Successfully opened all {success_count} links!")
                            st.balloons()
                        else:
                            st.warning(f"⚠️ Opened {success_count} out of {len(successful)} links")
                
                with col_bulk2:
                    if st.button("📥 Download All Files", key="download_all_text_files"):
                        st.info("💡 Click individual download buttons below to download files")
                
                # Create results table
                st.markdown("### 📋 File Results Table")
                
                results_table_data = []
                for i, result in enumerate(successful):
                    # Extract SURL from original URL for identification
                    original_url = result.get('original_url', '')
                    surl = original_url.split('/')[-1] if '/' in original_url else f'File {i+1}'
                    
                    # Cache status
                    cache_status = "💾 Cached" if result.get('_cache_info', {}).get('cached', False) else "🚀 Fresh"
                    
                    results_table_data.append({
                        '#': i + 1,
                        'SURL': surl,
                        'File Name': result.get('file_name', 'Unknown')[:30] + ('...' if len(result.get('file_name', '')) > 30 else ''),
                        'Size': result.get('size', 'Unknown'),
                        'Type': result.get('file_type', 'Unknown').upper(),
                        'Status': cache_status,
                        'Has Direct Link': '✅' if result.get('direct_link') else '❌',
                        'Has Thumbnail': '🖼️' if result.get('thumbnail') else '📄'
                    })
                
                # Display results table
                results_df = pd.DataFrame(results_table_data)
                
                # Custom column configuration for better display
                column_config = {
                    "#": st.column_config.NumberColumn("No.", width="small"),
                    "SURL": st.column_config.TextColumn("SURL", width="medium"),
                    "File Name": st.column_config.TextColumn("File Name", width="large"),
                    "Size": st.column_config.TextColumn("Size", width="small"),
                    "Type": st.column_config.TextColumn("Type", width="small"),
                    "Status": st.column_config.TextColumn("Status", width="small"),
                    "Has Direct Link": st.column_config.TextColumn("Direct Link", width="small"),
                    "Has Thumbnail": st.column_config.TextColumn("Preview", width="small")
                }
                
                st.dataframe(
                    results_df,
                    width='stretch',
                    hide_index=True,
                    column_config=column_config
                )
                
                # Individual file actions (expandable)
                st.markdown("### 🎯 Individual File Actions")
                
                for i, result in enumerate(successful):
                    file_name = result.get('file_name', f'File {i+1}')
                    file_size = result.get('size', 'Unknown')
                    
                    with st.expander(f"📄 {file_name} - {file_size}", expanded=False):
                        col_info, col_actions = st.columns([3, 2])
                        
                        with col_info:
                            # File details
                            st.markdown("**📋 File Details:**")
                            st.text(f"📄 Name: {result.get('file_name', 'Unknown')}")
                            st.text(f"📏 Size: {result.get('size', 'Unknown')}")
                            st.text(f"📁 Type: {result.get('file_type', 'Unknown')}")
                            st.text(f"💾 Bytes: {result.get('sizebytes', 0):,}")
                            
                            # Show thumbnail if available
                            if result.get('thumbnail'):
                                try:
                                    st.image(result['thumbnail'], caption="Preview", width=150)
                                except:
                                    st.caption("📷 Thumbnail available but couldn't load")
                            
                            # Show links
                            if result.get('direct_link'):
                                st.text_input("🔗 Direct Link:", value=result['direct_link'], key=f"text_direct_{i}")
                            if result.get('download_link') and result.get('download_link') != result.get('direct_link'):
                                st.text_input("🔗 Alt Link:", value=result['download_link'], key=f"text_alt_{i}")
                            
                            # Show service and cache info
                            service_info = f"🚀 Service: {result.get('service', 'RapidAPI')}"
                            if result.get('_cache_info', {}).get('cached', False):
                                cache_age = result['_cache_info'].get('cache_age_hours', 0)
                                service_info += f" | 💾 Cached ({cache_age:.1f}h ago)"
                            st.caption(service_info)
                        
                        with col_actions:
                            st.markdown("**🎯 Actions:**")
                            
                            # Action buttons in a more compact layout
                            if st.button(f"📊 Get File Info", key=f"text_info_{i}", width='stretch'):
                                st.json(result)
                            
                            if st.button(f"📥 Download File", key=f"text_dl_{i}", width='stretch'):
                                download_file_with_progress(result)
                            
                            if st.button(f"🌐 Open Direct Link", key=f"text_open_{i}", width='stretch'):
                                preferred_browser = st.session_state.get('preferred_browser', None)
                                with st.spinner("🌐 Opening link..."):
                                    open_result = open_direct_file_link(result, browser=preferred_browser)
                                display_browser_open_result(open_result, show_details=False)
                                if open_result['status'] == 'success':
                                    st.balloons()
                            
                            # Show quick stats
                            st.markdown("**📊 Quick Stats:**")
                            st.caption(f"Index: #{i+1}")
                            st.caption(f"Direct Link: {'✅ Yes' if result.get('direct_link') else '❌ No'}")
                            st.caption(f"Thumbnail: {'🖼️ Yes' if result.get('thumbnail') else '📄 No'}")
            
            # Display failed files
            if failed:
                st.subheader("❌ Failed Files")
                
                # Create failed files table
                failed_table_data = []
                for i, result in enumerate(failed):
                    original_url = result.get('original_url', 'Unknown')
                    surl = original_url.split('/')[-1] if '/' in original_url else f'Failed {i+1}'
                    error_msg = result.get('error', 'Unknown error')
                    
                    failed_table_data.append({
                        '#': i + 1,
                        'SURL': surl,
                        'Error': error_msg[:50] + ('...' if len(error_msg) > 50 else ''),
                        'URL': original_url[:40] + ('...' if len(original_url) > 40 else ''),
                        'Status': '❌ Failed'
                    })
                
                # Display failed files table
                failed_df = pd.DataFrame(failed_table_data)
                
                failed_column_config = {
                    "#": st.column_config.NumberColumn("No.", width="small"),
                    "SURL": st.column_config.TextColumn("SURL", width="medium"),
                    "Error": st.column_config.TextColumn("Error", width="large"),
                    "URL": st.column_config.TextColumn("URL", width="large"),
                    "Status": st.column_config.TextColumn("Status", width="small")
                }
                
                st.dataframe(
                    failed_df,
                    width='stretch',
                    hide_index=True,
                    column_config=failed_column_config
                )
                
                # Individual retry options
                st.markdown("### 🔄 Retry Failed Files")
                for i, result in enumerate(failed):
                    with st.expander(f"❌ Failed Link {i+1}: {result.get('error', 'Unknown error')[:30]}...", expanded=False):
                        col_error, col_retry = st.columns([2, 1])
                        
                        with col_error:
                            st.error(f"**Error:** {result['error']}")
                            st.text(f"**URL:** {result['original_url']}")
                            
                            # Show error details if available
                            if 'details' in result:
                                st.caption(f"Details: {result['details']}")
                        
                        with col_retry:
                            if st.button(f"🔄 Retry Link {i+1}", key=f"retry_failed_{i}", width='stretch'):
                                with st.spinner("Retrying..."):
                                    retry_result = st.session_state.rapidapi_client.get_file_info(result['original_url'])
                                
                                if 'error' not in retry_result:
                                    st.success("✅ Retry successful!")
                                    st.json(retry_result)
                                else:
                                    st.error(f"❌ Retry failed: {retry_result['error']}")
                            
                            st.caption(f"Link #{i+1}")
                            st.caption("Click to retry")
        
                        # Show extracted links if available but not processed
        elif 'extracted_links' in st.session_state and st.session_state.extracted_links:
            st.markdown("---")
            # Check if processing is in progress
            if st.session_state.get('processing_extracted_links', False):
                st.info("⏳ Processing extracted links... Results will appear here when complete.")
            else:
                st.info("👆 Click 'Get File Info for All Links' above to process the extracted links")
    
    with tab4:
        st.subheader("📊 CSV Manager - TeraBox Links Database")
        
        # Description
        st.info("""
        **📊 CSV Manager** - Manage your saved TeraBox links:
        - ✅ View all extracted links from terebox.csv with detailed file information
        - ✅ Bulk process saved links with real-time progress tracking
        - ✅ Filter and search through your link database
        - ✅ Export and manage your TeraBox link collection
        - ✅ Track processing status and comprehensive response data
        - 🌐 **NEW:** Open all download links in browser with one click
        - 📊 **NEW:** View thumbnails, file sizes, and complete API responses
        """)
        
        # Load links from CSV with automatic schema migration
        csv_data = load_links_from_csv()
        
        # Check if schema migration occurred and notify user
        if csv_data and len(csv_data) > 0:
            # Check if we have the new extended schema
            sample_row = csv_data[0]
            has_extended_schema = 'File_Name' in sample_row
            if has_extended_schema:
                st.success("✅ CSV database loaded successfully with enhanced schema support!")
            else:
                st.info("ℹ️ CSV database loaded. Enhanced features will be available after processing links.")
        
        if csv_data:
            # Display CSV statistics
            st.subheader("📈 Database Statistics")
            
            col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
            
            with col_stat1:
                st.metric("📊 Total Links", len(csv_data))
            
            with col_stat2:
                processed_count = len([row for row in csv_data if row.get('Processed', 'No') == 'Yes'])
                st.metric("✅ Processed", processed_count)
            
            with col_stat3:
                pending_count = len([row for row in csv_data if row.get('Processed', 'No') == 'No'])
                st.metric("⏳ Pending", pending_count)
            
            with col_stat4:
                unique_domains = len(set(row.get('Domain', 'Unknown') for row in csv_data))
                st.metric("🌐 Domains", unique_domains)
            
            # Filter options
            st.markdown("---")
            st.subheader("🔍 Filter & Search")
            
            col_filter1, col_filter2 = st.columns(2)
            
            with col_filter1:
                # Status filter
                status_filter = st.selectbox(
                    "Filter by Status:",
                    ["All", "Pending", "Processed"],
                    key="csv_status_filter"
                )
                
                # Domain filter
                all_domains = sorted(set(row.get('Domain', 'Unknown') for row in csv_data))
                domain_filter = st.selectbox(
                    "Filter by Domain:",
                    ["All"] + all_domains,
                    key="csv_domain_filter"
                )
            
            with col_filter2:
                # Search box
                search_term = st.text_input(
                    "Search Links (SURL or Link):",
                    placeholder="Enter SURL or part of link...",
                    key="csv_search"
                )
                
                # Date range filter
                st.caption("💡 Use filters to narrow down your link collection")
            
            # Apply filters
            filtered_data = csv_data.copy()
            
            if status_filter != "All":
                if status_filter == "Pending":
                    filtered_data = [row for row in filtered_data if row.get('Processed', 'No') == 'No']
                elif status_filter == "Processed":
                    filtered_data = [row for row in filtered_data if row.get('Processed', 'No') == 'Yes']
            
            if domain_filter != "All":
                filtered_data = [row for row in filtered_data if row.get('Domain', 'Unknown') == domain_filter]
            
            if search_term:
                filtered_data = [row for row in filtered_data 
                               if search_term.lower() in row.get('SURL', '').lower() 
                               or search_term.lower() in row.get('Link', '').lower()]
            
            # Display filtered results
            st.markdown("---")
            st.subheader(f"📋 Links Database ({len(filtered_data)} of {len(csv_data)} shown)")
            
            if filtered_data:
                # Create DataFrame for display
                display_df = pd.DataFrame(filtered_data)
                
                # Customize column display
                if not display_df.empty:
                    # Truncate long URLs for better display
                    display_df['Link_Short'] = display_df['Link'].apply(
                        lambda x: x[:50] + '...' if len(str(x)) > 50 else str(x)
                    )
                    
                    # Add processed file information for better display
                    display_df['File_Info'] = display_df.apply(
                        lambda row: f"{row.get('File_Name', '')[:30]}..." if row.get('File_Name') else 'Not processed',
                        axis=1
                    )
                    
                    # Reorder columns for better display
                    column_order = ['ID', 'SURL', 'Link_Short', 'Domain', 'Status', 'Processed', 'File_Info', 'File_Size', 'Processed_At']
                    display_columns = [col for col in column_order if col in display_df.columns]
                    
                    st.dataframe(
                        display_df[display_columns],
                        width='stretch',
                        hide_index=True,
                        column_config={
                            "ID": st.column_config.NumberColumn("ID", width="small"),
                            "SURL": st.column_config.TextColumn("SURL", width="medium"),
                            "Link_Short": st.column_config.TextColumn("Link", width="large"),
                            "Domain": st.column_config.TextColumn("Domain", width="medium"),
                            "Status": st.column_config.TextColumn("Status", width="small"),
                            "Processed": st.column_config.TextColumn("Processed", width="small"),
                            "File_Info": st.column_config.TextColumn("File", width="medium"),
                            "File_Size": st.column_config.TextColumn("Size", width="small"),
                            "Processed_At": st.column_config.TextColumn("Processed At", width="medium")
                        }
                    )
                    
                    # Add expandable details for processed files
                    st.markdown("---")
                    st.subheader("🔍 Detailed File Information")
                    
                    # Filter for processed files only
                    processed_files = [row for row in filtered_data if row.get('Processed') == 'Yes' and row.get('Status') == 'Processed']
                    
                    if processed_files:
                        selected_file_id = st.selectbox(
                            "Select a processed file to view details:",
                            options=[f"ID {row['ID']}: {row.get('File_Name', row.get('SURL', 'Unknown'))}" for row in processed_files],
                            key="csv_file_selector"
                        )
                        
                        if selected_file_id:
                            # Extract ID from selection
                            file_id = int(selected_file_id.split(":")[0].replace("ID ", ""))
                            selected_file = next((row for row in processed_files if int(row['ID']) == file_id), None)
                            
                            if selected_file:
                                with st.expander(f"📄 {selected_file.get('File_Name', 'Unknown File')}", expanded=True):
                                    col_details1, col_details2 = st.columns(2)
                                    
                                    with col_details1:
                                        st.markdown("**📊 File Information:**")
                                        st.text(f"📄 Name: {selected_file.get('File_Name', 'N/A')}")
                                        st.text(f"📏 Size: {selected_file.get('File_Size', 'N/A')}")
                                        st.text(f"📁 Type: {selected_file.get('File_Type', 'N/A')}")
                                        st.text(f"🌐 Domain: {selected_file.get('Domain', 'N/A')}")
                                        st.text(f"⏰ Processed: {selected_file.get('Processed_At', 'N/A')}")
                                    
                                    with col_details2:
                                        st.markdown("**🔗 Links:**")
                                        if selected_file.get('Download_Link'):
                                            st.text_input("Direct Download:", value=selected_file['Download_Link'], key=f"detail_dl_{file_id}")
                                        
                                        if selected_file.get('Thumbnail'):
                                            st.text_input("Thumbnail:", value=selected_file['Thumbnail'], key=f"detail_thumb_{file_id}")
                                            # Show thumbnail image
                                            try:
                                                st.image(selected_file['Thumbnail'], caption="File Thumbnail", width=200)
                                            except:
                                                st.caption("Could not load thumbnail image")
                                    
                                    # Raw response data
                                    if selected_file.get('Response_Data'):
                                        st.markdown("**📋 Complete API Response:**")
                                        try:
                                            response_json = json.loads(selected_file['Response_Data'])
                                            st.json(response_json)
                                        except:
                                            st.text_area("Raw Response Data:", value=selected_file['Response_Data'], height=200, key=f"raw_data_{file_id}")
                    else:
                        st.info("ℹ️ No processed files to display details for. Process some links first!")
                
                # Bulk actions
                st.markdown("---")
                st.subheader("🎯 Bulk Actions")
                
                col_action1, col_action2, col_action3, col_action4 = st.columns(4)
                
                with col_action1:
                    if st.button("📊 Get File Info for All Links", type="primary", key="csv_process_all"):
                        # Extract only the links for processing
                        links_to_process = [row['Link'] for row in filtered_data if row.get('Processed', 'No') == 'No']
                        
                        if links_to_process:
                            # Set processing flag
                            processing_key = 'processing_csv_links'
                            st.session_state[processing_key] = True
                            
                            # Create progress tracking containers
                            progress_container = st.container()
                            with progress_container:
                                st.markdown("### 🔄 Processing Links with Progress Tracking")
                                
                                # Progress bar and status
                                progress_bar = st.progress(0)
                                status_text = st.empty()
                                
                                # Statistics containers
                                col_stats1, col_stats2, col_stats3 = st.columns(3)
                                with col_stats1:
                                    processed_metric = st.empty()
                                with col_stats2:
                                    success_metric = st.empty()
                                with col_stats3:
                                    failed_metric = st.empty()
                            
                            try:
                                results = []
                                successful_count = 0
                                failed_count = 0
                                
                                # Process each link individually with progress updates
                                for i, link in enumerate(links_to_process):
                                    # Update progress
                                    progress = (i + 1) / len(links_to_process)
                                    progress_bar.progress(progress)
                                    status_text.text(f"🔄 Processing link {i + 1} of {len(links_to_process)}: {link[:50]}...")
                                    
                                    # Update metrics
                                    processed_metric.metric("📊 Processed", f"{i + 1}/{len(links_to_process)}")
                                    success_metric.metric("✅ Successful", successful_count)
                                    failed_metric.metric("❌ Failed", failed_count)
                                    
                                    try:
                                        # Process single link
                                        result = st.session_state.rapidapi_client.get_file_info(link)
                                        
                                        if 'error' in result:
                                            failed_count += 1
                                            # Update CSV with error
                                            update_csv_with_response(link, result)
                                        else:
                                            successful_count += 1
                                            # Update CSV with successful response
                                            update_csv_with_response(link, result)
                                        
                                        results.append(result)
                                        
                                    except Exception as e:
                                        failed_count += 1
                                        error_result = {'error': str(e), 'original_url': link}
                                        results.append(error_result)
                                        # Update CSV with error
                                        update_csv_with_response(link, error_result)
                                        log_error(e, f"bulk_processing_link_{i}")
                                
                                # Final progress update
                                progress_bar.progress(1.0)
                                status_text.text("✅ Processing completed!")
                                processed_metric.metric("📊 Processed", f"{len(links_to_process)}/{len(links_to_process)}")
                                success_metric.metric("✅ Successful", successful_count)
                                failed_metric.metric("❌ Failed", failed_count)
                                
                                # Store results
                                StateManager.update_multiple_states({
                                    'csv_processing_results': results,
                                    processing_key: False,
                                    'csv_processing_completed': True
                                })
                                
                                st.success(f"🎉 Bulk processing completed! Processed {len(results)} links ({successful_count} successful, {failed_count} failed)")
                                st.balloons()
                                
                            except Exception as e:
                                st.error(f"❌ Bulk processing failed: {str(e)}")
                                st.session_state[processing_key] = False
                                log_error(e, "bulk_processing_main")
                        else:
                            st.info("ℹ️ No unprocessed links found in current filter")
                
                with col_action2:
                    if st.button("📥 Export Filtered Data", key="csv_export"):
                        if filtered_data:
                            # Convert to DataFrame and prepare for download
                            export_df = pd.DataFrame(filtered_data)
                            csv_export = export_df.to_csv(index=False)
                            
                            st.download_button(
                                label="💾 Download Filtered CSV",
                                data=csv_export,
                                file_name=f"terebox_filtered_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                mime="text/csv",
                                key="download_filtered_csv"
                            )
                        else:
                            st.info("ℹ️ No data to export")
                
                with col_action3:
                    if st.button("🌐 Open All Links", key="csv_open_all"):
                        # Get all processed files with download links
                        processed_files_with_links = [
                            row for row in filtered_data 
                            if row.get('Processed') == 'Yes' 
                            and row.get('Status') == 'Processed' 
                            and row.get('Download_Link')
                        ]
                        
                        if processed_files_with_links:
                            # Create progress tracking for opening links
                            st.markdown("### 🌐 Opening All Download Links")
                            
                            progress_bar = st.progress(0)
                            status_text = st.empty()
                            
                            # Statistics containers
                            col_open_stats1, col_open_stats2, col_open_stats3 = st.columns(3)
                            with col_open_stats1:
                                opened_metric = st.empty()
                            with col_open_stats2:
                                success_metric = st.empty()
                            with col_open_stats3:
                                failed_metric = st.empty()
                            
                            opened_count = 0
                            success_count = 0
                            failed_count = 0
                            
                            preferred_browser = st.session_state.get('preferred_browser', None)
                            
                            # Open each link
                            for i, file_row in enumerate(processed_files_with_links):
                                # Update progress
                                progress = (i + 1) / len(processed_files_with_links)
                                progress_bar.progress(progress)
                                
                                file_name = file_row.get('File_Name', f"File {i+1}")
                                status_text.text(f"🌐 Opening link {i + 1} of {len(processed_files_with_links)}: {file_name[:40]}...")
                                
                                # Update metrics
                                opened_count += 1
                                opened_metric.metric("🔗 Opened", f"{opened_count}/{len(processed_files_with_links)}")
                                success_metric.metric("✅ Success", success_count)
                                failed_metric.metric("❌ Failed", failed_count)
                                
                                try:
                                    # Create file info object for browser opening
                                    file_info = {
                                        'file_name': file_row.get('File_Name', 'Unknown'),
                                        'direct_link': file_row.get('Download_Link'),
                                        'size': file_row.get('File_Size', 'Unknown'),
                                        'original_url': file_row.get('Link')
                                    }
                                    print(f"file_info: {file_info} \n file_row: {file_row}")
                                    # Open the link
                                    with st.spinner(f"🌐 Opening {file_name}..."):
                                        open_result = open_direct_file_link(file_info, browser=preferred_browser)
                                    
                                    if open_result.get('status') == 'success':
                                        success_count += 1
                                        log_info(f"Successfully opened link for: {file_name}")
                                        # Update CSV status to indicate link was opened successfully
                                        update_csv_link_status(file_row.get('Link'), 'Opened', 'Yes')
                                    else:
                                        failed_count += 1
                                        log_error(Exception(f"Failed to open link for: {file_name}"), "bulk_open_links")
                                        # Update CSV status to indicate opening failed
                                        update_csv_link_status(file_row.get('Link'), 'Open Failed', 'Yes')
                                
                                except Exception as e:
                                    failed_count += 1
                                    log_error(e, f"bulk_open_link_{i}")
                                    # Update CSV status to indicate opening failed due to exception
                                    update_csv_link_status(file_row.get('Link'), 'Open Failed', 'Yes')
                                
                                # Small delay to prevent overwhelming the browser
                                import time
                                time.sleep(0.5)
                            
                            # Final progress update
                            progress_bar.progress(1.0)
                            status_text.text("✅ All links opened!")
                            opened_metric.metric("🔗 Opened", f"{len(processed_files_with_links)}/{len(processed_files_with_links)}")
                            success_metric.metric("✅ Success", success_count)
                            failed_metric.metric("❌ Failed", failed_count)
                            
                            if success_count > 0:
                                st.success(f"🎉 Successfully opened {success_count} download links!")
                                st.balloons()
                            
                            if failed_count > 0:
                                st.warning(f"⚠️ Failed to open {failed_count} links. Check browser settings or try individual links.")
                        
                        else:
                            st.info("ℹ️ No processed files with download links found. Process some links first!")
                
                with col_action4:
                    if st.button("🗑️ Clear CSV Database", key="csv_clear_all"):
                        if st.session_state.get('confirm_csv_clear', False):
                            try:
                                # Clear the CSV file
                                csv_path = "utils/terebox.csv"
                                if os.path.exists(csv_path):
                                    os.remove(csv_path)
                                st.success("✅ CSV database cleared successfully!")
                                st.session_state.confirm_csv_clear = False
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Error clearing CSV: {str(e)}")
                        else:
                            st.session_state.confirm_csv_clear = True
                            st.warning("⚠️ Click again to confirm clearing all data")
                
                # Show processing results if available
                if st.session_state.get('csv_processing_completed', False):
                    st.balloons()
                    st.success("🎉 CSV processing completed! Results shown below.")
                    st.session_state['csv_processing_completed'] = False
                
                if 'csv_processing_results' in st.session_state and st.session_state.csv_processing_results:
                    results = st.session_state.csv_processing_results
                    
                    # Display results similar to text processor
                    successful = [r for r in results if 'error' not in r]
                    failed = [r for r in results if 'error' in r]
                    
                    st.markdown("---")
                    st.subheader("📊 Processing Results")
                    
                    col_success, col_fail = st.columns(2)
                    with col_success:
                        st.metric("✅ Successful", len(successful))
                    with col_fail:
                        st.metric("❌ Failed", len(failed))
                    
                    # Display successful files
                    if successful:
                        st.subheader("✅ Successfully Processed Files")
                        
                        for i, result in enumerate(successful):
                            with st.expander(f"📄 {result.get('file_name', f'File {i+1}')} - {result.get('size', 'Unknown')}", expanded=False):
                                # Main file information
                                col_info, col_actions = st.columns([2, 1])
                                
                                with col_info:
                                    st.text(f"📄 Name: {result.get('file_name', 'Unknown')}")
                                    st.text(f"📏 Size: {result.get('size', 'Unknown')}")
                                    st.text(f"📁 Type: {result.get('file_type', 'Unknown')}")
                                    
                                    # Show thumbnail if available
                                    thumbnail_url = result.get('thumb') or result.get('thumbnail')
                                    if thumbnail_url:
                                        st.image(thumbnail_url, caption="File Thumbnail", width=200)
                                    
                                    if result.get('direct_link'):
                                        st.text_input("🔗 Direct Link:", value=result['direct_link'], key=f"csv_direct_{i}")
                                    
                                    # Alternative download links
                                    if result.get('link') and result.get('link') != result.get('direct_link'):
                                        st.text_input("🔗 Alternative Link:", value=result['link'], key=f"csv_alt_{i}")
                                
                                with col_actions:
                                    if st.button(f"📥 Download", key=f"csv_dl_{i}"):
                                        download_file_with_progress(result)
                                    
                                    if st.button(f"🌐 Open Link", key=f"csv_open_{i}"):
                                        preferred_browser = st.session_state.get('preferred_browser', None)
                                        with st.spinner("🌐 Opening link..."):
                                            open_result = open_direct_file_link(result, browser=preferred_browser)
                                        display_browser_open_result(open_result, show_details=False)
                                        if open_result['status'] == 'success':
                                            st.balloons()
                                
                                # Expanded response data section
                                st.markdown("---")
                                with st.expander("🔍 Detailed API Response", expanded=False):
                                    st.markdown("**📊 Complete API Response Data:**")
                                    
                                    # Display response in a formatted way
                                    response_data = {
                                        "File Information": {
                                            "Name": result.get('file_name', 'N/A'),
                                            "Size": result.get('size', 'N/A'),
                                            "Size (bytes)": result.get('sizebytes', 'N/A'),
                                            "Type": result.get('file_type', 'N/A'),
                                        },
                                        "Download Links": {
                                            "Direct Link": result.get('direct_link', 'N/A'),
                                            "Alternative Link": result.get('link', 'N/A'),
                                            "Thumbnail": result.get('thumb', result.get('thumbnail', 'N/A'))
                                        },
                                        "Processing Information": {
                                            "Original URL": result.get('original_url', 'N/A'),
                                            "Processing Time": result.get('processing_time', 'N/A'),
                                            "Cache Status": result.get('_cache_info', {}).get('cached', False)
                                        }
                                    }
                                    
                                    st.json(response_data)
                                    
                                    # Raw response data
                                    if st.checkbox(f"Show Raw Response Data", key=f"raw_response_{i}"):
                                        st.code(json.dumps(result, indent=2), language='json')
                    
                    # Display failed files
                    if failed:
                        st.subheader("❌ Failed Files")
                        for i, result in enumerate(failed):
                            st.error(f"URL: {result.get('original_url', 'Unknown')[:50]}... - Error: {result.get('error', 'Unknown')}")
            
            else:
                st.info("ℹ️ No links match your current filters. Try adjusting the filter criteria.")
        
        else:
            st.info("📝 No links found in terebox.csv. Use the Text Processor tab to extract and save some links first!")
            
            # Quick action to go to text processor
            if st.button("📝 Go to Text Processor", key="goto_text_processor"):
                st.info("💡 Switch to the 'Text Processor' tab above to extract TeraBox links from text.")
    
    with tab5:
        st.subheader("🧪 Testing & Debugging")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**API Testing:**")
            
            if st.button("🔍 Test API Key"):
                with st.spinner("Testing API key..."):
                    validation = st.session_state.rapidapi_client.validate_api_key()
                st.json(validation)
            
            if st.button("🧪 Test with Sample URLs"):
                with st.spinner("Testing with sample URLs..."):
                    test_results = st.session_state.rapidapi_client.test_with_sample_url()
                st.json(test_results)
        
        with col2:
            st.markdown("**Service Information:**")
            
            if st.button("📊 Get API Status"):
                api_status = st.session_state.rapidapi_client.get_api_status()
                st.json(api_status)
            
            if st.button("📈 Get Usage Info"):
                usage_info = st.session_state.rapidapi_client.get_usage_info()
                st.json(usage_info)
        
        # Custom URL testing
        st.markdown("**Custom URL Testing:**")
        test_url = st.text_input("Test URL:", placeholder="https://terabox.com/s/your_test_link")
        
        if st.button("🧪 Test Custom URL"):
            if test_url:
                with st.spinner("Testing custom URL..."):
                    result = st.session_state.rapidapi_client.get_file_info(test_url)
                
                if 'error' in result:
                    st.error(f"❌ Test failed: {result['error']}")
                else:
                    st.success("✅ Test successful!")
                    st.json(result)
            else:
                st.error("Please enter a test URL")
    
    with tab6:
        st.subheader("📊 Usage Information")
        
        # Pricing information
        pricing_info = st.session_state.rapidapi_client.get_pricing_info()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**💰 Pricing Model:**")
            st.info(pricing_info['pricing_model'])
            
            st.markdown("**✅ Benefits:**")
            for benefit in pricing_info['benefits']:
                st.text(f"• {benefit}")
        
        with col2:
            st.markdown("**⚠️ Considerations:**")
            for consideration in pricing_info['considerations']:
                st.text(f"• {consideration}")
            
            if st.button("🌐 Open RapidAPI Dashboard"):
                st.markdown(f"[Open Dashboard]({pricing_info['dashboard']})")
        
        # Supported formats
        st.markdown("**🔗 Supported URL Formats:**")
        supported_formats = st.session_state.rapidapi_client.get_supported_formats()
        
        for format_url in supported_formats:
            st.code(format_url)
    
    with tab7:
        st.subheader("💾 Cache Management")
        
        # Cache status and information
        cache_info = st.session_state.rapidapi_client.get_cache_info()
        
        if cache_info.get('enabled'):
            # st.success("✅ **Cache Status: Enabled**")
            
            # col1, col2 = st.columns(2)
            
            # with col1:
            #     st.info(f"📁 **Cache Directory:** `{cache_info.get('cache_directory', 'Unknown')}`")
            #     st.info(f"⏰ **Cache TTL:** {cache_info.get('ttl_hours', 24)} hours")
            
            # with col2:
            # Cache statistics
            if st.button("📊 Get Cache Statistics"):
                    with st.spinner("Loading cache statistics..."):
                        cache_stats = st.session_state.rapidapi_client.get_cache_stats()
                    
                    if 'error' not in cache_stats:
                        col_stat1, col_stat2, col_stat3 = st.columns(3)
                        
                        with col_stat1:
                            st.metric("📄 Total Files", cache_stats.get('total_files', 0))
                            st.metric("✅ Valid Files", cache_stats.get('valid_files', 0))
                        
                        with col_stat2:
                            st.metric("⚠️ Expired Files", cache_stats.get('expired_files', 0))
                            st.metric("💾 Total Size", f"{cache_stats.get('total_size_mb', 0):.2f} MB")
                        
                        with col_stat3:
                            # Show cache efficiency
                            total_files = cache_stats.get('total_files', 0)
                            valid_files = cache_stats.get('valid_files', 0)
                            efficiency = (valid_files / total_files * 100) if total_files > 0 else 0
                            st.metric("🎯 Cache Efficiency", f"{efficiency:.1f}%")
                        
                        # Show detailed file list
                        if cache_stats.get('files'):
                            st.markdown("---")
                            st.subheader("📋 Cache Files Details")
                            
                            # Create a dataframe for better display
                            import pandas as pd
                            
                            files_data = []
                            for file_info in cache_stats['files'][:10]:  # Show only first 10
                                files_data.append({
                                    'SURL': file_info.get('surl', 'Unknown')[:15] + '...' if len(file_info.get('surl', '')) > 15 else file_info.get('surl', 'Unknown'),
                                    'Age (hours)': f"{file_info.get('age_hours', 0):.1f}",
                                    'Size (KB)': f"{file_info.get('size_kb', 0):.1f}",
                                    'Status': '✅ Valid' if file_info.get('is_valid', False) else '⚠️ Expired',
                                    'Created': file_info.get('created_at', 'Unknown')[:10] if file_info.get('created_at') else 'Unknown'
                                })
                            
                            if files_data:
                                df = pd.DataFrame(files_data)
                                st.dataframe(df, width='stretch', hide_index=True)
                                
                                if len(cache_stats['files']) > 10:
                                    st.caption(f"Showing first 10 of {len(cache_stats['files'])} cache files")
                    else:
                        st.error(f"❌ Error getting cache stats: {cache_stats.get('error', 'Unknown error')}")
            
            # Cache management actions
            st.markdown("---")
            st.subheader("🛠️ Cache Actions")
            
            col_action1, col_action2, col_action3 = st.columns(3)
            
            with col_action1:
                if st.button("🧹 Clean Expired Cache", type="secondary"):
                    with st.spinner("Cleaning expired cache files..."):
                        cleanup_result = st.session_state.rapidapi_client.cleanup_expired_cache()
                    
                    if cleanup_result.get('status') == 'success':
                        cleaned_files = cleanup_result.get('cleaned_files', 0)
                        if cleaned_files > 0:
                            st.success(f"✅ Cleaned {cleaned_files} expired cache files")
                        else:
                            st.info("ℹ️ No expired cache files found")
                    else:
                        st.error(f"❌ Cleanup failed: {cleanup_result.get('message', 'Unknown error')}")
            
            with col_action2:
                if st.button("🗑️ Clear All Cache", type="secondary"):
                    if st.session_state.get('confirm_clear_cache', False):
                        with st.spinner("Clearing all cache files..."):
                            clear_result = st.session_state.rapidapi_client.clear_cache()
                        
                        if clear_result.get('status') == 'success':
                            cleared_files = clear_result.get('cleared', 0)
                            st.success(f"✅ Cleared {cleared_files} cache files")
                        else:
                            st.error(f"❌ Clear failed: {clear_result.get('message', 'Unknown error')}")
                        
                        st.session_state.confirm_clear_cache = False
                    else:
                        st.session_state.confirm_clear_cache = True
                        st.warning("⚠️ Click again to confirm clearing all cache")
            
            with col_action3:
                # Force refresh option
                st.markdown("**🔄 Force Refresh:**")
                st.caption("Next request will bypass cache")
                if 'force_refresh_next' not in st.session_state:
                    st.session_state.force_refresh_next = False
                
                if st.checkbox("Force refresh next request", value=st.session_state.force_refresh_next):
                    st.session_state.force_refresh_next = True
                    st.info("ℹ️ Next request will bypass cache")
                else:
                    st.session_state.force_refresh_next = False
            
            # # Cache configuration
            # st.markdown("---")
            # st.subheader("⚙️ Cache Configuration")
            
            # current_ttl = cache_info.get('ttl_hours', 24)
            # st.info(f"Current cache TTL: {current_ttl} hours")
            # st.caption("Cache TTL (Time To Live) determines how long responses are cached before expiring.")
            
            # # Show cache benefits
            # with st.expander("💡 Cache Benefits"):
            #     st.markdown("""
            #     **✅ Performance Benefits:**
            #     - Faster response times for repeated requests
            #     - Reduced API usage and costs
            #     - Better user experience with instant results
            #     - Offline access to previously fetched data
                
            #     **📊 Usage Optimization:**
            #     - Automatic cleanup of expired files
            #     - Configurable cache duration
            #     - Smart cache key generation using SURL
            #     - Detailed cache statistics and monitoring
                
            #     **🔧 Management Features:**
            #     - Force refresh to bypass cache
            #     - Selective or complete cache clearing
            #     - Cache file inspection and monitoring
            #     - Automatic expiry based on TTL
            #     """)
        
        else:
            st.warning("⚠️ **Cache Status: Disabled**")
            st.info("Caching is not enabled for this RapidAPI client instance.")
            
            with st.expander("ℹ️ About Caching"):
                st.markdown("""
                **What is Response Caching?**
                
                Response caching stores API responses locally to improve performance and reduce API usage:
                
                - **Faster Access**: Previously fetched files load instantly
                - **Cost Savings**: Reduces RapidAPI calls and associated costs
                - **Better Experience**: No waiting for repeated requests
                - **Offline Access**: Access cached data even without internet
                
                **How It Works:**
                1. First request fetches data from RapidAPI and caches it
                2. Subsequent requests for the same TeraBox link return cached data
                3. Cache expires after 24 hours (configurable)
                4. Expired cache is automatically cleaned up
                
                **Cache Storage:**
                - Files stored in `output/sessions/` directory
                - Named using TeraBox link identifier (surl)
                - JSON format with metadata and response data
                - Automatic cleanup of expired entries
                """)

# else:
#     # Getting started section
#     st.header("🚀 Getting Started with RapidAPI")
    
#     col1, col2 = st.columns(2)
    
#     with col1:
#         st.markdown("""
#         ### ✅ Why Choose RapidAPI Mode:
#         - **Professional Reliability** - Commercial-grade uptime and performance
#         - **No Complex Setup** - Just need an API key, no OAuth or cookies
#         - **Guaranteed Results** - Professional service with SLA
#         - **Scalable** - Handle high-volume requests
#         - **Support** - Commercial support available
#         - **No Anti-Bot Issues** - Service handles all technical challenges
#         """)
    
#     with col2:
#         st.markdown("""
#         ### 💰 Cost Considerations:
#         - **Pay-per-Use** - Only pay for what you use
#         - **Subscription Plans** - Various tiers available
#         - **Free Tier** - Usually includes some free requests
#         - **Business Plans** - Higher limits for commercial use
#         - **Transparent Pricing** - Clear pricing on RapidAPI marketplace
#         - **No Hidden Costs** - What you see is what you pay
#         """)
    
#     # Comparison with other modes
#     st.subheader("📊 Quick Comparison")
    
#     comparison_data = {
#         "Aspect": ["Setup", "Cost", "Reliability", "Support", "Rate Limits"],
#         "🎪 Unofficial": ["None", "Free", "Variable", "Community", "May hit blocks"],
#         "🍪 Cookie": ["Cookie needed", "Free", "Good", "Community", "Account limits"],
#         "🏢 Official API": ["Complex", "Free*", "Excellent", "Official", "API limits"],
#         "💳 RapidAPI": ["API key only", "Paid", "Excellent", "Commercial", "Plan-based"]
#     }
    
#     import pandas as pd
#     df = pd.DataFrame(comparison_data)
#     st.dataframe(df, width='stretch', hide_index=True)
    
#     # Sample API response
#     st.subheader("📋 Sample API Response")
    
#     with st.expander("📄 Example Response Format"):
#         sample_response = {
#             "direct_link": "https://data.1024tera.com/file/fa17446224904abdcb3c052c69d1a7e2?bkt=...",
#             "file_name": "Richh(1)(1)(1)(1).mp4", 
#             "link": "https://d.1024tera.com/file/fa17446224904abdcb3c052c69d1a7e2?fid=...",
#             "size": "16.00 MB",
#             "sizebytes": 16775878,
#             "thumb": "https://data.1024tera.com/thumbnail/fa17446224904abdcb3c052c69d1a7e2?fid=..."
#         }
#         st.json(sample_response)

# # Pricing and plans section
# st.markdown("---")
# st.header("💰 RapidAPI Pricing & Plans")

# col1, col2, col3 = st.columns(3)

# with col1:
#     st.markdown("""
#     **🆓 Basic Plan**
#     - Limited requests/month
#     - Good for testing
#     - Personal projects
#     - Low volume usage
#     """)

# with col2:
#     st.markdown("""
#     **💼 Pro Plan**
#     - Higher request limits
#     - Business applications
#     - Regular usage
#     - Priority support
#     """)

# with col3:
#     st.markdown("""
#     **🚀 Ultra Plan**
#     - Unlimited requests
#     - Enterprise usage
#     - High-volume processing
#     - Premium support
#     """)

# st.info("💡 **Note:** Visit the RapidAPI marketplace for current pricing and plan details.")

# # Footer
# st.markdown("---")
# st.info("""
# 💳 **RapidAPI Mode Summary:**
# - Professional commercial service for TeraBox access
# - Simple API key authentication
# - Reliable direct download links
# - Commercial support and SLA
# - Perfect for business applications and high-volume usage
# - Requires RapidAPI subscription but offers guaranteed reliability
# """)
