from typing import Dict, Any, Optional


def format_push_message(payload: Dict[str, Any]) -> str:
    repository = payload.get("repository", {}).get("full_name", "unknown")
    ref = payload.get("ref", "unknown")
    commits = payload.get("commits", [])
    pusher = payload.get("pusher", {}).get("name", "unknown")
    
    message = f"""🔄 **PUSH EVENT**

📦 **Repository:** `{repository}`
🌿 **Branch:** `{ref.replace('refs/heads/', '')}`
👤 **Pusher:** `{pusher}`
📝 **Commits ({len(commits)}):**"""

    for commit in commits[:5]:
        msg = commit.get("message", "").split("\n")[0][:100]
        author = commit.get("author", {}).get("name", "unknown")
        message += f"\n• `{msg}` - {author}"
    
    if len(commits) > 5:
        message += f"\n• _...and {len(commits) - 5} more commits_"
    
    return message


def format_pr_message(payload: Dict[str, Any]) -> str:
    action = payload.get("action", "unknown")
    pr = payload.get("pull_request", {})
    
    repository = payload.get("repository", {}).get("full_name", "unknown")
    pr_title = pr.get("title", "unknown")
    pr_number = payload.get("pull_request", {}).get("number", "?")
    user = pr.get("user", {}).get("login", "unknown")
    state = pr.get("state", "unknown")
    merged = pr.get("merged", False)
    
    action_emoji = {
        "opened": "🆕",
        "closed": "❌",
        "synchronize": "🔄",
        "reopened": "🔁",
    }.get(action, "📋")
    
    state_info = ""
    if action == "closed":
        state_info = " (MERGED ✅)" if merged else " (CLOSED)"
    
    message = f"""📥 **PULL REQUEST {action.upper()}**

📦 **Repository:** `{repository}`
#{pr_number} **{pr_title}**
👤 **User:** `{user}`
📊 **State:** `{state}`{state_info}
🔗 **Link:** {payload.get('pull_request', {}).get('html_url', 'N/A')}"""

    return message


def format_issue_message(payload: Dict[str, Any]) -> str:
    action = payload.get("action", "unknown")
    issue = payload.get("issue", {})
    
    repository = payload.get("repository", {}).get("full_name", "unknown")
    issue_title = issue.get("title", "unknown")
    issue_number = issue.get("number", "?")
    user = issue.get("user", {}).get("login", "unknown")
    state = issue.get("state", "unknown")
    labels = [l.get("name") for l in issue.get("labels", [])[:3]]
    
    action_emoji = {
        "opened": "🆕",
        "closed": "✅",
        "reopened": "🔁",
    }.get(action, "📋")
    
    labels_str = ", ".join([f"`{l}`" for l in labels]) if labels else "None"
    
    message = f"""{action_emoji} **ISSUE {action.upper()}**

📦 **Repository:** `{repository}`
#{issue_number} **{issue_title}**
👤 **User:** `{user}`
📊 **State:** `{state}`
🏷️ **Labels:** {labels_str}
🔗 **Link:** {issue.get('html_url', 'N/A')}"""

    return message
