# app/routers/module_router.py
from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from .. import crud, models

router = APIRouter(
    prefix="/api",
    tags=["模块"]
)

@router.post("/projects/{project_id}/modules/", response_model=models.Module, status_code=status.HTTP_201_CREATED)
async def create_module(project_id: int, module: models.ModuleCreate):
    """
    为项目创建新模块。
    """
    if module.project_id != project_id:
        raise HTTPException(status_code=400, detail="Project ID in path and body must match.")
    db_project = crud.get_project(project_id)
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found.")
    return crud.create_module(module)

@router.get("/projects/{project_id}/modules/", response_model=List[models.Module])
async def get_modules_by_project(project_id: int):
    """
    获取项目的所有模块。
    """
    db_project = crud.get_project(project_id)
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found.")
    return crud.get_modules_for_project(project_id)

@router.get("/modules/{module_id}", response_model=models.Module)
async def get_module(module_id: int):
    """
    获取单个模块。
    """
    db_module = crud.get_module(module_id)
    if not db_module:
        raise HTTPException(status_code=404, detail="Module not found.")
    return db_module

@router.put("/modules/{module_id}", response_model=models.Module)
async def update_module(module_id: int, module: models.ModuleCreate):
    """
    更新单个模块。
    """
    db_module = crud.get_module(module_id)
    if not db_module:
        raise HTTPException(status_code=404, detail="Module not found.")
    updated_module = crud.update_module(module_id, module)
    if not updated_module:
        raise HTTPException(status_code=500, detail="Failed to update module.")
    return updated_module

@router.delete("/modules/{module_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_module(module_id: int):
    """
    删除单个模块。
    """
    db_module = crud.get_module(module_id)
    if not db_module:
        raise HTTPException(status_code=404, detail="Module not found.")
    crud.delete_module(module_id)
    return
