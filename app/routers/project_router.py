# app/routers/project_router.py
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import List
from .. import crud, models
from .testcase_router import run_test_case_in_background

router = APIRouter(
    prefix="/api/projects",
    tags=["项目"],
)

@router.post("/", response_model=models.Project)
def create_project(project: models.ProjectCreate):
    """
    创建新项目。
    """
    try:
        return crud.create_project(project)
    except Exception as e:
        # 这可能是重复的名称错误或其他数据库问题
        raise HTTPException(status_code=400, detail=f"Could not create project: {e}")

@router.get("/", response_model=List[models.Project])
def get_all_projects():
    """
    检索所有项目。
    """
    return crud.get_all_projects()

@router.get("/{project_id}", response_model=models.Project)
def get_project(project_id: int):
    """
    通过其ID检索单个项目。
    """
    db_project = crud.get_project(project_id)
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return db_project

@router.put("/{project_id}", response_model=models.Project)
def update_project(project_id: int, project: models.ProjectUpdate):
    """
    更新项目。
    """
    db_project = crud.get_project(project_id)
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    try:
        return crud.update_project(project_id=project_id, project=project)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating project: {e}")

@router.delete("/{project_id}")
def delete_project(project_id: int):
    """
    删除项目及其所有关联的测试用例和步骤。
    """
    db_project = crud.get_project(project_id)
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    
    try:
        result = crud.delete_project(project_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting project: {e}")

@router.get("/{project_id}/modules", response_model=List[models.Module])
def get_project_modules(project_id: int):
    """
    检索特定项目的所有模块。
    """
    db_project = crud.get_project(project_id)
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return crud.get_modules_for_project(project_id)

@router.post("/{project_id}/run")
def run_project_test_cases(project_id: int, background_tasks: BackgroundTasks):
    """
    触发项目中所有测试用例的运行。
    """
    db_project = crud.get_project(project_id)
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    test_cases = crud.get_all_test_cases_for_project(project_id)
    if not test_cases:
        return {"message": f"此项目中没有要运行的测试用例。"}

    for case in test_cases:
        background_tasks.add_task(run_test_case_in_background, case['id'])
    
    return {"message": f"已为项目 {project_id} 中的 {len(test_cases)} 个测试用例触发运行。"}



@router.get("/{project_id}/testcases", response_model=List[models.TestCase])
def get_project_test_cases(project_id: int):
    """
    检索特定项目的所有测试用例。
    """
    db_project = crud.get_project(project_id)
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return crud.get_all_test_cases_for_project(project_id)
