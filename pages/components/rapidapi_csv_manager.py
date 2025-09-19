"""
RapidAPI CSV Manager Component

This component handles CSV database management for TeraBox links including:
- CSV data loading and display
- Advanced filtering and searching
- Bulk processing operations
- Data analytics and visualization
- Export and import functionality
- Link status management

Component Features:
- Comprehensive data filtering
- Visual analytics dashboard
- Bulk operations with progress
- Advanced search capabilities
- Data export functionality
- Status tracking and management
"""

import streamlit as st
import pandas as pd
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from utils.state_manager import StateManager
from utils.browser_utils import open_direct_file_link, display_browser_open_result
from utils.config import log_info, log_error
import json


class RapidAPICSVManager:
    """
    CSV Database Manager Component for RapidAPI Mode
    
    Provides comprehensive management of TeraBox links database with
    advanced filtering, analytics, and bulk operations.
    
    Features:
    - Advanced data filtering
    - Visual analytics dashboard
    - Bulk processing operations
    - Search and export functionality
    - Status tracking and management
    - Data quality monitoring
    """
    
    def __init__(self):
        """Initialize the CSV Manager component"""
        log_info("Initializing RapidAPICSVManager component")
    
    def render_csv_manager_section(self) -> None:
        """
        Render the complete CSV manager section
        
        This includes:
        - Description and features
        - Database statistics
        - Filtering interface
        - Data display
        - Bulk operations
        """
        log_info("Rendering CSV manager section")
        
        st.subheader("📊 CSV Manager - TeraBox Links Database")
        
        # Description
        self._render_description()
        
        # Load and display data
        csv_data = self._load_csv_data()
        
        if csv_data:
            # Enhanced database statistics
            self._render_database_statistics(csv_data)
            
            # Visual analytics
            self._render_visual_analytics(csv_data)
            
            # Filtering interface
            filtered_data = self._render_filtering_interface(csv_data)
            
            # Data display
            self._render_data_display(filtered_data, len(csv_data))
            
            # Bulk operations
            self._render_bulk_operations(filtered_data)
        else:
            self._render_empty_state()
    
    def _render_description(self) -> None:
        """Render CSV manager description"""
        st.info("""
        **📊 CSV Manager** - Manage your saved TeraBox links:
        - ✅ View all extracted links from terebox.csv with detailed file information
        - ✅ Bulk process saved links with real-time progress tracking
        - ✅ Filter and search through your link database
        - ✅ Export and manage your TeraBox link collection
        - ✅ Track processing status and comprehensive response data
        - 🌐 **NEW:** Open all download links in browser with one click
        - 📊 **NEW:** View thumbnails, file sizes, and complete API responses
        - 🔄 **NEW:** Reset failed links for retry (only 200 status = processed)
        - 📈 **NEW:** Enhanced analytics with proper status code tracking
        """)
    
    def _load_csv_data(self) -> List[Dict]:
        """Load CSV data with schema migration"""
        log_info("Loading CSV data with automatic schema migration")
        
        from pages.RapidAPI_Mode import load_links_from_csv
        csv_data = load_links_from_csv()
        
        # Check if schema migration occurred and notify user
        if csv_data and len(csv_data) > 0:
            sample_row = csv_data[0]
            has_extended_schema = 'File_Name' in sample_row
            if has_extended_schema:
                st.success("✅ CSV database loaded successfully with enhanced schema support!")
            else:
                st.info("ℹ️ CSV database loaded. Enhanced features will be available after processing links.")
        
        log_info(f"CSV data loaded - {len(csv_data)} records")
        return csv_data
    
    def _render_database_statistics(self, csv_data: List[Dict]) -> None:
        """Render enhanced database statistics"""
        log_info("Rendering database statistics")
        
        st.subheader("📈 Enhanced Database Statistics")
        
        # Calculate comprehensive statistics
        total_links = len(csv_data)
        processed_count = len([row for row in csv_data if row.get('Processed', 'No') == 'Yes'])
        pending_count = len([row for row in csv_data if row.get('Processed', 'No') == 'No'])
        success_count = len([row for row in csv_data if row.get('Status') == 'Processed' and row.get('Processed') == 'Yes'])
        failed_count = len([row for row in csv_data if row.get('Status') == 'Failed' and row.get('Processed') == 'No'])
        opened_count = len([row for row in csv_data if row.get('Status') == 'Opened'])
        unique_domains = len(set(row.get('Domain', 'Unknown') for row in csv_data))
        
        # Calculate percentages
        processed_percentage = (processed_count / total_links * 100) if total_links > 0 else 0
        success_rate = (success_count / processed_count * 100) if processed_count > 0 else 0
        
        # Basic statistics row
        col_stat1, col_stat2, col_stat3, col_stat4, col_stat5 = st.columns(5)
        
        with col_stat1:
            st.metric("📊 Total Links", total_links)
        with col_stat2:
            st.metric("✅ Processed", processed_count, delta=f"{processed_percentage:.1f}% of total")
        with col_stat3:
            st.metric("⏳ Pending", pending_count)
        with col_stat4:
            st.metric("🎯 Success Rate", f"{success_rate:.1f}%", delta=f"{success_count} successful")
        with col_stat5:
            st.metric("🌐 Domains", unique_domains)
        
        # Advanced statistics
        self._render_advanced_statistics(csv_data, success_count, failed_count, opened_count)
    
    def _render_advanced_statistics(self, csv_data: List[Dict], success_count: int, 
                                  failed_count: int, opened_count: int) -> None:
        """Render advanced statistics section"""
        st.markdown("### 📊 Detailed Analytics")
        col_advanced1, col_advanced2, col_advanced3, col_advanced4 = st.columns(4)
        
        with col_advanced1:
            st.metric("🔄 Successfully Processed", success_count)
            st.metric("❌ Failed Processing", failed_count)
        
        with col_advanced2:
            st.metric("🌐 Links Opened", opened_count)
            processed_files_with_size = [row for row in csv_data if row.get('File_Size') and row.get('File_Size') != '']
            st.metric("📏 Files with Size Info", len(processed_files_with_size))
        
        with col_advanced3:
            # Domain distribution
            domain_counts = {}
            for row in csv_data:
                domain = row.get('Domain', 'Unknown')
                domain_counts[domain] = domain_counts.get(domain, 0) + 1
            top_domain = max(domain_counts, key=domain_counts.get) if domain_counts else 'None'
            st.metric("🏆 Top Domain", top_domain, delta=f"{domain_counts.get(top_domain, 0)} links")
        
        with col_advanced4:
            # Time-based statistics
            self._render_time_statistics(csv_data)
    
    def _render_time_statistics(self, csv_data: List[Dict]) -> None:
        """Render time-based statistics"""
        recent_links = [row for row in csv_data if row.get('Extracted_At')]
        if recent_links:
            try:
                dates = [datetime.strptime(row['Extracted_At'], "%Y-%m-%d %H:%M:%S") 
                        for row in recent_links if row.get('Extracted_At')]
                if dates:
                    most_recent = max(dates)
                    days_since = (datetime.now() - most_recent).days
                    st.metric("📅 Last Added", f"{days_since} days ago")
            except:
                st.metric("📅 Last Added", "Unknown")
        else:
            st.metric("📅 Last Added", "No data")
    
    def _render_visual_analytics(self, csv_data: List[Dict]) -> None:
        """Render visual analytics section"""
        log_info("Rendering visual analytics")
        
        st.markdown("### 📈 Visual Analytics")
        
        analytics_tab1, analytics_tab2, analytics_tab3 = st.tabs([
            "📊 Status Distribution", 
            "🌐 Domain Analysis", 
            "📅 Timeline Analysis"
        ])
        
        with analytics_tab1:
            self._render_status_distribution(csv_data)
        
        with analytics_tab2:
            self._render_domain_analysis(csv_data)
        
        with analytics_tab3:
            self._render_timeline_analysis(csv_data)
    
    def _render_status_distribution(self, csv_data: List[Dict]) -> None:
        """Render status distribution analytics"""
        log_info("Rendering status distribution analytics")
        
        # Calculate status distribution
        pending_count = len([row for row in csv_data if row.get('Processed', 'No') == 'No'])
        success_count = len([row for row in csv_data if row.get('Status') == 'Processed' and row.get('Processed') == 'Yes'])
        failed_count = len([row for row in csv_data if row.get('Status') == 'Failed' and row.get('Processed') == 'No'])
        opened_count = len([row for row in csv_data if row.get('Status') == 'Opened'])
        
        status_data = {
            'Pending (Not Called)': pending_count,
            'Successfully Processed (200)': success_count,
            'API Failed (Non-200)': failed_count,
            'Links Opened': opened_count
        }
        
        # Remove zero values for cleaner chart
        status_data = {k: v for k, v in status_data.items() if v > 0}
        
        if status_data:
            col_chart1, col_chart2 = st.columns([2, 1])
            
            with col_chart1:
                chart_df = pd.DataFrame(list(status_data.items()), columns=['Status', 'Count'])
                st.bar_chart(chart_df.set_index('Status'))
            
            with col_chart2:
                st.markdown("**📊 Status Breakdown:**")
                total_links = len(csv_data)
                for status, count in status_data.items():
                    percentage = (count / total_links * 100) if total_links > 0 else 0
                    st.write(f"**{status}:** {count} ({percentage:.1f}%)")
                
                # Add explanation
                st.markdown("---")
                st.markdown("**📋 Status Definitions:**")
                st.caption("• **Pending**: API not called yet")
                st.caption("• **Successfully Processed**: API returned 200 with valid data")
                st.caption("• **API Failed**: API returned non-200 status")
                st.caption("• **Links Opened**: Successfully opened in browser")
        else:
            st.info("No status data available for visualization")
    
    def _render_domain_analysis(self, csv_data: List[Dict]) -> None:
        """Render domain distribution analysis"""
        log_info("Rendering domain analysis")
        
        # Calculate domain distribution
        domain_counts = {}
        for row in csv_data:
            domain = row.get('Domain', 'Unknown')
            domain_counts[domain] = domain_counts.get(domain, 0) + 1
        
        if domain_counts:
            col_domain1, col_domain2 = st.columns([2, 1])
            
            with col_domain1:
                domain_df = pd.DataFrame(list(domain_counts.items()), columns=['Domain', 'Count'])
                domain_df = domain_df.sort_values('Count', ascending=True)
                st.bar_chart(domain_df.set_index('Domain'))
            
            with col_domain2:
                st.markdown("**🌐 Domain Distribution:**")
                sorted_domains = sorted(domain_counts.items(), key=lambda x: x[1], reverse=True)
                total_links = len(csv_data)
                for domain, count in sorted_domains[:10]:
                    percentage = (count / total_links * 100) if total_links > 0 else 0
                    st.write(f"**{domain}:** {count} ({percentage:.1f}%)")
        else:
            st.info("No domain data available for visualization")
    
    def _render_timeline_analysis(self, csv_data: List[Dict]) -> None:
        """Render timeline analysis"""
        log_info("Rendering timeline analysis")
        
        # Extract timeline data
        timeline_data = []
        for row in csv_data:
            if row.get('Extracted_At'):
                try:
                    date = datetime.strptime(row['Extracted_At'], "%Y-%m-%d %H:%M:%S")
                    timeline_data.append(date.date())
                except:
                    continue
        
        if timeline_data:
            # Count links by date
            date_counts = {}
            for date in timeline_data:
                date_counts[date] = date_counts.get(date, 0) + 1
            
            if date_counts:
                col_timeline1, col_timeline2 = st.columns([2, 1])
                
                with col_timeline1:
                    timeline_df = pd.DataFrame(list(date_counts.items()), columns=['Date', 'Links Added'])
                    timeline_df = timeline_df.sort_values('Date')
                    st.line_chart(timeline_df.set_index('Date'))
                
                with col_timeline2:
                    st.markdown("**📅 Timeline Summary:**")
                    sorted_dates = sorted(date_counts.items(), key=lambda x: x[1], reverse=True)
                    st.write(f"**Most Active Day:** {sorted_dates[0][0]} ({sorted_dates[0][1]} links)")
                    st.write(f"**Total Days:** {len(date_counts)}")
                    st.write(f"**Average per Day:** {sum(date_counts.values()) / len(date_counts):.1f}")
        else:
            st.info("No timeline data available for visualization")
    
    def _render_filtering_interface(self, csv_data: List[Dict]) -> List[Dict]:
        """Render advanced filtering interface and apply filters"""
        log_info("Rendering filtering interface")
        
        st.markdown("---")
        st.subheader("🔍 Advanced Filter & Search")
        
        # Basic filters
        status_filter, domain_filter, processed_filter = self._render_basic_filters(csv_data)
        
        # Advanced search
        search_term, file_type_filter, size_range = self._render_advanced_search(csv_data)
        
        # Date filters
        date_range, processing_date_filter = self._render_date_filters(csv_data)
        
        # Quick filter buttons
        self._render_quick_filters()
        
        # Apply filters
        filtered_data = self._apply_filters(
            csv_data, status_filter, domain_filter, processed_filter,
            search_term, file_type_filter, size_range, date_range, processing_date_filter
        )
        
        return filtered_data
    
    def _render_basic_filters(self, csv_data: List[Dict]) -> tuple:
        """Render basic filter controls"""
        with st.expander("🎯 Basic Filters", expanded=True):
            col_basic1, col_basic2, col_basic3 = st.columns(3)
            
            with col_basic1:
                all_statuses = sorted(set([row.get('Status', 'Pending') for row in csv_data if row.get('Status')]))
                status_filter = st.selectbox(
                    "Filter by Status:",
                    ["All"] + all_statuses,
                    key="csv_status_filter"
                )
            
            with col_basic2:
                all_domains = sorted(set(row.get('Domain', 'Unknown') for row in csv_data))
                domain_filter = st.selectbox(
                    "Filter by Domain:",
                    ["All"] + all_domains,
                    key="csv_domain_filter"
                )
            
            with col_basic3:
                processed_filter = st.selectbox(
                    "Filter by Processing:",
                    ["All", "Processed", "Not Processed"],
                    key="csv_processed_filter"
                )
        
        return status_filter, domain_filter, processed_filter
    
    def _render_advanced_search(self, csv_data: List[Dict]) -> tuple:
        """Render advanced search controls"""
        with st.expander("🔍 Advanced Search", expanded=True):
            col_search1, col_search2 = st.columns(2)
            
            with col_search1:
                search_term = st.text_input(
                    "🔍 Search in Links/SURL/File Names:",
                    placeholder="Enter search term...",
                    key="csv_search"
                )
                
                # File type filter
                processed_files = [row for row in csv_data if row.get('File_Type')]
                if processed_files:
                    file_types = sorted(set([row.get('File_Type', '') for row in processed_files if row.get('File_Type')]))
                    file_type_filter = st.selectbox(
                        "Filter by File Type:",
                        ["All"] + file_types,
                        key="csv_file_type_filter"
                    )
                else:
                    file_type_filter = "All"
            
            with col_search2:
                # File size filter
                size_range = self._render_size_filter(csv_data)
        
        return search_term, file_type_filter, size_range
    
    def _render_size_filter(self, csv_data: List[Dict]) -> Optional[tuple]:
        """Render file size filter"""
        files_with_size = [row for row in csv_data if row.get('File_Size') and row.get('File_Size') != '']
        
        if files_with_size:
            st.markdown("**📏 File Size Filter:**")
            size_filter_enabled = st.checkbox("Enable size filtering", key="size_filter_enabled")
            
            if size_filter_enabled:
                # Parse file sizes and create range slider
                size_values = []
                for row in files_with_size:
                    size_str = row.get('File_Size', '')
                    try:
                        if 'MB' in size_str:
                            size_mb = float(size_str.replace('MB', '').strip())
                        elif 'GB' in size_str:
                            size_mb = float(size_str.replace('GB', '').strip()) * 1024
                        elif 'KB' in size_str:
                            size_mb = float(size_str.replace('KB', '').strip()) / 1024
                        else:
                            size_mb = 0
                        size_values.append(size_mb)
                    except:
                        continue
                
                if size_values:
                    min_size, max_size = min(size_values), max(size_values)
                    return st.slider(
                        "Size Range (MB):",
                        min_value=float(min_size),
                        max_value=float(max_size),
                        value=(float(min_size), float(max_size)),
                        key="csv_size_range"
                    )
        
        return None
    
    def _render_date_filters(self, csv_data: List[Dict]) -> tuple:
        """Render date filtering controls"""
        with st.expander("📅 Date & Time Filters", expanded=False):
            col_date1, col_date2 = st.columns(2)
            
            with col_date1:
                date_range = self._render_extraction_date_filter(csv_data)
            
            with col_date2:
                processing_date_filter = self._render_processing_date_filter(csv_data)
        
        return date_range, processing_date_filter
    
    def _render_extraction_date_filter(self, csv_data: List[Dict]) -> Optional[tuple]:
        """Render extraction date range filter"""
        st.markdown("**📅 Extraction Date Range:**")
        dates_available = [row for row in csv_data if row.get('Extracted_At')]
        
        if dates_available:
            try:
                all_dates = []
                for row in dates_available:
                    try:
                        date = datetime.strptime(row['Extracted_At'], "%Y-%m-%d %H:%M:%S").date()
                        all_dates.append(date)
                    except:
                        continue
                
                if all_dates:
                    min_date, max_date = min(all_dates), max(all_dates)
                    return st.date_input(
                        "Select date range:",
                        value=(min_date, max_date),
                        min_value=min_date,
                        max_value=max_date,
                        key="csv_date_range"
                    )
            except:
                pass
        else:
            st.info("No extraction dates available")
        
        return None
    
    def _render_processing_date_filter(self, csv_data: List[Dict]) -> str:
        """Render processing date filter"""
        st.markdown("**⏰ Processing Date Filter:**")
        processed_dates = [row for row in csv_data if row.get('Processed_At')]
        
        if processed_dates:
            return st.selectbox(
                "Show files processed:",
                ["All time", "Today", "This week", "This month"],
                key="csv_processing_date_filter"
            )
        else:
            st.info("No processing dates available")
            return "All time"
    
    def _render_quick_filters(self) -> None:
        """Render quick filter buttons"""
        st.markdown("**⚡ Quick Filters:**")
        col_quick1, col_quick2, col_quick3, col_quick4, col_quick5 = st.columns(5)
        
        with col_quick1:
            if st.button("🔄 Show All", key="quick_all"):
                st.query_params.clear()
                st.rerun()
        
        with col_quick2:
            if st.button("⏳ Pending Only", key="quick_pending"):
                st.query_params["filter"] = "pending"
                st.rerun()
        
        with col_quick3:
            if st.button("✅ Processed Only", key="quick_processed"):
                st.query_params["filter"] = "processed"
                st.rerun()
        
        with col_quick4:
            if st.button("❌ Failed Only", key="quick_failed"):
                st.query_params["filter"] = "failed"
                st.rerun()
        
        with col_quick5:
            if st.button("🌐 Opened Links", key="quick_opened"):
                st.query_params["filter"] = "opened"
                st.rerun()
    
    def _apply_filters(self, csv_data: List[Dict], status_filter: str, domain_filter: str,
                      processed_filter: str, search_term: str, file_type_filter: str,
                      size_range: Optional[tuple], date_range: Optional[tuple],
                      processing_date_filter: str) -> List[Dict]:
        """Apply all filters to CSV data"""
        log_info("Applying filters to CSV data")
        
        filtered_data = csv_data.copy()
        original_count = len(filtered_data)
        
        # Apply quick filters from URL parameters
        self._apply_quick_filters(status_filter, processed_filter)
        
        # Apply individual filters
        if status_filter != "All":
            filtered_data = [row for row in filtered_data if row.get('Status', 'Pending') == status_filter]
        
        if domain_filter != "All":
            filtered_data = [row for row in filtered_data if row.get('Domain', 'Unknown') == domain_filter]
        
        if processed_filter != "All":
            if processed_filter == "Processed":
                filtered_data = [row for row in filtered_data if row.get('Processed', 'No') == 'Yes']
            elif processed_filter == "Not Processed":
                filtered_data = [row for row in filtered_data if row.get('Processed', 'No') == 'No']
        
        # Apply search filter
        if search_term:
            search_lower = search_term.lower()
            filtered_data = [row for row in filtered_data 
                           if search_lower in row.get('SURL', '').lower() 
                           or search_lower in row.get('Link', '').lower()
                           or search_lower in row.get('File_Name', '').lower()]
        
        # Apply other filters
        if file_type_filter and file_type_filter != "All":
            filtered_data = [row for row in filtered_data if row.get('File_Type', '') == file_type_filter]
        
        # Show filter summary
        filters_applied = original_count - len(filtered_data)
        if filters_applied > 0:
            st.info(f"🎯 Filters applied: Showing {len(filtered_data)} of {original_count} total links ({filters_applied} filtered out)")
        
        log_info(f"Filters applied - Original: {original_count}, Filtered: {len(filtered_data)}")
        return filtered_data
    
    def _apply_quick_filters(self, status_filter: str, processed_filter: str) -> None:
        """Apply quick filters based on URL parameters"""
        quick_filter = st.query_params.get("filter", None)
        if quick_filter:
            st.info(f"🎯 Quick filter active: {quick_filter.title()}")
    
    def _render_data_display(self, filtered_data: List[Dict], total_count: int) -> None:
        """Render filtered data display"""
        log_info(f"Rendering data display for {len(filtered_data)} filtered records")
        
        st.markdown("---")
        st.subheader(f"📋 Links Database ({len(filtered_data)} of {total_count} shown)")
        
        if filtered_data:
            # Create DataFrame for display
            display_df = pd.DataFrame(filtered_data)
            
            if not display_df.empty:
                # Customize columns for display
                display_df['Link_Short'] = display_df['Link'].apply(
                    lambda x: x[:50] + '...' if len(str(x)) > 50 else str(x)
                )
                
                display_df['File_Info'] = display_df.apply(
                    lambda row: f"{row.get('File_Name', '')[:30]}..." if row.get('File_Name') else 'Not processed',
                    axis=1
                )
                
                # Display table
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
                
                # Detailed file information section
                self._render_detailed_file_info(filtered_data)
        else:
            st.info("ℹ️ No links match your current filters. Try adjusting the filter criteria.")
    
    def _render_detailed_file_info(self, filtered_data: List[Dict]) -> None:
        """Render detailed file information section"""
        st.markdown("---")
        st.subheader("🔍 Detailed File Information")
        
        # Filter for processed files only
        processed_files = [row for row in filtered_data 
                          if row.get('Processed') == 'Yes' and row.get('Status') == 'Processed']
        
        if processed_files:
            selected_file_id = st.selectbox(
                "Select a processed file to view details:",
                options=[f"ID {row['ID']}: {row.get('File_Name', row.get('SURL', 'Unknown'))}" for row in processed_files],
                key="csv_file_selector"
            )
            
            if selected_file_id:
                self._display_selected_file_details(selected_file_id, processed_files)
        else:
            st.info("ℹ️ No processed files to display details for. Process some links first!")
    
    def _display_selected_file_details(self, selected_file_id: str, processed_files: List[Dict]) -> None:
        """Display details for selected file"""
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
                        st.text_area("Raw Response Data:", value=selected_file['Response_Data'], 
                                   height=200, key=f"raw_data_{file_id}")
    
    def _render_bulk_operations(self, filtered_data: List[Dict]) -> None:
        """Render bulk operation buttons"""
        log_info("Rendering bulk operations section")
        
        st.markdown("---")
        st.subheader("🎯 Bulk Actions")
        
        col_action1, col_action2, col_action3, col_action4, col_action5 = st.columns(5)
        
        with col_action1:
            self._render_process_all_button(filtered_data)
        
        with col_action2:
            self._render_export_button(filtered_data)
        
        with col_action3:
            self._render_open_all_button(filtered_data)
        
        with col_action4:
            self._render_reset_failed_button(filtered_data)
        
        with col_action5:
            self._render_clear_database_button()
    
    def _render_process_all_button(self, filtered_data: List[Dict]) -> None:
        """Render process all links button"""
        if st.button("📊 Get File Info for All Links", type="primary", key="csv_process_all"):
            links_to_process = [row['Link'] for row in filtered_data if row.get('Processed', 'No') == 'No']
            
            if links_to_process:
                self._handle_bulk_csv_processing(links_to_process)
            else:
                st.info("ℹ️ No unprocessed links found in current filter")
    
    def _render_export_button(self, filtered_data: List[Dict]) -> None:
        """Render export data button"""
        if st.button("📥 Export Filtered Data", key="csv_export"):
            if filtered_data:
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
    
    def _render_open_all_button(self, filtered_data: List[Dict]) -> None:
        """Render open all links button"""
        if st.button("🌐 Open All Links", key="csv_open_all"):
            processed_files_with_links = [
                row for row in filtered_data 
                if row.get('Processed') == 'Yes' 
                and row.get('Status') == 'Processed' 
                and row.get('Download_Link')
            ]
            
            if processed_files_with_links:
                self._handle_open_all_links(processed_files_with_links)
            else:
                st.info("ℹ️ No processed files with download links found. Process some links first!")
    
    def _render_reset_failed_button(self, filtered_data: List[Dict]) -> None:
        """Render reset failed links button"""
        if st.button("🔄 Reset Failed Links", key="csv_reset_failed"):
            failed_links = [row for row in filtered_data 
                          if row.get('Status') == 'Failed' and row.get('Processed') == 'No']
            
            if failed_links:
                with st.spinner(f"🔄 Resetting {len(failed_links)} failed links to pending..."):
                    from pages.RapidAPI_Mode import reset_failed_links_to_pending
                    if reset_failed_links_to_pending():
                        st.success(f"✅ Reset {len(failed_links)} failed links to pending status!")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("❌ Failed to reset links")
            else:
                st.info("ℹ️ No failed links found to reset")
    
    def _render_clear_database_button(self) -> None:
        """Render clear database button"""
        if st.button("🗑️ Clear CSV Database", key="csv_clear_all"):
            if st.session_state.get('confirm_csv_clear', False):
                try:
                    import os
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
    
    def _handle_bulk_csv_processing(self, links_to_process: List[str]) -> None:
        """Handle bulk processing of CSV links"""
        log_info(f"Starting bulk CSV processing for {len(links_to_process)} links")
        
        processing_key = 'processing_csv_links'
        st.session_state[processing_key] = True
        
        # Implementation would be similar to bulk processor
        # This is a placeholder for the actual implementation
        st.info("🔄 Bulk CSV processing implementation would go here")
    
    def _handle_open_all_links(self, processed_files_with_links: List[Dict]) -> None:
        """Handle opening all processed links"""
        log_info(f"Opening all links for {len(processed_files_with_links)} files")
        
        # Implementation would handle opening all links with progress
        st.info("🌐 Open all links implementation would go here")
    
    def _render_empty_state(self) -> None:
        """Render empty state when no CSV data is available"""
        st.info("📝 No links found in terebox.csv. Use the Text Processor tab to extract and save some links first!")
        
        if st.button("📝 Go to Text Processor", key="goto_text_processor"):
            st.info("💡 Switch to the 'Text Processor' tab above to extract TeraBox links from text.")


def create_csv_manager() -> RapidAPICSVManager:
    """Factory function to create CSV Manager component"""
    log_info("Creating RapidAPICSVManager component instance")
    return RapidAPICSVManager()
