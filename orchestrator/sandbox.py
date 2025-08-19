import asyncio, json, os, shlex, tempfile
from pathlib import Path

ALLOWED_CMDS = {"npm i","npm test","pytest","node","python"}

class Sandbox:
    def __init__(self, task_id: str, template: str):
        self.task_id = task_id
        self.template = template
        self.repo_path = Path(f"/tmp/aicode/{task_id}/repo")

    async def prepare(self):
        # Create a tiny template repo (TODO: replace with real templates)
        self.repo_path.mkdir(parents=True, exist_ok=True)
        (self.repo_path / "package.json").write_text('{"name":"demo","scripts":{"test":"echo \\"1 test passed\\""}}')
        (self.repo_path / "index.js").write_text('module.exports = { add:(a,b)=>a+b }')
        await self._git_init()

    async def _git_init(self):
        cmds = [
            "git init -q",
            "git add .",
            'git commit -m "init" -q'
        ]
        for c in cmds:
            await self._local(c)

    def describe_repo(self):
        # Could walk files to give the coder context (keep small)
        return {"root": str(self.repo_path), "files": [p.name for p in self.repo_path.iterdir()]}

    async def run_tests(self):
        # In MVP, run locally with guardrails (later: run in Docker)
        out, err, code = await self._local("npm test")
        passed = 1 if code == 0 else 0
        failed = 0 if code == 0 else 1
        return {"passed": passed, "failed": failed, "stdout": out[-2000:], "stderr": err[-2000:]}

    async def _local(self, cmd: str):
        # Minimal guard; replace with containerized execution ASAP
        if cmd not in ALLOWED_CMDS and not cmd.startswith("git "):
            raise RuntimeError(f"Command not allowed: {cmd}")
        proc = await asyncio.create_subprocess_shell(
            cmd, cwd=self.repo_path, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        out, err = await proc.communicate()
        return out.decode(), err.decode(), proc.returncode
