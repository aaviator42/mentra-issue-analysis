#!/usr/bin/env python3
"""
Analyze only GitHub issues labeled as 'bug' from MentraOS
"""

import json
import re
from pathlib import Path
from collections import defaultdict
import sys


def load_bug_issues(issues_dir):
    """Load only issues with 'bug' label."""
    bug_issues = []
    issues_dir = Path(issues_dir)
    
    print("Loading bug issues...")
    
    for issue_file in issues_dir.glob("issue_*.json"):
        try:
            with open(issue_file, 'r', encoding='utf-8') as f:
                issue = json.load(f)
                
                # Check if issue has 'bug' label
                labels = [label['name'].lower() for label in issue.get('labels', [])]
                if 'bug' in labels:
                    bug_issues.append(issue)
        except Exception as e:
            print(f"Error loading {issue_file}: {e}")
    
    print(f"Found {len(bug_issues)} bug issues")
    return bug_issues


def categorize_bugs(bug_issues):
    """Categorize bug issues by type - multiple categories per bug."""
    categories = {
        'bluetooth_pairing': [],
        'translation_language': [],
        'streaming_media': [],
        'permissions_android': [],
        'ios_specific': [],
        'app_crashes': [],
        'ui_navigation': [],
        'cloud_sync': [],
        'hardware_integration': [],
        'performance': [],
        'wifi_connectivity': [],
        'developer_console': [],
        'error_handling': [],
        'audio_processing': [],
        'gallery_media': [],
        'state_synchronization': [],
        'ble_communication': [],
        'camera_functionality': [],
        'other': []
    }
    
    patterns = {
        'bluetooth_pairing': [
            r'\bpair\w*\b', r'\bbluetooth\b', r'\bble\b.*\bconnect\b', r'\bdisconnect\b', 
            r'\bglasses\b.*\bpair\b', r'\bpairing\b'
        ],
        'translation_language': [
            r'\btranslat\w+\b', r'\blanguage\b', r'\bwelsh\b', r'\bchinese\b', 
            r'\benglish\b', r'\bhang\w*\b.*\btranslat\w+\b', r'\bspeech\b.*\bprocess\w*\b'
        ],
        'streaming_media': [
            r'\bstream\w*\b', r'\brtmp\b', r'\blive\b.*\bstream\b', r'\bvideo\b.*\bstream\b', 
            r'\brecord\w*\b.*\bstream\b', r'\bmedia\b.*\bstream\b'
        ],
        'permissions_android': [
            r'\bpermission\w*\b', r'\bandroid\b.*\bpermission\b', r'\bmicrophone\b.*\bpermission\b', 
            r'\blocation\b.*\bpermission\b', r'\bnotification\w*\b.*\bpermission\b'
        ],
        'ios_specific': [
            r'\bios\b', r'\biphone\b', r'\bmic\b.*\bios\b', r'\bapple\b',
            r'\bios\b.*\bfail\w*\b', r'\bios\b.*\bcrash\b'
        ],
        'app_crashes': [
            r'\bcrash\w*\b', r'\bexception\b', r'\bfail\w*\b.*\bapp\b', 
            r'\bclose\w*\b.*\bapp\b', r'\bhang\w*\b', r'\bfreez\w*\b', r'\bsoftexception\b'
        ],
        'ui_navigation': [
            r'\bpage\b', r'\bnavigat\w*\b', r'\bui\b', r'\bmenu\b', 
            r'\bbutton\b', r'\bsettings\b.*\breset\b', r'\bscreen\b.*\bblank\b'
        ],
        'cloud_sync': [
            r'\bcloud\b', r'\bsync\b', r'\bserver\b', r'\bapi\b', 
            r'\bwebsocket\b', r'\bdatabase\b', r'\bclient\b.*\bserver\b'
        ],
        'hardware_integration': [
            r'\bhardware\b', r'\bsensor\w*\b', r'\bcalibrat\w*\b', 
            r'\bfirmware\b', r'\bglasses\b.*\bstop\b'
        ],
        'performance': [
            r'\bslow\b', r'\bperformance\b', r'\btimeout\b', 
            r'\bmemory\b', r'\bbattery\b', r'\blag\w*\b', r'\bunreliable\b'
        ],
        'wifi_connectivity': [
            r'\bwifi\b', r'\bhotspot\b', r'\bpassword\b.*\bwifi\b', 
            r'\bnetwork\b.*\bconnect\b', r'\bwifi\b.*\bconnect\b'
        ],
        'developer_console': [
            r'\bdev\b.*\bconsole\b', r'\bupload\b.*\bimage\b', r'\bicon\b.*\bupload\b',
            r'\bdeveloper\b.*\bconsole\b', r'\bauth\w*\b.*\bconsole\b'
        ],
        'error_handling': [
            r'\berror\b.*\bmessage\b', r'\bfeedback\b.*\bmissing\b', r'\bretry\b.*\binfinite\b',
            r'\bwebview\b.*\berror\b', r'\berror\b.*\bhandling\b'
        ],
        'audio_processing': [
            r'\baudio\b', r'\bmicrophone\b', r'\bmic\b', r'\bspeech\b', 
            r'\bplayback\b', r'\bsound\b', r'\bvoice\b'
        ],
        'gallery_media': [
            r'\bgallery\b', r'\bmedia\b.*\btransfer\b', r'\bphoto\b.*\bsync\b',
            r'\bgallery\b.*\bsync\b', r'\bmedia\b.*\bgallery\b'
        ],
        'state_synchronization': [
            r'\bstate\b.*\bsync\b', r'\bclient\b.*\bcloud\b.*\bstate\b', 
            r'\bapp\b.*\bstate\b', r'\bboot\b.*\bscreen\b.*\bdeleted\b'
        ],
        'ble_communication': [
            r'\bble\b', r'\bphoto\b.*\brequest\b', r'\back\b.*\bissue\b',
            r'\bble\b.*\btransfer\b', r'\bble\b.*\bcrash\b'
        ],
        'camera_functionality': [
            r'\bcamera\b', r'\brotation\b.*\bhardcoded\b', r'\bphoto\b.*\btaking\b',
            r'\brecord\w*\b', r'\bcamera\b.*\brotation\b'
        ]
    }
    
    for issue in bug_issues:
        title = issue.get('title', '').lower()
        body = issue.get('body', '').lower() if issue.get('body') else ''
        text = f"{title} {body}"
        
        matched_categories = []
        for category, pattern_list in patterns.items():
            for pattern in pattern_list:
                if re.search(pattern, text):
                    categories[category].append(issue)
                    matched_categories.append(category)
                    break
        
        if not matched_categories:
            categories['other'].append(issue)
    
    return categories


