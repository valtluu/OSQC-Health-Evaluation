import requests
import pandas as pd
from datetime import datetime, timedelta

GITHUB_TOKEN = "YOUR_GITHUB_TOKEN"


# Headers for the GitHub API request
headers = {
    'Authorization': f'token {GITHUB_TOKEN}',
    'Accept': 'application/vnd.github.v3+json'
}


def search_repositories(query, per_page=30, page=1):
    url = f'https://api.github.com/search/repositories?q={query}&per_page={per_page}&page={page}'
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f'Error: {response.status_code}')
        return None


def collect_data(query, max_pages=10):
    all_repositories = []
    for page in range(1, max_pages + 1):
        result = search_repositories(query, page=page)
        if result:
            repositories = result.get('items', [])
            all_repositories.extend(repositories)
        else:
            break
    return all_repositories


def get_contributors_count(owner, repo_name):
    url = f'https://api.github.com/repos/{owner}/{repo_name}/contributors'
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        contributors = response.json()
        return len(contributors)
    else:
        print(f'Error fetching contributors for {owner}/{repo_name}: {response.status_code}')
        return None

# Extract relevant information and filter by last contribution date
def extract_relevant_info(repositories, cutoff_date):
    data = []
    for repo in repositories:
        last_pushed_date = datetime.strptime(repo['pushed_at'], '%Y-%m-%dT%H:%M:%SZ')
        if last_pushed_date >= cutoff_date:
            contributors_count = get_contributors_count(repo['owner']['login'], repo['name'])
            if contributors_count is not None:
                data.append({
                    'Name': repo['name'],
                    'Owner': repo['owner']['login'],
                    'Stars': repo['stargazers_count'],
                    'Forks': repo['forks_count'],
                    'Language': repo['language'],
                    'Description': repo['description'],
                    'Created_at': repo['created_at'],
                    'Updated_at': repo['updated_at'],
                    'Pushed_at': repo['pushed_at'],
                    'Contributors': contributors_count,
                    'URL': repo['html_url']
                })
            else:
                print("NO")
                print(contributors_count)
    return data

# Convert data to pandas DataFrame and save to CSV with semicolon delimiter
def save_to_csv(data, filename):
    df = pd.DataFrame(data)
    df.to_csv(filename, sep=';', index=False)
    print(f'Data saved to {filename}')

if __name__ == '__main__':
    query = 'quantum computing'
    repositories = collect_data(query)

    # Define the cutoff date (2 years ago from today)
    cutoff_date = datetime.now() - timedelta(days=2*365)

    data = extract_relevant_info(repositories, cutoff_date)
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    save_to_csv(data, f'quantum_computing_projects_{timestamp}.csv')
