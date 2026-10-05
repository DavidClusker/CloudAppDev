from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import models, schemas
from database import SessionLocal, engine
from fastapi.middleware.cors import CORSMiddleware
import logging


# Create all tables in the database
models.Base.metadata.create_all(bind=engine)

# Create the FastAPI application
app = FastAPI()

# Add CORS middleware to allow React frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React's default port
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# CREATE - Add a new item

#Logging configuration
logging.basicConfig(filename='server.log', encoding='utf-8', level=logging.DEBUG)


@app.post("/items/", response_model=schemas.Item)
def create_item(item: schemas.ItemCreate, db: Session = Depends(get_db)):
    db_item = models.Item(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    logging.info("A fresh new item created with id=%s", db_item.id)
    return db_item

# READ - Get all items
@app.get("/items/", response_model=list[schemas.Item])
def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = db.query(models.Item).offset(skip).limit(limit).all()
    logging.info("Retrieved everything %s items", len(items))
    return items

# READ - Get a single item by ID
@app.get("/items/{item_id}", response_model=schemas.Item)
def read_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if item is None:
        logging.warning("Item id=%s couldn't be found", item_id)
        raise HTTPException(status_code=404, detail="Item not found")
    logging.info("Retrieved item id=%s", item_id)
    return item

# UPDATE - Update an existing item
@app.put("/items/{item_id}", response_model=schemas.Item)
def update_item(item_id: int, item: schemas.ItemCreate, db: Session = Depends(get_db)):
    db_item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if db_item is None:
        logging.warning("Cannot update as the item is missing id=%s", item_id)
        raise HTTPException(status_code=404, detail="Item not found")

    for field, value in item.dict().items():
        setattr(db_item, field, value)

    db.commit()
    db.refresh(db_item)
    logging.info("Updated item id=%s", item_id)
    return db_item

# DELETE - Remove an item
@app.delete("/items/{item_id}")
def delete_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if item is None:
        logging.warning("Cannot delete as the item is missing id=%s", item_id)
        raise HTTPException(status_code=404, detail="Item not found")

    db.delete(item)
    db.commit()
    logging.info("Deleted item id=%s", item_id)
    return {"message": "Item deleted successfully"}