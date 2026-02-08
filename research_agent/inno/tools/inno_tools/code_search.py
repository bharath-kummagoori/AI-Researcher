import requests
from typing import Optional, List, Dict
from research_agent.inno.tools.github_client import GitHubSearcher
from research_agent.inno.registry import register_tool
from research_agent.constant import GITHUB_AI_TOKEN
import json
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)
from urllib.parse import quote

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=60),
    retry=retry_if_exception_type((
        requests.exceptions.RequestException,
        requests.exceptions.HTTPError
    ))
)
@register_tool("search_github_repos")
def search_github_repos(context_variables, query, limit=5):
    """
    Search GitHub public repositories based on a keyword.

    :param query: The query to search for in repository names or descriptions.
    :param limit: The total number of repositories to return.
    :return: A list of dictionaries containing repository details, limited to the specified number.
    """
    date_limit = context_variables.get("date_limit")
    assert date_limit, "Date limit is required"

    exclude_users = ["lucidrains"]
    if exclude_users:
        # 将排除用户列表转换为GitHub搜索语法
        exclude_query = ' '.join([f'-user:{user}' for user in exclude_users])
        query = f"{query} {exclude_query}"

    repos = []
    per_page = 10
    page = 1
    while len(repos) < limit:
        date_query = f"{query} created:<{date_limit}"
        encoded_query = quote(date_query)
        url = f'https://api.github.com/search/repositories?q={encoded_query}&per_page={per_page}&page={page}'

        headers = {
            'Accept': 'application/vnd.github.v3+json'
        }
        # Only add auth header if token is available
        if GITHUB_AI_TOKEN:
            headers['Authorization'] = f'token {GITHUB_AI_TOKEN}'

        try:
            response = requests.get(url, headers=headers)
        except Exception as e:
            return f"GitHub search failed due to network error: {e}. Continuing without GitHub results."

        if response.status_code == 200:
            items = response.json().get('items', [])
            for item in items:
                formatted_repo = {
                    "name": f"{item['owner']['login']}/{item['name']}",
                    "author": item['owner']['login'],
                    "description": item['description'],
                    "link": item['html_url'],
                    "stars": item['stargazers_count'],
                    "created_at": item['created_at'],
                    "language": item['language']
                }
                repos.append(formatted_repo)
                if len(repos) >= limit:
                    break

            if len(items) < per_page:  # Stop if there are no more repos to fetch
                break
            page += 1
        else:
            # Return gracefully instead of crashing
            return f"GitHub search returned status {response.status_code}. This is non-critical - continuing without GitHub results."

    return_str = f"The results of searching {query} on GitHub: \n"

    for repo in repos:
        return_str += f"""
        Name: {repo['name']}
        Description: {repo['description']}
        Link: {repo['link']}
        Stars: {repo['stars']}
        Created at: {repo['created_at']}
        Language: {repo['language']}
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
        # No GitHub token - use unauthenticated searcher
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
