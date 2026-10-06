from fastapi import FastAPI,HTTPException,status,Query,Depends,Header
from pydantic import BaseModel,Field
from typing import Optional,Annotated





app=FastAPI(title='Myfirst fastapiapp')

class ItemCreate(BaseModel):
    name:str=Field(...,min_length=2,max_length=50)
    price:float=Field(...,gt=0)
    is_in_stock:bool =True

class ItemUpdate(BaseModel):
    name:Optional[str]=Field(None,min_length=2,max_length=50)
    price:Optional[float]=Field(None,gt=0)
    is_in_stock:Optional[bool]=None

class ItemResponse(BaseModel):
    id:int
    name:str
    price:float
    is_in_stock:bool

db_items:dict[int, dict]={}
id_counter = 1





###############################################
#CRUD
#create post
#response_model is a parameter passed to FastAPI route decorators (like @app.get() or @app.post()) that defines the schema used to validate, serialize, filter, and document outgoing HTTP responses.
@app.post("/items",response_model=ItemResponse,status_code=status.HTTP_201_CREATED)
def create_item(payload:ItemCreate):
        global id_counter
        new_item ={
            "id":id_counter,
            "name":payload.name,
            "price":payload.price,
            "is_in_stock":payload.is_in_stock,
        }
        db_items[id_counter]=new_item
        id_counter +=1
        return new_item


@app.get("/items",response_model=list[ItemResponse])
def get_all_items(in_stock_only: Optional[bool] = Query(None, description="Filter items by stock availability"),
    max_price: Optional[float] = Query(None, description="Filter items below a certain price")):
     items=list(db_items.values())
     if in_stock_only is not None:
          items=[i for i in items if i["is_in_stock"]== in_stock_only]
     if max_price is not None:
          items=[i for i in items if i["price"]==max_price]
     return items

# READ ONE (GET by ID)
@app.get("/items/{item_id}", response_model=ItemResponse)
def get_item_by_id(item_id: int):
    item = db_items.get(item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Item with ID {item_id} does not exist"
        )
    return item

# UPDATE (PATCH by ID)
@app.patch("/items/{item_id}", response_model=ItemResponse)
def update_item(item_id: int, updates: ItemUpdate):
    item = db_items.get(item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Item with ID {item_id} does not exist"
        )
    
    # Exclude unset fields so only provided keys get updated
    update_data = updates.model_dump(exclude_unset=True)
    item.update(update_data)
    return item

# DELETE (DELETE by ID)
@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int):
    if item_id not in db_items:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Item with ID {item_id} does not exist"
        )
    del db_items[item_id]
    return None


##############################################################################################
#Depecndency Injection


# Depends
# What it is: A tool that activates FastAPI's Dependency Injection system.

# What it does: It tells FastAPI: "Before running this route handler, 
# execute this other helper function/class, resolve what it needs, 
# and inject its output into my route's parameter."

def pagination_params(skip:str):
    if skip=='ayushsecret':
        return "login successful"
    else:
        return "rejected"

# 2. Inject it into a route using Depends()
@app.get("/pages/")
def read_items(pagination: Annotated[str, Depends(pagination_params)]):
    return pagination

@app.get("/pageusers/")
def read_users(pagination: Annotated[dict, Depends(pagination_params)]):
    return pagination



# Header
# What it is: A parameter extractor for reading values from incoming HTTP request headers.

# What it does: It tells FastAPI to look specifically inside the 
# request headers (not query parameters or the JSON body) for a
#  given variable. It automatically converts snake_case to kebab-case 
# (x_token maps to the X-Token HTTP header) and documents the requirement in Swagger UI.

# # Example:
#For sensiticec data cannot be enteredd in the query parameter therefore we use the Heaader

# Python
@app.get("/cookies")
def read_items(x_token: str = Header(..., description="Authentication secret")):
    # Extracts the value sent in HTTP header: "X-Token: my-secret-key"
    return {"received_token": x_token}


# HTTPException
# What it is: A specialized Python exception designed to halt request execution immediately and send a standard HTTP error response to the client.

# What it does: Instead of your server crashing with an unhandled 500 Internal Server Error, throwing HTTPException returns a clean, formatted JSON payload ({"detail": "..."}) with the HTTP status code you specify.

# Example:

# Python
@app.get("/items/{item_id}")
def get_item(item_id: int):
    if item_id > 100:
        raise HTTPException(
            status_code=404,
            detail="Item not found in inventory"
        )
    return {"item_id": item_id}


# status
# What it is: A module containing human-readable constants for standard HTTP status codes (provided by Starlette, which FastAPI builds on).

# What it does: Prevents "magic numbers" in your codebase. Instead of typing 201, 401, or 404, you use descriptive constants like status.HTTP_201_CREATED or status.HTTP_404_NOT_FOUND, making the code self-documenting and less error-prone.

# Example:

# Python
# Instead of hardcoding: status_code=201
@app.post("/items", status_code=status.HTTP_201_CREATED)
def create_item(name: str):
    return {"name": name}