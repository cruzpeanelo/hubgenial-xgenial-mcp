import os
from github import Github
from dotenv import load_dotenv
from datetime import datetime

class GitHubAssistant:
    def __init__(self):
        load_dotenv()
        self.gh = Github(os.getenv('GITHUB_TOKEN'))
        self.user = self.gh.get_user()

    def create_repo(self, name, description=""):
        try:
            # Try to get existing repo first
            try:
                repo = self.user.get_repo(name)
                print(f"Repository {name} already exists at {repo.html_url}")
                return repo
            except Exception as e:
                print(f"Trying to create new repo: {str(e)}")
                # Create new repo if it doesn't exist
                repo = self.user.create_repo(
                    name=name,
                    description=description,
                    private=False
                )
                print(f"Created new repository: {repo.html_url}")
                return repo
            
        except Exception as e:
            print(f"Error creating/accessing repository: {e}")
            return None

    def analyze_repo(self, repo_name):
        try:
            repo = self.gh.get_repo(repo_name)
            analysis = {
                "name": repo.name,
                "created_at": repo.created_at,
                "stars": repo.stargazers_count,
                "forks": repo.forks_count,
                "issues": repo.open_issues_count,
                "languages": repo.get_languages(),
                "branches": list(repo.get_branches()),
                "contributors": list(repo.get_contributors())
            }
            return analysis
        except Exception as e:
            print(f"Error analyzing repository: {e}")
            return None

    def push_code(self, repo_name, file_path, content, commit_message):
        try:
            repo = self.gh.get_repo(f"{self.user.login}/{repo_name}")
            current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
            branch_name = f"update_{current_time}"
            
            # Create main branch if it doesn't exist
            try:
                source = repo.get_branch("main")
            except:
                # Create initial commit on main
                repo.create_file(
                    path="README.md",
                    message="Initial commit",
                    content="# " + repo_name,
                    branch="main"
                )
                source = repo.get_branch("main")
            
            repo.create_git_ref(ref=f"refs/heads/{branch_name}", sha=source.commit.sha)
            
            repo.create_file(
                path=file_path,
                message=commit_message,
                content=content,
                branch=branch_name
            )
            
            repo.create_pull(
                title=f"Update {file_path}",
                body=commit_message,
                head=branch_name,
                base="main"
            )
            return True
        except Exception as e:
            print(f"Error pushing code: {e}")
            return False

# Uso
if __name__ == "__main__":
    assistant = GitHubAssistant()
    
    # Criar novo repositório
    repo = assistant.create_repo(
        name="hubgenial-xgenial-mcp",
        description="GitHub Assistant powered by MCP"
    )
    
    # Enviar este código para o repositório
    with open(__file__, 'r') as file:
        assistant.push_code(
            repo_name="hubgenial-xgenial-mcp",
            file_path="github_assistant.py",
            content=file.read(),
            commit_message="Initial commit: GitHub Assistant implementation"
        )