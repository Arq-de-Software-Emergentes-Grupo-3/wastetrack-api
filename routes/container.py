import math
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List
from models.container import Container
from schemas.container import ContainerCreate, ContainerUpdate, ContainerResponse, FavoriteUpdate, CapacityUpdate, LimitUpdate
from config.db import get_db

container = APIRouter(prefix="/containers", tags=["Containers"])

# GET all containers
@container.get("/", response_model=List[ContainerResponse], description="Get a list of all containers")
def get_containers(db: Session = Depends(get_db)):
    containers = db.query(Container).all()
    return containers

# GET container by GUID
@container.get("/{guid}", response_model=ContainerResponse, description="Get a container by GUID")
def get_container(guid: str, db: Session = Depends(get_db)):
    container = db.query(Container).filter(Container.guid == guid).first()
    if not container:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Container not found")
    return container

# GET containers by status
@container.get("/status/{status}", response_model=List[ContainerResponse], description="Get containers by status")
def get_containers_by_status(status: str, db: Session = Depends(get_db)):
    if status not in ["active", "inactive"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Status must be 'active' or 'inactive'")
    containers = db.query(Container).filter(Container.status == status).all()
    return containers

# GET containers nearby by guid
@container.get(
    "/get-nearby-containers/{guid}",
    response_model=List[ContainerResponse],
    description="Get nearby containers relative to a specific container by GUID",
)
def get_nearby_containers_by_guid(guid: str, db: Session = Depends(get_db)):
    def haversine(lat1, lon1, lat2, lon2):
        R = 6371
        phi1 = math.radians(float(lat1))
        phi2 = math.radians(float(lat2))
        d_phi = math.radians(float(lat2) - float(lat1))
        d_lambda = math.radians(float(lon2) - float(lon1))
        a = math.sin(d_phi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    # Buscar contenedor base
    ref = db.query(Container).filter(Container.guid == guid).first()
    if not ref or not ref.latitude or not ref.longitude:
        raise HTTPException(status_code=404, detail="Reference container not found or missing coordinates")

    # Buscar todos los contenedores cercanos (excepto él mismo)
    all_containers = db.query(Container).filter(Container.guid != guid).all()
    nearby = []

    for c in all_containers:
        if c.latitude and c.longitude:
            distance = haversine(ref.latitude, ref.longitude, c.latitude, c.longitude)
            if distance <= 5:
                nearby.append((distance, c))

    nearby_sorted = sorted(nearby, key=lambda x: x[0])
    return [c for _, c in nearby_sorted]


# POST create container
@container.post("/", response_model=dict, status_code=status.HTTP_201_CREATED, description="Create a new container")
def create_container(payload: ContainerCreate, db: Session = Depends(get_db)):
    new_container = Container(**payload.dict())
    db.add(new_container)
    db.commit()
    db.refresh(new_container)
    return {"message": "Container created successfully", "guid": new_container.guid}

# POST simulate sending capacity alert
@container.post("/{guid}/alert", response_model=dict, description="Send capacity alert for a container")
def send_capacity_alert(guid: str, db: Session = Depends(get_db)):
    container = db.query(Container).filter(Container.guid == guid).first()
    if not container:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Container not found")

    if container.capacity > 90:
        return {"message": f"ALERT: Container {guid} is over 90% capacity!"}
    else:
        return {"message": f"Container {guid} is within normal capacity."}
    
# PUT update container by GUID
@container.put("/{guid}", response_model=dict, description="Update a container by GUID")
def update_container(guid: str, payload: ContainerUpdate, db: Session = Depends(get_db)):
    container = db.query(Container).filter(Container.guid == guid).first()
    if not container:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Container not found")

    for key, value in payload.dict(exclude_unset=True).items():
        setattr(container, key, value)

    db.commit()
    return {"message": "Container updated successfully"}

# PUT update container status only
@container.put("/{guid}/status", response_model=dict, description="Update container status")
def update_container_status(guid: str, new_status: str, db: Session = Depends(get_db)):
    if new_status not in ["active", "inactive"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Status must be 'active' or 'inactive'")

    container = db.query(Container).filter(Container.guid == guid).first()
    if not container:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Container not found")

    container.status = new_status
    db.commit()
    return {"message": f"Container status is now '{new_status}'"}

# PUT update isFavorite
@container.put("/{guid}/favorite", response_model=dict, description="Update isFavorite status")
def update_favorite_status(guid: str, payload: FavoriteUpdate, db: Session = Depends(get_db)):
    container = db.query(Container).filter(Container.guid == guid).first()
    if not container:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Container not found")

    container.isFavorite = payload.isFavorite
    db.commit()
    return {"message": f"Container marked as {'favorite' if payload.isFavorite else 'not favorite'}"}

# PUT update capacity
@container.put("/{guid}/capacity", response_model=dict, description="Update container capacity")
def update_capacity(guid: str, payload: CapacityUpdate, db: Session = Depends(get_db)):
    container = db.query(Container).filter(Container.guid == guid).first()
    if not container:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Container not found")

    if payload.capacity < 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Capacity must be non-negative")

    container.capacity = payload.capacity
    db.commit()
    return {"message": f"Container capacity updated to {payload.capacity}"}

# PUT update limit
@container.put("/{guid}/limit", response_model=dict, description="Update container limit")
def update_limit(guid: str, payload: LimitUpdate, db: Session = Depends(get_db)):
    container = db.query(Container).filter(Container.guid == guid).first()
    if not container:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Container not found")

    if payload.limit < 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Limit must be non-negative")

    container.limit = payload.limit
    db.commit()
    return {"message": f"Container limit updated to {payload.limit}"}

# DELETE container by GUID
@container.delete("/{guid}", status_code=status.HTTP_204_NO_CONTENT, description="Delete a container by GUID")
def delete_container(guid: str, db: Session = Depends(get_db)):
    container = db.query(Container).filter(Container.guid == guid).first()
    if not container:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Container not found")
    db.delete(container)
    db.commit()
    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content={"message": "Container deleted successfully"})
