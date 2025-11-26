import requests
import json
from datetime import datetime
import sys


def fetch_biocontainers_tools(size=50, show_preview=3):
    """
    Fetch top bioinformatics tools from BioContainers API

    Args:
        size (int): Number of tools to fetch (default: 50)
        show_preview (int): Number of tools to display preview (default: 3)
    """

    # API endpoint and parameters
    url = "https://api.biocontainers.pro/ga4gh/trs/v2/tools"
    params = {
        "size": size,
        "sort": "pulls",  # Changed from "pull_count" to "pulls"
        "order": "desc",
        "page": 0
    }

    try:
        print(f"Fetching top {size} bioinformatics tools...")
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()  # Raises an HTTPError for bad responses

        data = response.json()

        if not data:
            print("No data received from API")
            return None

        print(f"Successfully fetched {len(data)} tools\n")

        # Display preview of first few tools
        print(f"=== Preview of Top {min(show_preview, len(data))} Tools ===")
        for i, tool in enumerate(data[:show_preview], 1):
            print(f"\n{i}. Tool ID: {tool.get('id', 'N/A')}")
            print(f"   Name: {tool.get('name', 'N/A')}")

            # Handle pulls count
            pulls = tool.get('pulls', 'N/A')
            if isinstance(pulls, (int, float)):
                print(f"   Pulls: {pulls:,}")
            else:
                print(f"   Pulls: {pulls}")

            print(f"   Organization: {tool.get('organization', 'N/A')}")

            # Display tool class information
            toolclass = tool.get('toolclass', {})
            if toolclass:
                print(f"   Type: {toolclass.get('name', 'N/A')} ({toolclass.get('description', 'N/A')})")

            # Display version information
            versions = tool.get('versions', [])
            if versions:
                latest_version = versions[0] if versions else {}
                version_name = latest_version.get('meta_version', 'N/A')
                print(f"   Latest Version: {version_name}")
                print(f"   Total Versions: {len(versions)}")

            print(f"   API URL: {tool.get('url', 'N/A')}")
            print("   " + "=" * 60)

        # Save to JSON file with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"biocontainers_top_{size}_{timestamp}.json"

        # Create metadata
        metadata = {
            "fetch_date": datetime.now().isoformat(),
            "total_tools": len(data),
            "api_endpoint": url,
            "parameters": params
        }

        # Combine metadata and data
        output_data = {
            "metadata": metadata,
            "tools": data
        }

        with open(filename, "w", encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

        print(f"\n✅ Data saved to: {filename}")

        # Display summary statistics
        print(f"\n=== Summary Statistics ===")
        print(f"Total tools fetched: {len(data)}")

        if data:
            pull_counts = [tool.get('pulls', 0) for tool in data]
            pull_counts = [count for count in pull_counts if isinstance(count, (int, float)) and count > 0]
            if pull_counts:
                print(f"Highest pull count: {max(pull_counts):,}")
                print(f"Lowest pull count: {min(pull_counts):,}")
                print(f"Average pull count: {sum(pull_counts) / len(pull_counts):,.0f}")

        return data

    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching data: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing JSON response: {e}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None


def analyze_tools(data):
    """
    Perform basic analysis on the fetched tools data
    """
    if not data:
        return

    print(f"\n=== Tool Analysis ===")

    # Most common organizations
    orgs = {}
    for tool in data:
        org = tool.get('organization', 'Unknown')
        orgs[org] = orgs.get(org, 0) + 1

    print(f"\nTop Organizations:")
    for org, count in sorted(orgs.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  {org}: {count} tools")

    # Tool class distribution
    toolclasses = {}
    for tool in data:
        toolclass = tool.get('toolclass', {})
        tc_name = toolclass.get('name', 'Unknown')
        toolclasses[tc_name] = toolclasses.get(tc_name, 0) + 1

    print(f"\nTool Types:")
    for tc, count in sorted(toolclasses.items(), key=lambda x: x[1], reverse=True):
        print(f"  {tc}: {count} tools")

    # Version statistics
    version_counts = []
    for tool in data:
        versions = tool.get('versions', [])
        version_counts.append(len(versions))

    if version_counts:
        print(f"\nVersion Statistics:")
        print(f"  Average versions per tool: {sum(version_counts) / len(version_counts):.1f}")
        print(f"  Max versions for a single tool: {max(version_counts)}")
        print(f"  Tools with multiple versions: {sum(1 for v in version_counts if v > 1)}/{len(version_counts)}")

    # Tools with identifiers
    with_identifiers = sum(1 for tool in data if tool.get('identifiers'))
    print(f"\nTools with identifiers: {with_identifiers}/{len(data)} ({with_identifiers / len(data) * 100:.1f}%)")


if __name__ == "__main__":
    # Allow command line arguments
    size = int(sys.argv[1]) if len(sys.argv) > 1 else 50
    preview = int(sys.argv[2]) if len(sys.argv) > 2 else 3

    # Fetch and analyze data
    tools_data = fetch_biocontainers_tools(size=size, show_preview=preview)

    if tools_data:
        analyze_tools(tools_data)