import validators
from starlette.datastructures import URL
from typing import List
from fastapi import Depends, FastAPI, HTTPException,Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from . import models, schemas
from .database import SessionLocal, engine, get_db
from .utils import raise_bad_request, raise_not_found
from . import crud, models, schemas
from .config import get_settings




app = FastAPI()
settings = get_settings()

###############################################
# Create the database tables
models.Base.metadata.create_all(bind=engine)



@app.get("/")
def read_root():
    return {"message": "Welcome to the URL Shortener API!"} 


@app.post("/url", response_model=schemas.URLInfo,)
def create_url(url: schemas.URLBase,  db: Session = Depends(get_db)):
    if not validators.url(url.target_url):
        raise_bad_request(message = "Provided URL is not valid")
    
    db_url = crud.create_db_url(db=db, url=url)
    return get_admin_info(db_url)


@app.get("/{url_key}")
def forward_to_target_url(
    url_key: str,
    request: Request,
    db: Session = Depends(get_db)
):
    print(f"Got url_key: {url_key}")
    db_url = crud.get_db_url_by_key(db=db, url_key=url_key)
    print(f"DB URL: {db_url}")
    if db_url:
        crud.update_db_clicks(db=db, db_url=db_url)
        return RedirectResponse(db_url.target_url)
    else:
        raise_not_found(request)


@app.get("/admin/",  response_model= List[schemas.URLInfo])
def get_all_urls(
     db: Session = Depends(get_db)
):
    if db_urls := crud.get_db_all_urls(db):
           return [get_admin_info(db_url) for db_url in db_urls]
    else:
        raise HTTPException(
            status_code=404,
            detail="No URLs found in the database."
        )


@app.get("/admin/{secret_key}", name="admin", response_model=schemas.URLInfo)
def get_url_info(
    secret_key: str, request: Request, db: Session = Depends(get_db)
):
    if db_url := crud.get_db_url_by_secret_key(db, secret_key=secret_key):
        return get_admin_info(db_url)
    else:
        raise_not_found(request)


@app.delete("/admin/{secret_key}")
def delete_url(
    secret_key: str, request: Request, db: Session = Depends(get_db)
):
    if db_url := crud.deactivate_db_url_by_secret_key(db, secret_key=secret_key):
        message = f"Successfully deleted shortened URL for '{db_url.target_url}'"
        return {"detail": message}
    else:
        raise_not_found(request)





def get_admin_info(db_url: models.URL) -> schemas.URLInfo:
    base_url = URL(settings.base_url)
    admin_endpoint = app.url_path_for("admin", secret_key=db_url.secret_key)
     # ✅ BUILD a Pydantic object directly, do NOT return the ORM!
    return schemas.URLInfo(
        key=db_url.key,
        secret_key=db_url.secret_key,
        target_url=db_url.target_url,
        is_active=db_url.is_active,
        clicks=db_url.clicks,
        url=str(base_url.replace(path=db_url.key)),
        admin_url=str(base_url.replace(path=admin_endpoint)),
    )


