from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import models, schemas,oauth2
from app.database import get_db
router = APIRouter(
	prefix="/channels",
	tags=["Channels"]
)

@router.get("/",response_model=List[schemas.ChannelOut])
def get_channel(db: Session = Depends(get_db)):
	toGet = db.query(models.Channel).all()
	return toGet


@router.get("/{id}",response_model=schemas.ChannelOut)
def get_channel(id: int, db: Session = Depends(get_db)):
	toGet = db.query(models.Channel).filter(models.Channel.id == id).first()
	if not toGet:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Channel with id : {id} does not exist")
	return toGet


@router.post("/",response_model=schemas.ChannelOut)
def add_channel(channel: schemas.CreateChannel, db: Session = Depends(get_db),current_user = Depends(oauth2.get_current_user)):
	current_channel = db.query(models.Channel).filter(models.Channel.owner_id == current_user.id).first()
	if current_channel : 
		raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED, detail=f"You already have a channel")
	toPost = models.Channel(owner_id=current_user.id,**channel.dict())
	db.add(toPost)
	db.commit()
	db.refresh(toPost)
	return toPost


@router.put("/{id}",response_model=schemas.ChannelOut)
def update_channel(id: int, updated: schemas.CreateChannel, db: Session = Depends(get_db),current_user = Depends(oauth2.get_current_user)):
	toUpdate_query = db.query(models.Channel).filter(models.Channel.id == id)
	toUpdate = toUpdate_query.first()
	if not toUpdate :
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Channel with id : {id} does not exist")
	toUpdate_query.update(updated.dict(), synchronize_session=False)
	if toUpdate.owner_id != current_user.id :
		raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Not authorized to perform requested action")
	db.commit()
	return toUpdate


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_channel(id: int, db: Session = Depends(get_db),current_user = Depends(oauth2.get_current_user)):
	toDelete = db.query(models.Channel).filter(models.Channel.id == id)
	if not toDelete.first():
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Channel with id : {id} does not exist")
	if toDelete.first().owner_id != current_user.id :
		raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Not authorized to perform requested action")
	toDelete.delete(synchronize_session=False)
	db.commit()
