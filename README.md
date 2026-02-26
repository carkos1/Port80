# Port80
A Python script designed to extract business data from online directories and automatically audit the technical health of their websites.

What it does:

    Navigates through regional pages of online business directories.

    Extracts Business Name, Phone Number, and Email (via hidden mailto: tags).

    Visits the extracted website URL and performs a connection health check.

    Exports the categorized results to CSV files.

Connection & Health Tests:

    HTTP Status Codes detection (e.g., 200, 404, 403).

    Expired domains / Server down detection (CONNECTION_REFUSED).

    Response time monitoring / Timeouts (> 5 seconds).

    SSL Certificate verification (HTTP vs HTTPS).

Output

The script automatically generates two files in the root directory:

    Stores_Websites.csv: Businesses with their own domains (includes the technical diagnostic).

    Stores_Social.csv: Businesses operating exclusively via social media platforms (Facebook/Instagram).

Technologies

    Python 3

    requests (HTTP calls and network exception handling)

    beautifulsoup4 / lxml (HTML Parsing)

    urllib & csv
