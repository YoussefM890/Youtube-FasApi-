from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import models, schemas, oauth2
from app.database import get_db

router = APIRouter(
	prefix="/videos",
	tags=["Videos"]
)



@router.get("/all",response_model=List[schemas.VideoOut])
def get_all_videos(db: Session = Depends(get_db)):
	toGet = db.query(models.Video).all()
	return toGet

@router.get("/",response_model=List[schemas.VideoOut])
def get_all_your_video(db: Session = Depends(get_db),current_user = Depends(oauth2.get_current_user)):
	toGet = db.query(models.Video).filter(models.Video.owner_id == current_user.id).all()
	return toGet

@router.get("/{id}",response_model=schemas.VideoOut)
def get_one_video(id: int, db: Session = Depends(get_db)):
	toGet = db.query(models.Video).filter(models.Video.id == id).first()
	if not toGet:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Video with id : {id} does not exist")
	return toGet


@router.post("/", status_code=status.HTTP_201_CREATED,response_model=schemas.VideoOut)
def add_video(video: schemas.CreateVideo, db: Session = Depends(get_db),current_user = Depends(oauth2.get_current_user)):
	toPost = models.Video(owner_id = current_user.id , **video.dict())
	db.add(toPost)
	db.commit()
	db.refresh(toPost)
	return toPost


@router.put("/{id}",response_model=schemas.VideoOut)
def update_video(id: int, updated: schemas.CreateVideo, db: Session = Depends(get_db),current_user = Depends(oauth2.get_current_user)):
	toUpdate = db.query(models.Video).filter(models.Video.id == id)
	if not toUpdate.first():
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Video with id : {id} does not exist")
	if db.query(models.Video).filter(models.Video.id == id).first().owner_id != current_user.id :
		raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")
	toUpdate.update(updated.dict(), synchronize_session=False)
	db.commit()
	return toUpdate.first()


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_video(id: int, db: Session = Depends(get_db),current_user = Depends(oauth2.get_current_user)):
	toDelete = db.query(models.Video).filter(models.Video.id == id)
	if not toDelete.first():
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Video with id : {id} does not exist")
	if db.query(models.Video).filter(models.Video.id == id).first().owner_id != current_user.id :
		raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")
	toDelete.delete(synchronize_session=False)
	db.commit()

