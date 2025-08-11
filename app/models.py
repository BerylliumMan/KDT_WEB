# app/models.py
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

# ----------------------------
# 基础模型
# ----------------------------

class ProjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    base_url: Optional[str] = None
    browser: str = Field("chromium", pattern="^(chromium|firefox|webkit)$")
    headless: bool = True

class TestCaseBase(BaseModel):
    project_id: int
    module_id: Optional[int] = None
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None

class TestStepBase(BaseModel):
    case_id: int
    step_order: int = Field(..., gt=0)
    keyword: str
    locator: Optional[str] = None
    value: Optional[str] = None
    description: Optional[str] = None

class ModuleBase(BaseModel):
    project_id: int
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None

# ----------------------------
# 创建模型（用于POST请求）
# ----------------------------

class ProjectCreate(ProjectBase):
    pass

class ModuleCreate(ModuleBase):
    pass


class ProjectUpdate(ProjectBase):
    pass

class TestStepUpdate(BaseModel):
    id: Optional[int] = None # ID is present for existing steps
    step_order: int = Field(..., gt=0)
    keyword: str
    locator: Optional[str] = None
    value: Optional[str] = None
    description: Optional[str] = None

class TestCaseUpdate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    module_id: Optional[int] = None
    steps: List[TestStepUpdate] = []

class TestStepCreatePayload(BaseModel):
    step_order: int = Field(..., gt=0)
    keyword: str
    locator: Optional[str] = None
    value: Optional[str] = None
    description: Optional[str] = None


class TestCaseCreate(TestCaseBase):
    steps: List[TestStepCreatePayload] = []

class TestStepCreate(TestStepBase):
    pass

# ----------------------------
# 响应模型（用于GET请求）
# ----------------------------

class TestStep(TestStepBase):
    id: int

class Module(ModuleBase):
    id: int
    created_at: datetime

class ModuleUpdate(ModuleBase):
    pass

class TestCase(TestCaseBase):
    id: int
    created_at: datetime
    steps: List[TestStep] = []

class Project(ProjectBase):
    id: int
    created_at: datetime

class TestRun(BaseModel):
    id: int
    case_id: int
    status: str
    start_time: datetime
    end_time: datetime
    duration: float
    report_path: Optional[str] = None
    log_path: Optional[str] = None

class TestCasePage(BaseModel):
    items: List[TestCase]
    total_items: int
    page: int
    size: int

