# 🎯 CSV Manager Usage Example

## Complete Workflow Demonstration

### Step 1: Extract Links from Text
1. **Navigate to RapidAPI Mode** (💳 RapidAPI Mode page)
2. **Enter your API key** and validate it
3. **Go to Text Processor tab** (📝 Text Processor)
4. **Paste sample text** with TeraBox links:

```
Check out these awesome files:
Video 👉 https://terasharelink.com/s/1FQd8x4-bpyTN8TnV6APOLA
Document 👉 https://www.terabox.app/sharing/link?surl=ABC123DEF456
Music 👉 https://terabox.com/s/sample_link_123
Software 👉 https://1024terabox.com/s/music_file_xyz
```

5. **Click "🔍 Extract & Process Links"**
6. **Observe the results**:
   - ✅ Found 4 TeraBox links!
   - 💾 Links saved to terebox.csv successfully!
   - See extracted links in a table format

### Step 2: Manage Links in CSV Manager
1. **Switch to CSV Manager tab** (📊 CSV Manager)
2. **View Database Statistics**:
   - 📊 Total Links: 4
   - ⏳ Pending: 4
   - ✅ Processed: 0
   - 🌐 Domains: 4

3. **Explore Filtering Options**:
   - Filter by Status: "Pending" to see unprocessed links
   - Filter by Domain: Select specific TeraBox domains
   - Search: Enter SURL or part of link to find specific entries

### Step 3: Bulk Process All Links
1. **Click "📊 Get File Info for All Links"**
2. **Watch the processing**:
   - 🔄 Processing 4 links from CSV...
   - Progress indicators and status updates
   - ✅ Successfully processed X links!

3. **View Results**:
   - Success/failure metrics
   - Individual file details in expandable cards
   - Download and direct link options for each file

### Step 4: Export and Manage Data
1. **Export filtered data**:
   - Click "📥 Export Filtered Data"
   - Download CSV with current filter results
   - Timestamped filename for organization

2. **Clear database if needed**:
   - Click "🗑️ Clear CSV Database"
   - Confirm action (safety measure)
   - Fresh start for new link collections

## Sample CSV Structure

After extraction, your `utils/terebox.csv` will look like:

```csv
ID,Link,SURL,Domain,Extracted_At,Status,Processed
1,https://terasharelink.com/s/1FQd8x4-bpyTN8TnV6APOLA,1FQd8x4-bpyTN8TnV6APOLA,terasharelink.com,2025-09-19 13:20:00,Pending,No
2,https://www.terabox.app/sharing/link?surl=ABC123DEF456,link?surl=ABC123DEF456,www.terabox.app,2025-09-19 13:20:00,Pending,No
3,https://terabox.com/s/sample_link_123,sample_link_123,terabox.com,2025-09-19 13:20:00,Pending,No
4,https://1024terabox.com/s/music_file_xyz,music_file_xyz,1024terabox.com,2025-09-19 13:20:00,Pending,No
```

## Key Benefits

### 🔄 Persistent Storage
- Links are saved automatically when extracted
- No need to re-extract from the same text
- Build up a personal TeraBox link library

### 📊 Bulk Processing
- Process hundreds of links with one click
- Efficient API usage with batch operations
- Track processing status for each link

### 🔍 Advanced Management
- Filter by processing status or domain
- Search through your link collection
- Export subsets of your data

### 🎯 Workflow Efficiency
- Extract once, process anytime
- No manual copy-paste between tabs
- Seamless integration between text processing and file operations

## Tips for Best Results

1. **API Key**: Ensure you have a valid RapidAPI key for processing
2. **Text Format**: Any text format works - the system extracts all TeraBox links automatically
3. **Batch Size**: The system handles any number of links efficiently
4. **Data Backup**: Use the export feature to backup your link collections
5. **Regular Cleanup**: Clear old processed links periodically to maintain performance

---

*This workflow demonstrates the complete integration between text processing and CSV-based link management, providing a seamless experience for handling large collections of TeraBox links.*
