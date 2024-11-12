import requests
import pandas as pd
import matplotlib.pyplot as plt
import datetime

GITHUB_TOKEN = 'YOUR_GITHUB_TOKEN'

# Path to the CSV file containing the repository URLs
csv_file_path = 'FILE_CONTAINING_REPOSITORIES.csv'

# Read CSV file and extract URLs
repos_df = pd.read_csv(csv_file_path)
repos = repos_df['URL'].tolist()

def fetch_commit_data(repo_url):
    # Extract the 'owner/repo' format from the URL
    repo = repo_url.split('github.com/')[-1]
    url = f'https://api.github.com/repos/{repo}/commits'
    headers = {'Authorization': f'token {GITHUB_TOKEN}'}
    params = {
        'since': (datetime.datetime.now() - datetime.timedelta(days=365)).isoformat(),
        'until': datetime.datetime.now().isoformat(),
        'per_page': 100
    }

    commit_data = []
    while url:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        commits = response.json()
        for commit in commits:
            commit_data.append({
                'repository': repo,
                'commit_date': commit['commit']['committer']['date']
            })

        # Get the next page URL from the 'Link' header if available
        if 'Link' in response.headers:
            links = response.headers['Link'].split(',')
            url = None
            for link in links:
                if 'rel="next"' in link:
                    url = link[link.find('<')+1:link.find('>')]
                    break
        else:
            url = None

    return commit_data

# Fetch and process data for all repositories
raw_commit_data = []
for repo_url in repos:
    commit_data = fetch_commit_data(repo_url)
    raw_commit_data.extend(commit_data)

commit_df = pd.DataFrame(raw_commit_data)
commit_df['commit_date'] = pd.to_datetime(commit_df['commit_date'])

# Export the raw commit data to a CSV file
output_csv_file = 'raw_commit_data.csv'
commit_df.to_csv(output_csv_file, index=False)
