from typing import List

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas, oauth2
from ..database import get_db

router = APIRouter(
	prefix="/playlists",
	tags=["Playlists"]
)

# @router.get("/videos/{id}")
# def get_video(id: int, db: Session = Depends(get_db)):
# 	toGet = db.query(models.PlayList).filter(models.PlayList.id == id).first()
# 	if not toGet:
# 		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"playlist with id : {id} does not exist")
# 	toGet = db.query(models.Video).filter(models.Video.playlist_id == id).all()
# 	if not toGet:
# 		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
# 		                    detail=f"playlist with id {id} does not have any video")
# 	return toGet


@router.get("/all",response_model=List[schemas.PlaylistOut])
def get_playlists(db: Session = Depends(get_db)):
	playlists = db.query(models.PlayList).all()
	return playlists

@router.get("/",response_model=List[schemas.PlaylistOut])
def get_playlists(db: Session = Depends(get_db),current_user = Depends(oauth2.get_current_user)):
	toGet = db.query(models.PlayList).filter(models.PlayList.owner_id == current_user.id).all()
	return toGet

@router.get("/{id}",response_model=schemas.PlaylistOut)
def get_playlist(id: int, db: Session = Depends(get_db)):
	toGet = db.query(models.PlayList).filter(models.PlayList.id == id).first()
	if not toGet:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"playlist with id : {id} does not exist")
	return toGet


@router.post("/",response_model=schemas.PlaylistOut)
def add_playlist(playlist: schemas.CreatePlaylist, db: Session = Depends(get_db),current_user = Depends(oauth2.get_current_user)):
	toPost = models.PlayList(owner_id = current_user.id,**playlist.dict())
	db.add(toPost)
	db.commit()
	db.refresh(toPost)
	return toPost


@router.put("/{id}",response_model=schemas.PlaylistOut)
def update_playlist(id: int, updated: schemas.CreatePlaylist, db: Session = Depends(get_db),current_user = Depends(oauth2.get_current_user)):

	toUpdate = db.query(models.PlayList).filter(models.PlayList.id == id)
	if not toUpdate.first():
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"playlist with id : {id} does not exist")
	if toUpdate.first().owner_id != current_user.id :
		raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")
	updated  = updated.dict()
	updated["owner_id"] = current_user.id
	toUpdate.update(updated, synchronize_session=False)
	db.commit()
	return toUpdate.first()


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_playlist(id: int, db: Session = Depends(get_db),current_user = Depends(oauth2.get_current_user)):
	toDelete = db.query(models.PlayList).filter(models.PlayList.id == id)
	if not toDelete.first():
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"playlist with id : {id} does not exist")
	if toDelete.first().owner_id != current_user.id :
		raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")
	toDelete.delete(synchronize_session=False)
	db.commit()

@router.post("/{playlist_id}/{video_id}")
def add_video_to_playlist(playlist_id : int ,video_id : int, db: Session = Depends(get_db),
                          current_user=Depends(oauth2.get_current_user)):
	if not db.query(models.Video).filter(models.Video.id == video_id).first():
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
		                    detail=f"Video with id : {video_id} does not exist")
	playlist = db.query(models.PlayList).filter(models.PlayList.id == playlist_id).first()
	if not playlist:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
		                    detail=f"Playlist with id : {playlist_id} does not exist")
	if playlist.owner_id != current_user.id:
		raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")
	toEdit = models.PlaylistVideos(playlist_id = playlist_id , video_id = video_id)
	try:
		db.add(toEdit)
		db.commit()
		db.refresh(toEdit)
		return toEdit
	except:
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="video already in the playlist")

@router.delete("/{playlist_id}/{video_id}",status_code=status.HTTP_204_NO_CONTENT)
def add_video_to_playlist(playlist_id : int , video_id : int , db: Session = Depends(get_db),
                          current_user=Depends(oauth2.get_current_user)):
	playlist = db.query(models.PlayList).filter(models.PlayList.id == playlist_id).first()
	if playlist :
		if playlist.owner_id != current_user.id:
			raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")
	else : 	raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Playlist does not exist")
	toDelete = db.query(models.PlaylistVideos).filter(models.PlaylistVideos.video_id == video_id,
	                                                  models.PlaylistVideos.playlist_id == playlist_id)
	if not toDelete.first():
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not in the playlist")
	toDelete.delete(synchronize_session=False)
	db.commit()

