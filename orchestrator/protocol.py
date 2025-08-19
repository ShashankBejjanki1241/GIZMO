from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from uuid import uuid4

Role = Literal["planner","coder","tester","orchestrator","user","system"]
MsgType = Literal["plan","code_patch","test_report","status","request"]

class Artifact(BaseModel):
    kind: Literal["diff","file","log"]
    path: str

class Message(BaseModel):
    id: str = Field(default_factory=lambda: f"msg-{uuid4()}")
    task_id: str
    type: MsgType
    sender: Role
    recipient: Role
    content: str
    artifacts: List[Artifact] = []
    ts: float

class TaskRequest(BaseModel):
    task_id: str
    template: Literal["react","express","flask"]
    instruction: str
    model: Optional[str] = None  # e.g., gpt-4o-mini

def event(task_id: str, stage: str, data: dict):
    return {"task_id": task_id, "stage": stage, **data}

