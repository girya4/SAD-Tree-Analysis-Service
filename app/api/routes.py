from fastapi import APIRouter, Depends, HTTPException, status, Request, UploadFile, File, Response
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.auth import get_current_user, verify_task_ownership, generate_cookie_token
from app.models.task import Task, TaskStatus
from app.models.user import User
from app.api.schemas import TaskResponse, TaskStatusResponse, NewTaskResponse, WebhookPayload
from app.utils.file_utils import validate_file, generate_unique_filename, save_uploaded_file
from app.services.image_processor import process_image
from config import settings
import json

router = APIRouter()


@router.get("/", response_model=dict)
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Image processing service is running"}


@router.get("/api/get-session")
async def get_session(
    request: Request,
    user: User = Depends(get_current_user),
    response: Response = None
):
    """Get or create user session"""
    cookie_token = request.cookies.get(settings.cookie_name)
    
    if not cookie_token:
        # Generate new cookie token
        cookie_token = generate_cookie_token()
        # Update user with new token
        db = next(get_db())
        try:
            user.cookie_token = cookie_token
            db.commit()
        finally:
            db.close()
        
        # Set cookie in response
        response.set_cookie(
            key=settings.cookie_name,
            value=cookie_token,
            max_age=settings.cookie_max_age,
            httponly=True,
            secure=False,
            samesite="lax"
        )
    
    return {"user_id": user.id, "cookie_token": cookie_token}


@router.post("/api/newTask", response_model=NewTaskResponse)
async def create_new_task(
    request: Request,
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new image processing task"""
    try:
        # Validate file
        validate_file(file)
        
        # Generate unique filename
        filename = generate_unique_filename(file.filename)
        
        # Save uploaded file
        file_path = save_uploaded_file(file, filename)
        
        # Create task in database
        task = Task(
            user_id=user.id,
            status=TaskStatus.PENDING,
            original_path=file_path,
            task_metadata=json.dumps({
                "original_filename": file.filename,
                "file_size": file.size
            })
        )
        db.add(task)
        db.commit()
        db.refresh(task)
        
        # Start image processing task
        process_image.delay(task.id)
        
        response = NewTaskResponse(
            task_id=task.id,
            message="Task created successfully"
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create task: {str(e)}"
        )


@router.get("/api/isReady/{task_id}", response_model=TaskStatusResponse)
async def check_task_status(
    task_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Check if task is ready"""
    try:
        
        # Verify task ownership
        if not verify_task_ownership(db, task_id, user.id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        
        # Get task from database
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        
        return TaskStatusResponse(
            id=task.id,
            status=task.status,
            result_path=task.result_path,
            task_metadata=task.task_metadata
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get task status: {str(e)}"
        )


@router.post("/api/webhook/task-complete")
async def webhook_task_complete(
    payload: WebhookPayload,
    db: Session = Depends(get_db)
):
    """Webhook endpoint for task completion updates"""
    try:
        # Get task from database
        task = db.query(Task).filter(Task.id == payload.task_id).first()
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        
        # Update task status
        task.status = payload.status
        if payload.result_path:
            task.result_path = payload.result_path
        if payload.task_metadata:
            task.task_metadata = payload.task_metadata
        
        db.commit()
        
        return {"message": "Task updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update task: {str(e)}"
        )