def analyze_platforms(bug_issues):
    """Analyze platform distribution."""
    platforms = {'android': [], 'ios': [], 'both': [], 'unspecified': []}
    
    for issue in bug_issues:
        title = issue.get('title', '').lower()
        body = issue.get('body', '').lower() if issue.get('body') else ''
        labels = [label['name'].lower() for label in issue.get('labels', [])]
        text = f"{title} {body} {' '.join(labels)}"
        
        has_android = bool(re.search(r'\bandroid\b', text))
        has_ios = bool(re.search(r'\bios\b|\biphone\b', text))
        
        if has_android and has_ios:
            platforms['both'].append(issue)
        elif has_android:
            platforms['android'].append(issue)
        elif has_ios:
            platforms['ios'].append(issue)
        else:
            platforms['unspecified'].append(issue)
    
    return platforms


def analyze_hardware_models(bug_issues):
    """Analyze hardware model distribution."""
    models = {
        'even_realities_g1': [],
        'mentra_live': [],
        'mentra_mach1': [],
        'vuzix_z100': [],
        'unspecified': []
    }
    
    model_patterns = {
        'even_realities_g1': [r'\bg1\b', r'\beven\b.*\brealities\b', r'\bg1\b.*\bglasses\b'],
        'mentra_live': [r'\bmentra\b.*\blive\b', r'\blive\b'],
        'mentra_mach1': [r'\bmach\s*1\b', r'\bmentra\b.*\bmach\b'],
        'vuzix_z100': [r'\bvuzix\b', r'\bz100\b', r'\bz\s*100\b']
    }
    
    for issue in bug_issues:
        title = issue.get('title', '').lower()
        body = issue.get('body', '').lower() if issue.get('body') else ''
        text = f"{title} {body}"
        
        matched_models = []
        for model, pattern_list in model_patterns.items():
            for pattern in pattern_list:
                if re.search(pattern, text):
                    models[model].append(issue)
                    matched_models.append(model)
                    break
        
        if not matched_models:
            models['unspecified'].append(issue)
    
    return models


