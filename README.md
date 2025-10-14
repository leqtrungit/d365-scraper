# Microsoft Learn Course Scraper

A generic Python scraper for extracting content from Microsoft Learn training modules.

## Features

- ✅ **Generic & Reusable**: Works with any module on Microsoft Learn
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
python ms_learn_scraper.py <MODULE_UID> [-o OUTPUT_FILE]
```

### Parameters

- `MODULE_UID` (required): UID of the module to scrape
- `-o, --output` (optional): JSON output filename (default: `course_data.json`)

### Examples

#### 1. Scrape Dynamics 365 Finance module

```bash
python ms_learn_scraper.py learn-dynamics.get-started-financial-management-in-dynamics-365-finance-ops
```

#### 2. Scrape Azure Fundamentals module with custom output

```bash
python ms_learn_scraper.py learn.wwl.describe-cloud-compute -o azure_fundamentals.json
```

#### 3. View help

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

