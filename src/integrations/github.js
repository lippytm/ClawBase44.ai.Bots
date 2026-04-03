/**
 * GitHub Repositories integration module.
 * Connects to the GitHub REST API for cross-repository workflow triggers,
 * file reads, and repository dispatches.
 */

const fetch = (...args) =>
  import("node-fetch").then(({ default: f }) => f(...args));

class GitHubIntegration {
  constructor(config = {}) {
    this.apiUrl = config.apiUrl || "https://api.github.com";
    this.token = config.token || process.env.GITHUB_TOKEN;
    this.repos = config.repos || [];
  }

  _headers() {
    return {
      Accept: "application/vnd.github+json",
      Authorization: `Bearer ${this.token}`,
      "X-GitHub-Api-Version": "2022-11-28",
    };
  }

  async dispatchWorkflow(owner, repo, workflowId, ref = "main", inputs = {}) {
    const url = `${this.apiUrl}/repos/${owner}/${repo}/actions/workflows/${workflowId}/dispatches`;
    const res = await fetch(url, {
      method: "POST",
      headers: this._headers(),
      body: JSON.stringify({ ref, inputs }),
    });
    if (!res.ok) {
      throw new Error(`GitHub workflow dispatch failed: ${res.status} ${res.statusText}`);
    }
  }

  async repositoryDispatch(owner, repo, eventType, clientPayload = {}) {
    const url = `${this.apiUrl}/repos/${owner}/${repo}/dispatches`;
    const res = await fetch(url, {
      method: "POST",
      headers: this._headers(),
      body: JSON.stringify({ event_type: eventType, client_payload: clientPayload }),
    });
    if (!res.ok) {
      throw new Error(`GitHub repository dispatch failed: ${res.status} ${res.statusText}`);
    }
  }

  async broadcastDispatch(eventType, clientPayload = {}) {
    const results = await Promise.allSettled(
      this.repos.map((repo) => {
        const [owner, repoName] = repo.split("/");
        return this.repositoryDispatch(owner, repoName, eventType, clientPayload);
      })
    );
    return results;
  }

  async getFileContents(owner, repo, path, ref = "main") {
    const url = `${this.apiUrl}/repos/${owner}/${repo}/contents/${path}?ref=${ref}`;
    const res = await fetch(url, { headers: this._headers() });
    if (!res.ok) {
      throw new Error(`GitHub get file failed: ${res.status} ${res.statusText}`);
    }
    const json = await res.json();
    return Buffer.from(json.content, "base64").toString("utf8");
  }

  async listWorkflowRuns(owner, repo, workflowId) {
    const url = `${this.apiUrl}/repos/${owner}/${repo}/actions/workflows/${workflowId}/runs`;
    const res = await fetch(url, { headers: this._headers() });
    if (!res.ok) {
      throw new Error(`GitHub list workflow runs failed: ${res.status} ${res.statusText}`);
    }
    return res.json();
  }
}

module.exports = GitHubIntegration;
