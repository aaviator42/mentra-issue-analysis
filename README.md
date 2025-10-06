# MentraOS Bug Analysis Tools

Tools for analyzing GitHub issues from the MentraOS repository to determine testing strategies and bug patterns.

## Files

- `fetch_issues.py` - Downloads GitHub issues using GitHub API
- `analyze_bugs.py` - Analyzes bug reports and categorizes them by type and testing requirements
- `analysis_raw.txt` - Sample output from the analysis tool

## Installation

### Prerequisites

1. **Python 3.x** with standard libraries
2. **requests** library for GitHub API access

```bash
pip install requests
```

### GitHub Token (Recommended)

For higher rate limits (5,000 vs 60 requests/hour):

1. Go to GitHub Settings → Developer settings → Personal access tokens
2. Generate new token (classic)
3. Select scopes: `public_repo` and `read:discussion`

## Usage

### 1. Fetch Issues (`fetch_issues.py`)

Downloads GitHub issues and discussions using the GitHub API.

```bash
# Basic usage
python3 fetch_issues.py Mentra-Community/MentraOS

# Specify output directory
python3 fetch_issues.py Mentra-Community/MentraOS -o ./data

# Use authentication token (recommended)
python3 fetch_issues.py Mentra-Community/MentraOS --token ghp_your_token_here

# Or set as environment variable
export GITHUB_TOKEN=ghp_your_token_here
python3 fetch_issues.py Mentra-Community/MentraOS

# Fetch only issues
python3 fetch_issues.py Mentra-Community/MentraOS --issues-only

# Fetch only discussions
python3 fetch_issues.py Mentra-Community/MentraOS --discussions-only
```

**Output Structure:**
```
github_data/
└── Mentra-Community_MentraOS/
    ├── summary.json           # Combined summary
    ├── issues/
    │   ├── summary.json       # Issues summary
    │   ├── issue_1.json
    │   ├── issue_2.json
    │   └── ...
    └── discussions/
        ├── summary.json       # Discussions summary
        ├── discussion_1.json
        ├── discussion_2.json
        └── ...
```

### 2. Analyze Bugs (`analyze_bugs.py`)

Analyzes downloaded bug reports to categorize them and determine testing strategies.

```bash
python3 analyze_bugs.py
```

**Prerequisites:** Must have run `fetch_issues.py` first to download issue data.

#### Logic Overview

**1. Bug Detection**
- Filters issues with the `bug` label only
- Combines title and body text for pattern matching

**2. Multi-Category Classification**
- Each bug can belong to multiple categories (unlike first-match-wins approach)
- Uses regex patterns to match bugs to categories:

**Categories:**
- `bluetooth_pairing` - Pairing, connection issues with glasses
- `translation_language` - Translation, speech processing bugs  
- `streaming_media` - RTMP streaming, live video issues
- `permissions_android` - Android permission-related bugs
- `ios_specific` - iOS-only bugs and issues
- `app_crashes` - Application crashes, exceptions, hangs
- `ui_navigation` - UI/UX, page navigation issues
- `cloud_sync` - Server/client synchronization issues
- `hardware_integration` - Hardware sensor, calibration issues
- `performance` - Slow performance, timeouts, battery issues
- `wifi_connectivity` - WiFi connection, hotspot issues
- `developer_console` - Dev console, image upload issues
- `error_handling` - Poor error messages, missing feedback
- `audio_processing` - Microphone, audio playback issues
- `gallery_media` - Gallery sync, media transfer issues
- `state_synchronization` - App state sync issues
- `ble_communication` - Bluetooth Low Energy communication
- `camera_functionality` - Camera rotation, photo taking issues
- `other` - Uncategorized bugs

**3. Platform Analysis**
- Detects Android, iOS, both, or unspecified platform issues
- Uses regex patterns to match platform mentions

**4. Hardware Model Detection**
- Identifies which glasses model is affected:
  - Even Realities G1
  - Mentra Live
  - Mentra Mach 1
  - Vuzix Z100
  - Unspecified

**5. Testing Strategy Classification**

**No double-counting**. Each bug gets assigned to its most restrictive testing requirement using a hierarchy:

**Hierarchy (most to least restrictive):**
1. `environment_dependent_hard_to_test` (4) - Real-world conditions needed
2. `manual_workflow_testing_needed` (3) - Human interaction required  
3. `device_matrix_testing_needed` (2) - Multiple device testing needed
4. `automated_tests_could_catch` (1) - Can be automated

**Category Mappings:**
- **Environment Dependent:** streaming_media, hardware_integration, performance, wifi_connectivity
- **Manual Workflow:** translation_language, gallery_media  
- **Device Matrix:** bluetooth_pairing, permissions_android, ios_specific, audio_processing, ble_communication, camera_functionality
- **Automated:** app_crashes, ui_navigation, cloud_sync, developer_console, error_handling, state_synchronization

**Algorithm:**
1. For each bug, collect all matching categories
2. Map each category to its testing requirement
3. Assign bug to most restrictive requirement found
4. Ensures each bug appears in exactly one testing category

## Example Workflow

```bash
# 1. Fetch issues from MentraOS repository
python3 fetch_issues.py Mentra-Community/MentraOS --token ghp_your_token

# 2. Analyze the bugs and save output
python3 analyze_bugs.py > bug_analysis_report.txt

# 3. View the analysis
cat bug_analysis_report.txt
```

## Dependencies

### fetch_issues.py
- Python 3.x
- `requests` library

### analyze_bugs.py
- Python 3.x standard library only (json, re, pathlib, collections, sys)
- No external packages required