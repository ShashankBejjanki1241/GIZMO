from pathlib import Path
import subprocess, tempfile, textwrap

CRITICAL = {"package.json","package-lock.json","pnpm-lock.yaml","yarn.lock"}

def apply_unified_diff(repo_path: str | Path, diff_text: str):
    """
    Apply a unified diff safely.
    - Dry-run first.
    - Reject deletions of critical files.
    """
    repo = Path(repo_path)
    if any(line.startswith("---") and any(c in line for c in CRITICAL) for line in diff_text.splitlines()):
        return False, "Critical file modification blocked"

    with tempfile.NamedTemporaryFile(mode="w", delete=False) as tmp:
        tmp.write(diff_text)
        tmp.flush()
        # Dry run
        dry = subprocess.run(["git", "apply", "--check", tmp.name], cwd=repo, capture_output=True, text=True)
        if dry.returncode != 0:
            return False, f"Patch check failed:\n{dry.stderr}"
        # Apply
        real = subprocess.run(["git", "apply", tmp.name], cwd=repo, capture_output=True, text=True)
        if real.returncode != 0:
            return False, f"Patch apply failed:\n{real.stderr}"
    return True, "Patch applied"
