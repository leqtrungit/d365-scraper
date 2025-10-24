# Microsoft Learn Course Scraper

A generic Python scraper for extracting content from Microsoft Learn training modules.

## Features

- ✅ **Generic & Reusable**: Works with any module on Microsoft Learn
- ✅ **Batch Processing**: Scrape multiple modules from a file
- ✅ **Complete Scraping**: Extracts all units from a module
- ✅ **Comprehensive Structure**: Extracts titles, content, lists, images, and links
- ✅ **Absolute URLs**: Automatically converts relative URLs to absolute URLs
- ✅ **Clean Data**: Filters out unnecessary UI text
- ✅ **Full Metadata**: Includes module information, roles, products, levels, etc.

## Installation

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Basic Syntax

```bash
# Scrape a single module
python ms_learn_scraper.py <MODULE_UID> [-o OUTPUT_DIR]

# Scrape multiple modules from a file
python ms_learn_scraper.py -f <UID_FILE> [-o OUTPUT_DIR]
```

### Parameters

- `MODULE_UID`: Single module UID to scrape
- `-f, --file`: Path to file containing UIDs (one per line)
- `-o, --output`: Output directory for JSON files (default: current directory)

**Note**: Either `MODULE_UID` or `-f` is required (mutually exclusive).

### Examples

#### 1. Scrape a single module

```bash
python ms_learn_scraper.py learn-dynamics.get-started-financial-management-in-dynamics-365-finance-ops
```

Output: `learn-dynamics_get-started-financial-management-in-dynamics-365-finance-ops.json`

#### 2. Scrape a single module with custom output directory

```bash
python ms_learn_scraper.py learn.wwl.describe-cloud-compute -o output_data
```

Output: `output_data/learn_wwl_describe-cloud-compute.json`

#### 3. Scrape multiple modules from a file

Create a file `uids.txt`:
```
learn-dynamics.get-started-financial-management-in-dynamics-365-finance-ops
learn-dynamics.business-process-mapping-dynamics-365
learn.wwl.explore-microsoft-dynamics-365-finance-core-capabilities
```

Then run:
```bash
python ms_learn_scraper.py -f uids.txt -o output_data
```

Output:
- `output_data/learn-dynamics_get-started-financial-management-in-dynamics-365-finance-ops.json`
- `output_data/learn-dynamics_business-process-mapping-dynamics-365.json`
- `output_data/learn_wwl_explore-microsoft-dynamics-365-finance-core-capabilities.json`

#### 4. View help

```bash
python ms_learn_scraper.py --help
```

## How to Find Module UID

There are 2 ways to find a module's UID:

### Method 1: From Module URL

Visit the module page on Microsoft Learn, then:
- Open DevTools (F12)
- Find meta tag: `<meta name="uid" content="...">`
- Or search in troubleshooting links for parameter `uid=...`

### Method 2: From API

```bash
# Open this URL in browser to view metadata
https://learn.microsoft.com/api/catalog?uid=<MODULE_UID>
```

## Output Structure

The JSON output file has the following structure:

```json
{
  "module": {
    "uid": "module-uid",
    "title": "Module Title",
    "summary": "Module description",
    "duration_in_minutes": 84,
    "levels": ["beginner"],
    "roles": ["functional-consultant", "business-user"],
    "products": ["dynamics-365"],
    "url": "https://learn.microsoft.com/...",
    "number_of_units": 16
  },
  "units": [
    {
      "url": "https://learn.microsoft.com/.../unit-slug/",
      "title": "Unit Title",
      "duration": "5 minutes",
      "paragraphs": ["paragraph 1", "paragraph 2", ...],
      "lists": [
        {
          "type": "ul",
          "items": ["item 1", "item 2", ...]
        }
      ],
      "images": [
        {
          "src": "https://learn.microsoft.com/.../media/image.png",
          "alt": "Image description"
        }
      ],
      "links": [
        {
          "text": "Link text",
          "href": "https://..."
        }
      ],
      "uid": "unit-uid",
      "order": 1
    }
  ]
}
```

## Important Notes

### Image URLs

The scraper automatically handles image URLs:
- Relative paths like `media/image.png` are converted to absolute URLs
- URLs are created at module level (excluding unit path)
- Example: `https://learn.microsoft.com/en-us/training/modules/module-name/media/image.png`

### Link URLs

All relative links are also converted to absolute URLs for easy use.

### Rate Limiting

The script includes a 0.5s delay between requests to avoid overloading the server.

## Troubleshooting

### Error: "No module found for UID"

- Double-check that the UID is correct
- Try accessing the API: `https://learn.microsoft.com/api/catalog?uid=<UID>`

### Error: "No unit URLs found on module page"

- The module page may have a different structure
- Check if the module has units

## Dependencies

- `requests`: HTTP requests
- `beautifulsoup4`: HTML parsing
- `lxml`: XML/HTML parser

## License

MIT License

