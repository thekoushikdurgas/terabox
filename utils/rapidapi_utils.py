"""
RapidAPI Utilities Module

This module provides utility functions that were extracted from the main RapidAPI Mode file
to improve code organization and reusability.

Utility Categories:
- Link extraction and validation
- CSV database operations
- File processing utilities
- Download management
- Progress tracking
- Error handling

Architecture:
- Modular utility functions
- Comprehensive error handling
- Detailed logging and monitoring
- State management integration
- Performance optimization
"""

import re
import csv
import os
import json
import time
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from urllib.parse import urlparse
from utils.config import log_info, log_error
import streamlit as st


# ============================================================================
# LINK EXTRACTION AND VALIDATION UTILITIES
# ============================================================================

def extract_terabox_links_enhanced(text: str) -> List[str]:
    """
    Extract all TeraBox/TeraShare links from text using comprehensive pattern matching
    
    Enhanced version with improved logging, statistics, and validation
    
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
    
    Performance Monitoring:
    - Pattern execution timing
    - Link validation metrics
    - Memory usage tracking
    - Detailed statistics logging
    """
    log_info(f"[ENHANCED] Starting TeraBox link extraction from text")
    log_info(f"Text analysis - Length: {len(text)} characters, Lines: {len(text.splitlines())}")
    
    extraction_start_time = time.time()
    
    # Enhanced Text Analysis
    # Purpose: Analyze text characteristics for better processing
    # Benefits: Optimization hints, quality metrics, debugging information
    text_analysis = _analyze_text_characteristics(text)
    log_info(f"Text characteristics analysis: {json.dumps(text_analysis, indent=2)}")
    
    # Comprehensive TeraBox URL Patterns
    # Enhanced with additional domains and improved pattern matching
    patterns = _get_comprehensive_url_patterns()
    log_info(f"Using {len(patterns)} enhanced regex patterns for comprehensive link detection")
    
    # Text Preprocessing for Better Link Detection
    # Purpose: Clean text and prepare for pattern matching
    # Strategy: Handle Unicode, emojis, and formatting characters
    cleaned_text = _preprocess_text_for_extraction(text)
    log_info(f"Text preprocessing completed - Original: {len(text)}, Cleaned: {len(cleaned_text)}")
    
    # Pattern Matching Execution with Performance Monitoring
    all_links, pattern_stats = _execute_pattern_matching(patterns, cleaned_text)
    log_info(f"Pattern matching completed - Total raw matches: {len(all_links)}")
    
    # Enhanced Link Validation and Filtering
    validated_links, validation_stats = _validate_and_filter_links(all_links)
    log_info(f"Link validation completed - Valid: {len(validated_links)}, Invalid: {validation_stats['invalid_count']}")
    
    # Advanced Deduplication with Statistics
    unique_links, dedup_stats = _deduplicate_links_with_stats(validated_links)
    log_info(f"Deduplication completed - Unique: {len(unique_links)}, Duplicates removed: {dedup_stats['duplicates_removed']}")
    
    # Final Extraction Statistics and Performance Metrics
    extraction_duration = time.time() - extraction_start_time
    
    extraction_summary = {
        'extraction_duration_ms': round(extraction_duration * 1000, 2),
        'total_patterns': len(patterns),
        'raw_matches': len(all_links),
        'validated_links': len(validated_links),
        'unique_links': len(unique_links),
        'duplicates_removed': dedup_stats['duplicates_removed'],
        'invalid_links': validation_stats['invalid_count'],
        'text_characteristics': text_analysis,
        'pattern_performance': pattern_stats,
        'validation_performance': validation_stats,
        'deduplication_performance': dedup_stats
    }
    
    log_info(f"[ENHANCED] Link extraction completed successfully in {extraction_duration:.3f}s")
    log_info(f"Comprehensive extraction summary: {json.dumps(extraction_summary, indent=2)}")
    
    return unique_links