def analyze_testability(categories, bug_issues):
    """Determine what testing approaches would catch these bugs - no double counting."""
    testing_types = {
        'automated_tests_could_catch': [],
        'device_matrix_testing_needed': [],
        'manual_workflow_testing_needed': [],
        'environment_dependent_hard_to_test': []
    }
    
    # Map categories to testing feasibility (ordered by restrictiveness)
    testability_hierarchy = {
        'environment_dependent_hard_to_test': 4,
        'manual_workflow_testing_needed': 3,
        'device_matrix_testing_needed': 2,
        'automated_tests_could_catch': 1
    }
    
    testability_map = {
        'bluetooth_pairing': 'device_matrix_testing_needed',
        'translation_language': 'manual_workflow_testing_needed', 
        'streaming_media': 'environment_dependent_hard_to_test',
        'permissions_android': 'device_matrix_testing_needed',
        'ios_specific': 'device_matrix_testing_needed',
        'app_crashes': 'automated_tests_could_catch',
        'ui_navigation': 'automated_tests_could_catch',
        'cloud_sync': 'automated_tests_could_catch',
        'hardware_integration': 'environment_dependent_hard_to_test',
        'performance': 'environment_dependent_hard_to_test',
        'wifi_connectivity': 'environment_dependent_hard_to_test',
        'developer_console': 'automated_tests_could_catch',
        'error_handling': 'automated_tests_could_catch',
        'audio_processing': 'device_matrix_testing_needed',
        'gallery_media': 'manual_workflow_testing_needed',
        'state_synchronization': 'automated_tests_could_catch',
        'ble_communication': 'device_matrix_testing_needed',
        'camera_functionality': 'device_matrix_testing_needed'
    }
    
    # Track each bug's most restrictive testing requirement
    bug_testing_requirements = {}
    
    for category, issues in categories.items():
        if category == 'other':
            continue
            
        testing_type = testability_map.get(category, 'manual_workflow_testing_needed')
        for issue in issues:
            issue_id = issue['number']
            
            # If we haven't seen this bug or this requirement is more restrictive
            if (issue_id not in bug_testing_requirements or 
                testability_hierarchy[testing_type] > testability_hierarchy[bug_testing_requirements[issue_id]]):
                bug_testing_requirements[issue_id] = testing_type
    
    # Assign each bug to its most restrictive category
    for issue in bug_issues:
        issue_id = issue['number']
        if issue_id in bug_testing_requirements:
            testing_type = bug_testing_requirements[issue_id]
            testing_types[testing_type].append(issue)
        else:
            # Bugs not categorized go to manual workflow testing
            testing_types['manual_workflow_testing_needed'].append(issue)
    
    return testing_types


def main():
    issues_dir = "github_data/Mentra-Community_MentraOS/issues"
    
    if not Path(issues_dir).exists():
        print(f"Error: {issues_dir} not found")
        sys.exit(1)
    
    # Load and analyze bug issues
    bug_issues = load_bug_issues(issues_dir)
    categories = categorize_bugs(bug_issues)
    platforms = analyze_platforms(bug_issues)
    hardware_models = analyze_hardware_models(bug_issues)
    testability = analyze_testability(categories, bug_issues)
    
    # Generate report
    print("\n" + "="*60)
    print("MENTRAOS BUG ANALYSIS REPORT")
    print("="*60)
    
    print(f"\nTOTAL BUG ISSUES: {len(bug_issues)}")
    open_bugs = len([i for i in bug_issues if i['state'] == 'open'])
    closed_bugs = len([i for i in bug_issues if i['state'] == 'closed'])
    print(f"OPEN: {open_bugs} | CLOSED: {closed_bugs}")
    
    print(f"\nBUG CATEGORIES:")
    total_categorized = sum(len(issues) for issues in categories.values())
    for category, issues in categories.items():
        if issues:
            percentage = (len(issues) / total_categorized) * 100
            print(f"  {category.replace('_', ' ').title()}: {len(issues)} ({percentage:.1f}%)")
    
    print(f"\nPLATFORM BREAKDOWN:")
    for platform, issues in platforms.items():
        if issues:
            percentage = (len(issues) / len(bug_issues)) * 100
            print(f"  {platform.title()}: {len(issues)} ({percentage:.1f}%)")
    
    print(f"\nHARDWARE MODEL BREAKDOWN:")
    for model, issues in hardware_models.items():
        if issues:
            percentage = (len(issues) / len(bug_issues)) * 100
            readable_name = model.replace('_', ' ').title()
            print(f"  {readable_name}: {len(issues)} ({percentage:.1f}%)")
    
    print(f"\nTESTING STRATEGY ANALYSIS:")
    print("How these bugs could be caught:")
    for test_type, issues in testability.items():
        if issues:
            percentage = (len(issues) / len(bug_issues)) * 100
            readable_name = test_type.replace('_', ' ').title()
            print(f"  {readable_name}: {len(issues)} ({percentage:.1f}%)")
    
    print(f"\nTOP OPEN BUGS BY CATEGORY:")
    for category, issues in categories.items():
        open_issues = [i for i in issues if i['state'] == 'open']
        if open_issues:
            print(f"\n{category.replace('_', ' ').title()} (Open Issues):")
            for i, issue in enumerate(open_issues[:3]):
                print(f"  {i+1}. #{issue['number']}: {issue['title']}")
    
    print(f"\n" + "="*60)
    print("KEY INSIGHTS FOR TESTING STRATEGY")
    print("="*60)
    
    # Calculate key percentages
    device_dependent = len(testability['device_matrix_testing_needed'])
    environment_dependent = len(testability['environment_dependent_hard_to_test'])
    manual_workflows = len(testability['manual_workflow_testing_needed'])
    automatable = len(testability['automated_tests_could_catch'])
    
    total = len(bug_issues)
    
    print(f"\n• {(device_dependent/total)*100:.0f}% need device matrix testing")
    print(f"• {(environment_dependent/total)*100:.0f}% are environment-dependent (hard to automate)")
    print(f"• {(manual_workflows/total)*100:.0f}% need manual workflow testing")
    print(f"• {(automatable/total)*100:.0f}% could be caught by automated tests")
    

if __name__ == '__main__':
    main()