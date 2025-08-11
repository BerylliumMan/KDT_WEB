# app/routers/testcase_router.py
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Dict
import asyncio
import subprocess
import sys
import os

from .. import crud, models
from core.runner import run_test_case
from core.keyword_engine import KeywordEngine


router = APIRouter(
    prefix="/api/testcases",
    tags=["Test Cases"],
)

@router.get("/keywords", response_model=Dict[str, Dict])
def get_keywords():
    """
    返回可用关键词及其定义的字典。
    """
    return KeywordEngine.KEYWORD_DEFINITIONS


@router.post("/", response_model=models.TestCase)
def create_test_case(case: models.TestCaseCreate):
    """
    创建带有步骤的新测试用例。
    """
    # Verify project exists
    db_project = crud.get_project(case.project_id)
    if db_project is None:
        raise HTTPException(status_code=404, detail=f"Project with id {case.project_id} not found")
        
    try:
        return crud.create_test_case(case)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not create test case: {e}")

@router.get("/{case_id}", response_model=models.TestCase)
def get_test_case(case_id: int):
    """
    通过其ID检索单个测试用例，包括其步骤。
    """
    db_case = crud.get_test_case(case_id)
    if db_case is None:
        raise HTTPException(status_code=404, detail="Test case not found")
    return db_case

@router.delete("/{case_id}")
def delete_test_case(case_id: int):
    """
    删除测试用例及其步骤。
    """
    db_case = crud.get_test_case(case_id)
    if db_case is None:
        raise HTTPException(status_code=404, detail="Test case not found")
    
    try:
        return crud.delete_test_case(case_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting test case: {e}")

@router.put("/{case_id}", response_model=models.TestCase)
def update_test_case(case_id: int, case: models.TestCaseUpdate):
    """
    更新测试用例，包括其步骤。
    """
    db_case = crud.get_test_case(case_id)
    if db_case is None:
        raise HTTPException(status_code=404, detail="Test case not found")
    
    try:
        return crud.update_test_case(case_id, case)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating test case: {e}")

@router.get("/module/{module_id}/testcases", response_model=models.TestCasePage)
def get_module_test_cases(module_id: int, page: int = 1, size: int = 20):
    """
    检索特定模块的所有测试用例，并分页。
    """
    db_module = crud.get_module(module_id)
    if db_module is None:
        raise HTTPException(status_code=404, detail="Module not found")
    
    paginated_data = crud.get_all_test_cases_for_module_paginated(module_id, page, size)
    return {
        "items": paginated_data["items"],
        "total_items": paginated_data["total_items"],
        "page": page,
        "size": size
    }

@router.get("/project/{project_id}/testcases", response_model=models.TestCasePage)
def get_project_test_cases(project_id: int, page: int = 1, size: int = 20):
    """
    检索特定项目的所有测试用例，并分页。
    """
    db_project = crud.get_project(project_id)
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    
    paginated_data = crud.get_all_test_cases_for_project_paginated(project_id, page, size)
    return {
        "items": paginated_data["items"],
        "total_items": paginated_data["total_items"],
        "page": page,
        "size": size
    }



def run_test_case_in_background(case_id: int):
    """
    在单独进程中执行测试用例运行器脚本并记录其输出。
    """
    python_executable = sys.executable
    # Go up two levels from routers/ to the project root
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    runner_script_path = os.path.join(project_root, "core", "runner.py")

    command = [python_executable, runner_script_path, str(case_id)]

    try:
        # Execute the command from the project root. Its output will be inherited by the parent.
        process = subprocess.Popen(
            command, 
            cwd=project_root, # Set the working directory
        )
        
        # This is a background task, so we don't wait for it to complete.
        # For debugging, you might want to add: 
        # stdout, stderr = process.communicate()
        # print(f"Runner STDOUT: {stdout}")
        # print(f"Runner STDERR: {stderr}")

    except Exception as e:
        # Log any exception that occurs when trying to start the process
        print(f"[ERROR] Failed to start runner process for case {case_id}: {e}")

@router.post("/{case_id}/run")
def run_test_case_endpoint(case_id: int, background_tasks: BackgroundTasks):
    """
    在后台触发测试用例运行。
    """
    db_case = crud.get_test_case(case_id)
    if db_case is None:
        raise HTTPException(status_code=404, detail="Test case not found")

    # Run the test in a separate process to avoid event loop conflicts
    background_tasks.add_task(run_test_case_in_background, case_id)
    
    return {"message": f"Test case {case_id} run has been triggered in the background."}

@router.post("/module/{module_id}/run")
def run_module_test_cases(module_id: int, background_tasks: BackgroundTasks):
    """
    在后台触发特定模块内所有测试用例的运行。
    """
    db_module = crud.get_module(module_id)
    if db_module is None:
        raise HTTPException(status_code=404, detail="Module not found")
    
    test_cases = crud.get_all_test_cases_for_module(module_id)
    if not test_cases:
        return {"message": f"No test cases found for module {module_id} to run."}

    for case_data in test_cases:
        background_tasks.add_task(run_test_case_in_background, case_data['id'])
    
    return {"message": f"Triggered runs for {len(test_cases)} test cases in module {module_id}."}

@router.post("/project/{project_id}/run")
def run_project_test_cases(project_id: int, background_tasks: BackgroundTasks):
    """
    在后台触发特定项目内所有测试用例的运行。
    """
    db_project = crud.get_project(project_id)
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    
    test_cases = crud.get_all_test_cases_for_project(project_id)
    if not test_cases:
        return {"message": f"No test cases found for project {project_id} to run."}

    for case_data in test_cases:
        background_tasks.add_task(run_test_case_in_background, case_data['id'])
    
    return {"message": f"Triggered runs for {len(test_cases)} test cases in project {project_id}."}