def _analyze_text_characteristics(text: str) -> Dict[str, Any]:
    """
    Analyze text characteristics for optimization and debugging
    
    Args:
        text: Input text to analyze
        
    Returns:
        Dict with text analysis results
    """
    log_info("Analyzing text characteristics for extraction optimization")
    
    # Basic text metrics
    lines = text.splitlines()
    words = text.split()
    
    # Unicode and emoji analysis
    emoji_count = len(re.findall(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]', text))
    unicode_chars = sum(1 for char in text if ord(char) > 127)
    
    # URL detection
    potential_urls = len(re.findall(r'https?://[^\s]+', text))
    terabox_mentions = len(re.findall(r'terabox|terashare|terafile', text, re.IGNORECASE))
    
    analysis = {
        'total_characters': len(text),
        'total_lines': len(lines),
        'total_words': len(words),
        'empty_lines': len([line for line in lines if not line.strip()]),
        'emoji_count': emoji_count,
        'unicode_characters': unicode_chars,
        'potential_urls': potential_urls,
        'terabox_mentions': terabox_mentions,
        'avg_line_length': sum(len(line) for line in lines) / len(lines) if lines else 0,
        'has_formatting': any(char in text for char in ['\t', '\r', '\n']),
        'complexity_score': _calculate_text_complexity(text)
    }
    
    log_info(f"Text characteristics analysis completed: {analysis}")
    return analysis


def _calculate_text_complexity(text: str) -> float:
    """Calculate text complexity score for processing optimization"""
    # Simple complexity calculation based on various factors
    factors = {
        'length': min(len(text) / 10000, 1.0),  # Normalize to 0-1
        'unicode_ratio': sum(1 for char in text if ord(char) > 127) / max(len(text), 1),
        'url_density': len(re.findall(r'https?://', text)) / max(len(text.split()), 1),
        'special_chars': sum(1 for char in text if not char.isalnum() and not char.isspace()) / max(len(text), 1)
    }
    
    # Weighted complexity score
    complexity = (
        factors['length'] * 0.3 +
        factors['unicode_ratio'] * 0.2 +
        factors['url_density'] * 0.3 +
        factors['special_chars'] * 0.2
    )
    
    return round(complexity, 3)


def _get_comprehensive_url_patterns() -> List[str]:
    """
    Get comprehensive list of TeraBox URL patterns
    
    Returns:
        List of regex patterns for matching TeraBox URLs
    """
    log_info("Building comprehensive TeraBox URL pattern list")
    
    patterns = [
        # Official TeraBox Domains - Enhanced patterns
        r'https://www\.terabox\.app/sharing/link\?surl=[A-Za-z0-9_-]+(?:&[^\\s]*)?',  # With optional parameters
        r'https://terabox\.com/s/[A-Za-z0-9_-]+(?:\?[^\\s]*)?',  # With optional query params
        r'https://www\.terabox\.com/sharing/link\?surl=[A-Za-z0-9_-]+(?:&[^\\s]*)?',
        r'https://terabox\.app/s/[A-Za-z0-9_-]+(?:\?[^\\s]*)?',
        r'https://www\.terabox\.app/s/[A-Za-z0-9_-]+(?:\?[^\\s]*)?',
        
        # Mirror and Alternative Domains - Enhanced patterns
        r'https://1024terabox\.com/s/[A-Za-z0-9_-]+(?:\?[^\\s]*)?',
        r'https://1024tera\.com/s/[A-Za-z0-9_-]+(?:\?[^\\s]*)?',
        r'https://www\.1024tera\.com/s/[A-Za-z0-9_-]+(?:\?[^\\s]*)?',
        r'https://teraboxapp\.com/s/[A-Za-z0-9_-]+(?:\?[^\\s]*)?',
        r'https://freeterabox\.com/s/[A-Za-z0-9_-]+(?:\?[^\\s]*)?',
        r'https://nephobox\.com/s/[A-Za-z0-9_-]+(?:\?[^\\s]*)?',
        
        # Share Link Domains - Enhanced patterns
        r'https://terasharelink\.com/s/[A-Za-z0-9_-]+(?:\?[^\\s]*)?',
        r'https://terafileshare\.com/s/[A-Za-z0-9_-]+(?:\?[^\\s]*)?',
        r'https://www\.terafileshare\.com/s/[A-Za-z0-9_-]+(?:\?[^\\s]*)?',
        
        # Generic patterns for new domains - More flexible
        r'https://[a-zA-Z0-9.-]*terabox[a-zA-Z0-9.-]*/s/[A-Za-z0-9_-]+(?:\?[^\\s]*)?',
        r'https://[a-zA-Z0-9.-]*terabox[a-zA-Z0-9.-]*/sharing/link\?surl=[A-Za-z0-9_-]+(?:&[^\\s]*)?',
        
        # Protocol-agnostic patterns for edge cases
        r'(?:https?://)?(?:www\.)?terabox\.(?:com|app)/s/[A-Za-z0-9_-]+',
        r'(?:https?://)?(?:www\.)?terabox\.(?:com|app)/sharing/link\?surl=[A-Za-z0-9_-]+'
    ]
    
    log_info(f"Comprehensive pattern list built - {len(patterns)} patterns available")
    return patterns


def _preprocess_text_for_extraction(text: str) -> str:
    """
    Preprocess text for better link extraction
    
    Args:
        text: Raw input text
        
    Returns:
        Preprocessed text optimized for pattern matching
    """
    log_info("Preprocessing text for enhanced link extraction")
    
    # Remove excessive whitespace and normalize line breaks
    cleaned_text = re.sub(r'\s+', ' ', text.strip())
    
    # Handle common text formatting issues
    # Replace smart quotes and other Unicode punctuation
    replacements = {
        '"': '"', '"': '"',  # Smart quotes
        ''': "'", ''': "'",  # Smart apostrophes
        '…': '...',          # Ellipsis
        '–': '-', '—': '-'   # Em and en dashes
    }
    
    for old, new in replacements.items():
        cleaned_text = cleaned_text.replace(old, new)
    
    log_info(f"Text preprocessing completed - Character replacements applied")
    return cleaned_text


def _execute_pattern_matching(patterns: List[str], text: str) -> tuple:
    """
    Execute pattern matching with performance monitoring
    
    Args:
        patterns: List of regex patterns
        text: Text to search
        
    Returns:
        Tuple of (all_links, pattern_stats)
    """
    log_info("Executing pattern matching with performance monitoring")
    
    all_links = []
    pattern_stats = {}
    
    for i, pattern in enumerate(patterns):
        pattern_name = _get_pattern_description(pattern, i)
        log_info(f"Applying pattern {i+1}/{len(patterns)} ({pattern_name})")
        
        pattern_start = time.time()
        try:
            links = re.findall(pattern, text, re.IGNORECASE)
            pattern_duration = time.time() - pattern_start
            
            all_links.extend(links)
            pattern_stats[pattern_name] = {
                'matches': len(links),
                'duration_ms': round(pattern_duration * 1000, 2),
                'links_sample': links[:3] if links else [],
                'pattern': pattern,
                'success': True
            }
            
            log_info(f"Pattern {i+1} ({pattern_name}) found {len(links)} links in {pattern_duration*1000:.2f}ms")
            
        except re.error as e:
            pattern_duration = time.time() - pattern_start
            pattern_stats[pattern_name] = {
                'matches': 0,
                'duration_ms': round(pattern_duration * 1000, 2),
                'error': str(e),
                'pattern': pattern,
                'success': False
            }
            log_error(e, f"pattern_matching_{i}")
    
    log_info(f"Pattern matching execution completed - Total matches: {len(all_links)}")
    return all_links, pattern_stats


def _get_pattern_description(pattern: str, index: int) -> str:
    """
    Get human-readable description for regex pattern
    
    Args:
        pattern: Regex pattern string
        index: Pattern index for fallback naming
        
    Returns:
        Human-readable pattern description
    """
    pattern_descriptions = {
        'terasharelink': 'TeraShare Links',
        'terafileshare': 'TeraFile Share Links',
        'terabox\\.app.*sharing': 'Official App Sharing',
        'terabox\\.com.*sharing': 'Official Sharing Links',
        'terabox\\.com/s': 'Standard Short Links',
        'terabox\\.app/s': 'App Short Links',
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


def _validate_and_filter_links(all_links: List[str]) -> tuple:
    """
    Validate and filter extracted links with comprehensive statistics
    
    Args:
        all_links: List of extracted links to validate
        
    Returns:
        Tuple of (validated_links, validation_stats)
    """
    log_info(f"Starting enhanced link validation for {len(all_links)} links")
    
    validation_start_time = time.time()
    validated_links = []
    invalid_links = []
    validation_details = {}
    
    for i, link in enumerate(all_links):
        log_info(f"Validating link {i+1}/{len(all_links)}: {link[:50]}...")
        
        validation_result = validate_terabox_link_enhanced(link)
        if validation_result['valid']:
            validated_links.append(link)
            log_info(f"Link validated: {link} - Domain: {validation_result['domain']}")
        else:
            invalid_links.append(link)
            validation_details[link] = validation_result
            log_info(f"Link invalid: {link} - Reason: {validation_result['reason']}")
    
    validation_duration = time.time() - validation_start_time
    
    validation_stats = {
        'total_links': len(all_links),
        'valid_links': len(validated_links),
        'invalid_count': len(invalid_links),
        'validation_duration_ms': round(validation_duration * 1000, 2),
        'validation_details': validation_details,
        'success_rate': (len(validated_links) / len(all_links) * 100) if all_links else 0
    }
    
    log_info(f"Link validation completed - Success rate: {validation_stats['success_rate']:.1f}%")
    return validated_links, validation_stats


def validate_terabox_link_enhanced(link: str) -> Dict[str, Any]:
    """
    Enhanced TeraBox link validation with detailed error reporting
    
    Args:
        link: URL to validate
        
    Returns:
        Dict with comprehensive validation result and details
    """
    log_info(f"Enhanced validation for TeraBox link: {link}")
    
    # Basic validation checks
    if not link or not isinstance(link, str):
        return {
            'valid': False, 
            'reason': 'Empty or invalid link format', 
            'domain': None,
            'error_code': 'INVALID_INPUT'
        }
    
    # Protocol validation
    if not link.lower().startswith(('http://', 'https://')):
        return {
            'valid': False, 
            'reason': 'Missing HTTP/HTTPS protocol', 
            'domain': None,
            'error_code': 'MISSING_PROTOCOL'
        }
    
    # Enhanced domain extraction and validation
    try:
        parsed = urlparse(link)
        domain = parsed.netloc.lower()
        log_info(f"Enhanced link validation - Domain extracted: {domain}")
        
        # Comprehensive domain validation
        validation_result = _validate_terabox_domain(domain)
        if not validation_result['valid']:
            return {
                'valid': False,
                'reason': validation_result['reason'],
                'domain': domain,
                'error_code': 'INVALID_DOMAIN',
                'suggested_domains': validation_result.get('suggestions', [])
            }
        
        # Enhanced path validation
        path_validation = _validate_terabox_path(parsed.path, parsed.query)
        if not path_validation['valid']:
            return {
                'valid': False,
                'reason': path_validation['reason'],
                'domain': domain,
                'error_code': 'INVALID_PATH',
                'path_details': path_validation
            }
        
        # Successful validation
        log_info(f"Enhanced link validation successful - Domain: {domain}, Path: {parsed.path}")
        return {
            'valid': True, 
            'reason': 'Valid TeraBox link', 
            'domain': domain,
            'path_type': path_validation['path_type'],
            'surl': path_validation.get('surl'),
            'validation_score': 1.0
        }
        
    except Exception as e:
        log_error(e, "validate_terabox_link_enhanced")
        return {
            'valid': False, 
            'reason': 'Invalid URL format', 
            'domain': None,
            'error_code': 'PARSE_ERROR',
            'error_details': str(e)
        }


def _validate_terabox_domain(domain: str) -> Dict[str, Any]:
    """
    Validate TeraBox domain with suggestions for similar domains
    
    Args:
        domain: Domain to validate
        
    Returns:
        Dict with validation result and suggestions
    """
    # Known valid TeraBox domains (enhanced list)
    valid_domains = [
        'terabox.com', 'www.terabox.com',
        'terabox.app', 'www.terabox.app', 
        '1024terabox.com', 'www.1024terabox.com',
        '1024tera.com', 'www.1024tera.com',
        'terasharelink.com', 'www.terasharelink.com',
        'terafileshare.com', 'www.terafileshare.com',
        'teraboxapp.com', 'www.teraboxapp.com',
        'freeterabox.com', 'www.freeterabox.com',
        'nephobox.com', 'www.nephobox.com'
    ]
    
    if domain in valid_domains:
        return {'valid': True, 'reason': 'Known TeraBox domain'}
    
    # Find similar domains for suggestions
    suggestions = []
    for valid_domain in valid_domains:
        if domain in valid_domain or valid_domain in domain:
            suggestions.append(valid_domain)
    
    return {
        'valid': False,
        'reason': f'Unknown domain: {domain}',
        'suggestions': suggestions[:3]  # Limit to top 3 suggestions
    }


def _validate_terabox_path(path: str, query: str) -> Dict[str, Any]:
    """
    Validate TeraBox URL path structure
    
    Args:
        path: URL path component
        query: URL query component
        
    Returns:
        Dict with path validation result
    """
    # Valid path patterns with enhanced detection
    path_patterns = [
        (r'/s/([A-Za-z0-9_-]+)$', 'short_link'),
        (r'/sharing/link$', 'sharing_link')
    ]
    
    for pattern, path_type in path_patterns:
        match = re.match(pattern, path)
        if match:
            result = {'valid': True, 'reason': 'Valid path structure', 'path_type': path_type}
            
            if path_type == 'short_link':
                result['surl'] = match.group(1)
            elif path_type == 'sharing_link':
                # Check for surl parameter in query
                if 'surl=' in query:
                    surl_match = re.search(r'surl=([A-Za-z0-9_-]+)', query)
                    if surl_match:
                        result['surl'] = surl_match.group(1)
                    else:
                        return {'valid': False, 'reason': 'Invalid surl parameter format'}
                else:
                    return {'valid': False, 'reason': 'Sharing link missing surl parameter'}
            
            return result
    
    return {'valid': False, 'reason': f'Invalid path structure: {path}'}


def _deduplicate_links_with_stats(validated_links: List[str]) -> tuple:
    """
    Deduplicate links while preserving order and collecting statistics
    
    Args:
        validated_links: List of validated links
        
    Returns:
        Tuple of (unique_links, deduplication_stats)
    """
    log_info(f"Starting enhanced deduplication for {len(validated_links)} validated links")
    
    dedup_start_time = time.time()
    unique_links = []
    seen = set()
    duplicate_tracking = {}
    
    for link in validated_links:
        if link not in seen:
            unique_links.append(link)
            seen.add(link)
            log_info(f"Added unique link: {link}")
        else:
            # Track duplicate occurrences
            if link in duplicate_tracking:
                duplicate_tracking[link] += 1
            else:
                duplicate_tracking[link] = 2  # First duplicate (original + 1)
            log_info(f"Skipped duplicate link: {link}")
    
    dedup_duration = time.time() - dedup_start_time
    
    dedup_stats = {
        'original_count': len(validated_links),
        'unique_count': len(unique_links),
        'duplicates_removed': len(validated_links) - len(unique_links),
        'duplicate_details': duplicate_tracking,
        'deduplication_duration_ms': round(dedup_duration * 1000, 2),
        'deduplication_efficiency': (len(unique_links) / len(validated_links) * 100) if validated_links else 100
    }
    
    log_info(f"Deduplication completed - Efficiency: {dedup_stats['deduplication_efficiency']:.1f}%")
    return unique_links, dedup_stats


# ============================================================================
# CSV DATABASE UTILITIES
# ============================================================================

def save_links_to_csv_enhanced(links: List[str], csv_path: str = "utils/terebox.csv") -> Dict[str, Any]:
    """
    Enhanced CSV saving with comprehensive validation, logging, and statistics
    
    Args:
        links: List of TeraBox links to save
        csv_path: Path to CSV database file
        
    Returns:
        Dict with operation result and detailed statistics
    """
    log_info(f"[ENHANCED] Starting CSV save operation for {len(links)} links")
    log_info(f"Target CSV file: {csv_path}")
    
    operation_start_time = time.time()
    
    try:
        # Enhanced directory preparation
        csv_dir = os.path.dirname(csv_path)
        os.makedirs(csv_dir, exist_ok=True)
        log_info(f"CSV directory confirmed/created: {csv_dir}")
        
        # Enhanced timestamp generation with timezone info
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        timezone_info = datetime.now().astimezone().tzinfo
        log_info(f"Extraction timestamp generated: {timestamp} ({timezone_info})")
        
        # Enhanced existing data loading with validation
        existing_data, load_stats = _load_existing_csv_data_with_stats(csv_path)
        log_info(f"Existing data loaded - {load_stats['existing_count']} records, Load time: {load_stats['load_duration_ms']:.2f}ms")
        
        # Enhanced new link processing with metadata extraction
        new_rows, processing_stats = _process_new_links_with_metadata(links, existing_data, timestamp)
        log_info(f"New link processing completed - {len(new_rows)} new records, {processing_stats['duplicates_skipped']} duplicates")
        
        # Enhanced CSV writing with backup and validation
        write_result = _write_csv_with_backup_and_validation(csv_path, new_rows, load_stats['file_exists'])
        
        # Comprehensive operation statistics
        operation_duration = time.time() - operation_start_time
        
        operation_summary = {
            'success': write_result['success'],
            'operation_duration_ms': round(operation_duration * 1000, 2),
            'input_links': len(links),
            'new_records_added': len(new_rows),
            'duplicates_skipped': processing_stats['duplicates_skipped'],
            'existing_records': load_stats['existing_count'],
            'total_records_after': load_stats['existing_count'] + len(new_rows),
            'csv_file_path': csv_path,
            'csv_file_size_bytes': write_result.get('file_size_bytes', 0),
            'load_stats': load_stats,
            'processing_stats': processing_stats,
            'write_stats': write_result
        }
        
        log_info(f"[ENHANCED] CSV save operation completed successfully")
        log_info(f"Operation summary: {json.dumps(operation_summary, indent=2)}")
        
        return operation_summary
        
    except Exception as e:
        operation_duration = time.time() - operation_start_time
        log_error(e, "save_links_to_csv_enhanced")
        
        error_summary = {
            'success': False,
            'error': str(e),
            'operation_duration_ms': round(operation_duration * 1000, 2),
            'input_links': len(links),
            'csv_file_path': csv_path
        }
        
        log_info(f"CSV save operation failed: {json.dumps(error_summary, indent=2)}")
        return error_summary


def _load_existing_csv_data_with_stats(csv_path: str) -> tuple:
    """
    Load existing CSV data with comprehensive statistics
    
    Args:
        csv_path: Path to CSV file
        
    Returns:
        Tuple of (existing_links_set, load_statistics)
    """
    log_info(f"Loading existing CSV data with statistics from: {csv_path}")
    
    load_start_time = time.time()
    existing_links = set()
    existing_count = 0
    file_exists = False
    
    if os.path.exists(csv_path):
        file_exists = True
        file_size = os.path.getsize(csv_path)
        log_info(f"CSV file exists - Size: {file_size} bytes")
        
        try:
            with open(csv_path, 'r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                fieldnames = reader.fieldnames
                
                for row_num, row in enumerate(reader, 1):
                    link = row.get('Link', '')
                    if link:
                        existing_links.add(link)
                        existing_count += 1
                
                log_info(f"Loaded {existing_count} existing links from CSV - Fields: {fieldnames}")
                
        except Exception as e:
            log_error(e, "load_existing_csv_data")
            log_info("CSV file appears corrupted, starting fresh database")
            existing_links = set()
            existing_count = 0
    else:
        log_info("CSV file does not exist, will create new database")
    
    load_duration = time.time() - load_start_time
    
    load_stats = {
        'file_exists': file_exists,
        'existing_count': existing_count,
        'load_duration_ms': round(load_duration * 1000, 2),
        'file_size_bytes': os.path.getsize(csv_path) if file_exists else 0
    }
    
    return existing_links, load_stats


def _process_new_links_with_metadata(links: List[str], existing_links: set, timestamp: str) -> tuple:
    """
    Process new links with enhanced metadata extraction
    
    Args:
        links: List of links to process
        existing_links: Set of existing links for duplicate detection
        timestamp: Timestamp for record creation
        
    Returns:
        Tuple of (new_rows, processing_statistics)
    """
    log_info(f"Processing {len(links)} new links with enhanced metadata extraction")
    
    processing_start_time = time.time()
    new_rows = []
    skipped_duplicates = 0
    metadata_extraction_stats = {}
    
    for i, link in enumerate(links, 1):
        log_info(f"Processing link {i}/{len(links)}: {link}")
        
        if link not in existing_links:
            # Enhanced metadata extraction
            metadata = _extract_enhanced_link_metadata(link)
            
            # Create comprehensive CSV row
            row_data = {
                'ID': len(existing_links) + len(new_rows) + 1,
                'Link': link,
                'SURL': metadata['surl'],
                'Domain': metadata['domain'],
                'Extracted_At': timestamp,
                'Status': 'Pending',
                'Processed': 'No',
                'File_Name': '',
                'File_Size': '',
                'File_Type': '',
                'Download_Link': '',
                'Thumbnail': '',
                'Response_Data': '',
                'Processed_At': '',
                'Error_Message': '',
                # Enhanced metadata fields
                'Domain_Type': metadata['domain_type'],
                'URL_Format': metadata['url_format'],
                'Extract_Method': metadata['extract_method'],
                'Validation_Score': metadata['validation_score']
            }
            
            new_rows.append(row_data)
            metadata_extraction_stats[link] = metadata
            log_info(f"Added new link - ID: {row_data['ID']}, SURL: {metadata['surl']}, Domain: {metadata['domain']}")
            
        else:
            skipped_duplicates += 1
            log_info(f"Skipped duplicate link: {link}")
    
    processing_duration = time.time() - processing_start_time
    
    processing_stats = {
        'new_records': len(new_rows),
        'duplicates_skipped': skipped_duplicates,
        'processing_duration_ms': round(processing_duration * 1000, 2),
        'metadata_extraction_stats': metadata_extraction_stats,
        'processing_efficiency': (len(new_rows) / len(links) * 100) if links else 0
    }
    
    log_info(f"Link processing completed - Efficiency: {processing_stats['processing_efficiency']:.1f}%")
    return new_rows, processing_stats


def _extract_enhanced_link_metadata(link: str) -> Dict[str, Any]:
    """
    Extract enhanced metadata from TeraBox link
    
    Args:
        link: TeraBox link to analyze
        
    Returns:
        Dict with extracted metadata
    """
    log_info(f"Extracting enhanced metadata from link: {link[:50]}...")
    
    try:
        parsed = urlparse(link)
        domain = parsed.netloc
        
        # Extract SURL with multiple methods
        surl = None
        extract_method = 'unknown'
        
        if '/s/' in link:
            surl = link.split('/s/')[-1].split('?')[0]
            extract_method = 'path_extraction'
        elif 'surl=' in link:
            surl = link.split('surl=')[-1].split('&')[0]
            extract_method = 'query_extraction'
        else:
            surl = link.split('/')[-1] if '/' in link else link
            extract_method = 'fallback_extraction'
        
        # Determine domain type
        domain_type = _classify_domain_type(domain)
        
        # Determine URL format
        url_format = 'sharing_link' if '/sharing/link' in link else 'short_link'
        
        # Calculate validation score
        validation_score = _calculate_link_validation_score(link, domain, surl)
        
        metadata = {
            'surl': surl,
            'domain': domain,
            'domain_type': domain_type,
            'url_format': url_format,
            'extract_method': extract_method,
            'validation_score': validation_score,
            'path': parsed.path,
            'query': parsed.query
        }
        
        log_info(f"Enhanced metadata extracted: {metadata}")
        return metadata
        
    except Exception as e:
        log_error(e, "_extract_enhanced_link_metadata")
        return {
            'surl': link.split('/')[-1] if '/' in link else link,
            'domain': 'Unknown',
            'domain_type': 'unknown',
            'url_format': 'unknown',
            'extract_method': 'error_fallback',
            'validation_score': 0.0
        }


def _classify_domain_type(domain: str) -> str:
    """Classify TeraBox domain type"""
    domain_classifications = {
        'official': ['terabox.com', 'www.terabox.com', 'terabox.app', 'www.terabox.app'],
        'mirror': ['1024terabox.com', '1024tera.com', 'www.1024terabox.com', 'www.1024tera.com'],
        'share': ['terasharelink.com', 'terafileshare.com', 'www.terasharelink.com', 'www.terafileshare.com'],
        'alternative': ['teraboxapp.com', 'freeterabox.com', 'nephobox.com']
    }
    
    for domain_type, domains in domain_classifications.items():
        if domain in domains:
            return domain_type
    
    return 'unknown'


def _calculate_link_validation_score(link: str, domain: str, surl: str) -> float:
    """Calculate validation confidence score for link"""
    score = 0.0
    
    # Protocol score
    if link.startswith('https://'):
        score += 0.3
    elif link.startswith('http://'):
        score += 0.1
    
    # Domain score
    if 'terabox' in domain:
        score += 0.4
    elif any(keyword in domain for keyword in ['terashare', 'terafile']):
        score += 0.3
    
    # SURL score
    if surl and len(surl) > 5:
        score += 0.3
    
    return round(min(1.0, score), 2)


def _write_csv_with_backup_and_validation(csv_path: str, new_rows: List[Dict], file_exists: bool) -> Dict[str, Any]:
    """
    Write CSV with backup creation and validation
    
    Args:
        csv_path: Path to CSV file
        new_rows: New rows to write
        file_exists: Whether file already exists
        
    Returns:
        Dict with write operation results
    """
    log_info(f"Writing CSV with backup and validation - {len(new_rows)} new rows")
    
    write_start_time = time.time()
    
    try:
        # Create backup if file exists
        backup_path = None
        if file_exists and new_rows:
            backup_path = f"{csv_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            import shutil
            shutil.copy2(csv_path, backup_path)
            log_info(f"Backup created: {backup_path}")
        
        # Write new data
        if new_rows:
            fieldnames = [
                'ID', 'Link', 'SURL', 'Domain', 'Extracted_At', 'Status', 'Processed', 
                'File_Name', 'File_Size', 'File_Type', 'Download_Link', 'Thumbnail', 
                'Response_Data', 'Processed_At', 'Error_Message',
                # Enhanced fields
                'Domain_Type', 'URL_Format', 'Extract_Method', 'Validation_Score'
            ]
            
            with open(csv_path, 'a', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                
                # Write header if file is new
                if not file_exists:
                    writer.writeheader()
                    log_info("CSV header written to new file")
                
                # Write new rows
                writer.writerows(new_rows)
                log_info(f"Successfully wrote {len(new_rows)} new rows to CSV")
        
        # Final file statistics
        final_size = os.path.getsize(csv_path)
        write_duration = time.time() - write_start_time
        
        write_result = {
            'success': True,
            'records_written': len(new_rows),
            'file_size_bytes': final_size,
            'write_duration_ms': round(write_duration * 1000, 2),
            'backup_created': backup_path is not None,
            'backup_path': backup_path
        }
        
        log_info(f"CSV write operation completed successfully: {write_result}")
        return write_result
        
    except Exception as e:
        write_duration = time.time() - write_start_time
        log_error(e, "_write_csv_with_backup_and_validation")
        
        return {
            'success': False,
            'error': str(e),
            'write_duration_ms': round(write_duration * 1000, 2),
            'records_attempted': len(new_rows)
        }


# ============================================================================
# PERFORMANCE AND MONITORING UTILITIES
# ============================================================================

def monitor_component_performance(component_name: str, operation_name: str):
    """
    Context manager for monitoring component performance
    
    Args:
        component_name: Name of the component
        operation_name: Name of the operation being monitored
        
    Usage:
        with monitor_component_performance('TextProcessor', 'link_extraction'):
            # Component operation code here
            pass
    """
    class PerformanceMonitor:
        def __init__(self, component: str, operation: str):
            self.component = component
            self.operation = operation
            self.start_time = None
        
        def __enter__(self):
            self.start_time = time.time()
            log_info(f"[PERFORMANCE] Starting {self.component}.{self.operation}")
            return self
        
        def __exit__(self, exc_type, exc_val, exc_tb):
            duration = time.time() - self.start_time
            
            if exc_type is None:
                log_info(f"[PERFORMANCE] Completed {self.component}.{self.operation} in {duration:.3f}s")
            else:
                log_error(exc_val, f"[PERFORMANCE] Failed {self.component}.{self.operation} after {duration:.3f}s")
    
    return PerformanceMonitor(component_name, operation_name)


def create_operation_statistics(operation_name: str, start_time: float, 
                               success: bool, **kwargs) -> Dict[str, Any]:
    """
    Create comprehensive operation statistics
    
    Args:
        operation_name: Name of the operation
        start_time: Operation start time
        success: Whether operation was successful
        **kwargs: Additional statistics to include
        
    Returns:
        Dict with comprehensive operation statistics
    """
    end_time = time.time()
    duration = end_time - start_time
    
    stats = {
        'operation': operation_name,
        'success': success,
        'start_time': datetime.fromtimestamp(start_time).isoformat(),
        'end_time': datetime.fromtimestamp(end_time).isoformat(),
        'duration_seconds': round(duration, 3),
        'duration_ms': round(duration * 1000, 2),
        'timestamp': datetime.now().isoformat()
    }
    
    # Add additional statistics
    stats.update(kwargs)
    
    log_info(f"Operation statistics created for {operation_name}: {stats}")
    return stats


# ============================================================================
# ERROR HANDLING UTILITIES
# ============================================================================

def create_enhanced_error_info(error: Exception, context: str, **additional_info) -> Dict[str, Any]:
    """
    Create enhanced error information for debugging
    
    Args:
        error: Exception that occurred
        context: Context where error occurred
        **additional_info: Additional error context information
        
    Returns:
        Dict with comprehensive error information
    """
    log_error(error, f"create_enhanced_error_info - {context}")
    
    error_info = {
        'error_type': type(error).__name__,
        'error_message': str(error),
        'context': context,
        'timestamp': datetime.now().isoformat(),
        'additional_info': additional_info
    }
    
    # Add stack trace if available
    import traceback
    error_info['stack_trace'] = traceback.format_exc()
    
    log_info(f"Enhanced error info created: {error_info}")
    return error_info


# ============================================================================
# FACTORY FUNCTIONS
# ============================================================================

def get_rapidapi_utils_instance():
    """Get singleton instance of RapidAPI utilities"""
    if not hasattr(get_rapidapi_utils_instance, '_instance'):
        get_rapidapi_utils_instance._instance = True
        log_info("RapidAPI utilities instance created")
    
    return get_rapidapi_utils_instance._instance
