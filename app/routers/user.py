from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import models, schemas, utils, oauth2
from app.database import get_db


router = APIRouter(
	prefix="/users",
	tags=["Users"]
)

@router.get("/",response_model=List[schemas.UserOut])
def get_user(db: Session = Depends(get_db)):
	toGet = db.query(models.User).all()
	return toGet


@router.get("/{id}",response_model=schemas.UserOut)
def get_user(id: int, db: Session = Depends(get_db)):
	toGet = db.query(models.User).filter(models.User.id == id).first()
	if not toGet:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id : {id} does not exist")
	return toGet


@router.post("/",response_model=schemas.UserOut,status_code=status.HTTP_201_CREATED)
def adduser(user: schemas.CreateUser, db: Session = Depends(get_db)):
	try :
		hashed_password = utils.hash(user.password)
		print(user.password,hashed_password)
		user.password = hashed_password
		toPost = models.User(**user.dict())
		db.add(toPost)
		db.commit()
		db.refresh(toPost)
		return toPost
	except :
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="User with this Email already exist")


@router.put("/",response_model=schemas.UserOut)
def update_user(db: Session = Depends(get_db),current_user = Depends(oauth2.get_current_user)):
	toUpdate = db.query(models.User).filter(models.User.id == current_user.id)
	if not toUpdate.first():
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id : {id} does not exist")
	db.commit()
	return toUpdate.first()


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(db: Session = Depends(get_db),current_user = Depends(oauth2.get_current_user)):
	toDelete = db.query(models.User).filter(models.User.id == current_user.id)
	if not toDelete.first():
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id : {id} does not exist")
	toDelete.delete(synchronize_session=False)
	db.commit()
