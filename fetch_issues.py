#!/usr/bin/env python3
"""
GitHub Issues and Discussions Fetcher
Fetches all issues and discussions from a GitHub repository for analysis.
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
import requests


class GitHubFetcher:
    def __init__(self, token=None):
        self.token = token or os.getenv('GITHUB_TOKEN')
        self.headers = {
            'Accept': 'application/vnd.github+json',
            'X-GitHub-Api-Version': '2022-11-28'
        }
        if self.token:
            self.headers['Authorization'] = f'Bearer {self.token}'
    
    def fetch_issues(self, owner, repo, state='all'):
        """Fetch all issues (open and closed) from a repository."""
        issues = []
        page = 1
        
        print(f"Fetching {state} issues from {owner}/{repo}...")
        
        while True:
            url = f'https://api.github.com/repos/{owner}/{repo}/issues'
            params = {
                'state': state,
                'per_page': 100,
                'page': page,
                'sort': 'created',
                'direction': 'desc',
                'labels': ''  # Include all labels
            }
            
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code != 200:
                print(f"Error fetching issues: {response.status_code}")
                print(response.json())
                break
            
            data = response.json()
            if not data:
                break
            
            # Filter out pull requests (they show up in issues endpoint)
            page_issues = [item for item in data if 'pull_request' not in item]
            issues.extend(page_issues)
            
            print(f"  Fetched page {page}: {len(page_issues)} issues")
            page += 1
            
            if len(data) < 100:
                break
        
        return issues
    
    def fetch_discussions(self, owner, repo):
        """Fetch all discussions from a repository using GraphQL."""
        discussions = []
        has_next_page = True
        cursor = None
        
        print(f"Fetching discussions from {owner}/{repo}...")
        
        url = 'https://api.github.com/graphql'
        
        while has_next_page:
            query = """
            query($owner: String!, $repo: String!, $cursor: String) {
              repository(owner: $owner, name: $repo) {
                discussions(first: 100, after: $cursor) {
                  pageInfo {
                    hasNextPage
                    endCursor
                  }
                  nodes {
                    id
                    number
                    title
                    body
                    createdAt
                    updatedAt
                    closedAt
                    closed
                    url
                    author {
                      login
                    }
                    category {
                      name
                    }
                    labels(first: 10) {
                      nodes {
                        name
                      }
                    }
                    comments(first: 100) {
                      nodes {
                        id
                        body
                        createdAt
                        author {
                          login
                        }
                      }
                    }
                  }
                }
              }
            }
            """
            
            variables = {
                'owner': owner,
                'repo': repo,
                'cursor': cursor
            }
            
            response = requests.post(
                url,
                json={'query': query, 'variables': variables},
                headers=self.headers
            )
            
            if response.status_code != 200:
                print(f"Error fetching discussions: {response.status_code}")
                print(response.text)
                break
            
            data = response.json()
            
            if 'errors' in data:
                print(f"GraphQL errors: {data['errors']}")
                break
            
            repo_data = data.get('data', {}).get('repository', {})
            if not repo_data or 'discussions' not in repo_data:
                break
            
            discussions_data = repo_data['discussions']
            page_discussions = discussions_data['nodes']
            discussions.extend(page_discussions)
            
            print(f"  Fetched {len(page_discussions)} discussions")
            
            page_info = discussions_data['pageInfo']
            has_next_page = page_info['hasNextPage']
            cursor = page_info['endCursor']
        
        return discussions
    
    def save_to_files(self, owner, repo, issues, discussions, output_dir):
        """Save issues and discussions to organized files."""
        base_dir = Path(output_dir) / f"{owner}_{repo}"
        base_dir.mkdir(parents=True, exist_ok=True)
        
        # Save issues
        issues_dir = base_dir / 'issues'
        issues_dir.mkdir(exist_ok=True)
        
        print(f"\nSaving {len(issues)} issues to {issues_dir}...")
        
        for issue in issues:
            filename = f"issue_{issue['number']}.json"
            filepath = issues_dir / filename
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(issue, f, indent=2, ensure_ascii=False)
        
        # Save issues summary
        issues_summary = {
            'total_count': len(issues),
            'open_count': len([i for i in issues if i['state'] == 'open']),
            'closed_count': len([i for i in issues if i['state'] == 'closed']),
            'fetched_at': datetime.now().isoformat(),
            'issues': [{
                'number': i['number'],
                'title': i['title'],
                'state': i['state'],
                'created_at': i['created_at'],
                'url': i['html_url']
            } for i in issues]
        }
        
        with open(issues_dir / 'summary.json', 'w', encoding='utf-8') as f:
            json.dump(issues_summary, f, indent=2, ensure_ascii=False)
        
        # Save discussions
        if discussions:
            discussions_dir = base_dir / 'discussions'
            discussions_dir.mkdir(exist_ok=True)
            
            print(f"Saving {len(discussions)} discussions to {discussions_dir}...")
            
            for discussion in discussions:
                filename = f"discussion_{discussion['number']}.json"
                filepath = discussions_dir / filename
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(discussion, f, indent=2, ensure_ascii=False)
            
            # Save discussions summary
            discussions_summary = {
                'total_count': len(discussions),
                'open_count': len([d for d in discussions if not d['closed']]),
                'closed_count': len([d for d in discussions if d['closed']]),
                'fetched_at': datetime.now().isoformat(),
                'discussions': [{
                    'number': d['number'],
                    'title': d['title'],
                    'closed': d['closed'],
                    'created_at': d['createdAt'],
                    'url': d['url']
                } for d in discussions]
            }
            
            with open(discussions_dir / 'summary.json', 'w', encoding='utf-8') as f:
                json.dump(discussions_summary, f, indent=2, ensure_ascii=False)
        
        # Save combined summary
        combined_summary = {
            'repository': f"{owner}/{repo}",
            'fetched_at': datetime.now().isoformat(),
            'issues': {
                'total': len(issues),
                'open': len([i for i in issues if i['state'] == 'open']),
                'closed': len([i for i in issues if i['state'] == 'closed'])
            },
            'discussions': {
                'total': len(discussions),
                'open': len([d for d in discussions if not d['closed']]),
                'closed': len([d for d in discussions if d['closed']])
            }
        }
        
        with open(base_dir / 'summary.json', 'w', encoding='utf-8') as f:
            json.dump(combined_summary, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Data saved to: {base_dir}")
        print(f"   Issues: {combined_summary['issues']['total']} ({combined_summary['issues']['open']} open, {combined_summary['issues']['closed']} closed)")
        print(f"   Discussions: {combined_summary['discussions']['total']} ({combined_summary['discussions']['open']} open, {combined_summary['discussions']['closed']} closed)")


def main():
    parser = argparse.ArgumentParser(
        description='Fetch GitHub issues and discussions for analysis',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s facebook/react
  %(prog)s microsoft/vscode -o ./data
  %(prog)s owner/repo --token ghp_your_token_here
  %(prog)s owner/repo --issues-only

Environment Variables:
  GITHUB_TOKEN    GitHub personal access token (recommended for higher rate limits)
        """
    )
    
    parser.add_argument('repository', help='Repository in format: owner/repo')
    parser.add_argument('-o', '--output', default='./github_data',
                       help='Output directory (default: ./github_data)')
    parser.add_argument('-t', '--token', help='GitHub personal access token')
    parser.add_argument('--issues-only', action='store_true',
                       help='Fetch only issues, skip discussions')
    parser.add_argument('--discussions-only', action='store_true',
                       help='Fetch only discussions, skip issues')
    
    args = parser.parse_args()
    
    # Parse repository
    if '/' not in args.repository:
        print("Error: Repository must be in format 'owner/repo'")
        sys.exit(1)
    
    owner, repo = args.repository.split('/', 1)
    
    # Initialize fetcher
    fetcher = GitHubFetcher(token=args.token)
    
    if not fetcher.token:
        print("⚠️  Warning: No GitHub token provided. Rate limits will be lower.")
        print("   Set GITHUB_TOKEN environment variable or use --token flag.")
        print()
    
    # Fetch data
    issues = []
    discussions = []
    
    if not args.discussions_only:
        issues = fetcher.fetch_issues(owner, repo)
    
    if not args.issues_only:
        discussions = fetcher.fetch_discussions(owner, repo)
    
    # Save to files
    if issues or discussions:
        fetcher.save_to_files(owner, repo, issues, discussions, args.output)
    else:
        print("No data fetched.")
        sys.exit(1)


if __name__ == '__main__':
    main()