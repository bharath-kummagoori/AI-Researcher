import requests
from typing import Optional, List, Dict
from research_agent.inno.tools.github_client import GitHubSearcher
from research_agent.inno.registry import register_tool
from research_agent.constant import GITHUB_AI_TOKEN
import json
@register_tool("search_github_repos")
def search_github_repos(query, limit=5):
    """
    Search GitHub public repositories based on a keyword.

    :param query: The query to search for in repository names or descriptions.
    :param limit: The total number of repositories to return.
    :return: A list of dictionaries containing repository details, limited to the specified number.
    """
    repos = []
    per_page = 10
    page = 1
    while len(repos) < limit:
        
        url = f'https://api.github.com/search/repositories?q={query}&per_page={per_page}&page={page}'

        try:
            response = requests.get(url)
        except Exception as e:
            return f"GitHub search failed due to network error: {e}. Continuing without GitHub results."

        if response.status_code == 200:
            items = response.json().get('items', [])
            for item in items:
                formatted_repo = {
                    "name": f"{item['owner']['login']}/{item['name']}",
                    "author": item['owner']['login'],
                    "description": item['description'],
                    "link": item['html_url']
                }
                repos.append(formatted_repo)
                if len(repos) >= limit:
                    break

            if len(items) < per_page:  # Stop if there are no more repos to fetch
                break
            page += 1
        else:
            return f"GitHub search returned status {response.status_code}. This is non-critical - continuing without GitHub results."

    return_str = """
    Here are some of the repositories I found on GitHub:
    """

    for repo in repos:
        return_str += f"""
        Name: {repo['name']}
        Description: {repo['description']}
        Link: {repo['link']}
        """

    return return_str
@register_tool("search_github_code")
def search_github_code(repo_owner: str, 
                      repo_name: str, 
                      query: str, 
                      language: Optional[str] = None, 
                      per_page: int = 5, 
                      page: int = 1) -> List[Dict]:
    """
    Search GitHub code based on a keyword.
    
    Args:
        repo_owner: The owner of the repository
        repo_name: The name of the repository
        query: The keyword to search for
        language: The programming language to filter by, optional
        per_page: The number of results per page, optional
        page: The page number, optional
        
    Returns:
        List[Dict]: The search results list
    """
    try:
        searcher = GitHubSearcher(GITHUB_AI_TOKEN)
    except ValueError:
        searcher = GitHubSearcher(None)
    try:
        results = searcher.search_code(repo_owner, repo_name, query, language, per_page, page)
    except Exception as e:
        return json.dumps([{"error": f"GitHub code search failed: {e}"}], indent=4)
    if 'items' not in results:
        return json.dumps([], indent=4)

    # Extract useful information
    formatted_results = []
    for item in results['items']:
        try:
            response = requests.get(item['url'])
            if response.status_code == 200:
                download_url = response.json()['download_url']
                response = requests.get(download_url)
                content = response.text if response.status_code == 200 else ""
            else:
                content = ""
        except Exception:
            content = ""
        formatted_results.append({
            'name': item['name'],
            'path': item['path'],
            'url': item['html_url'],
            'repository': item['repository']['full_name'],
            'content_url': item['url'],
            'content': content
        })
    return json.dumps(formatted_results, indent=4)
