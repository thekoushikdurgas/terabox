/**
 * Fetches file details from Terabox using a short URL.
 * @param {string} shortUrl - The short URL of the file.
 * @returns {Promise<object|null>} - A promise that resolves to an object containing file details, or null if retrieval fails.
 */
async function getFileDetails(shortUrl) {
    // API Endpoint
    const apiUrl = `https://www.terabox.com/api/shorturlinfo?app_id=250528&shorturl=${shortUrl}&root=1`;

    // Request Headers
    const headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
        "Referer": "https://www.terabox.com/",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "X-Requested-With": "XMLHttpRequest"
    };

    try {
        // Send GET request to fetch file details
        const response = await fetch(apiUrl, { method: "GET", headers: headers });
        const data = await response.json();

        // Validate response
        if (!data || !data.sign) {
            console.error("Failed to retrieve file details. Response:", data);
            return null;
        }

        // Extract relevant file details
        const fileDetails = {
            status: "success",
            sign: data.sign,
            timestamp: data.timestamp,
            shareid: data.shareid,
            uk: data.uk,
            list: data.list || []
        };

        return fileDetails;

    } catch (error) {
        console.error("Error fetching file details:", error);
        return null;
    }
}

module.exports = getFileDetails;
