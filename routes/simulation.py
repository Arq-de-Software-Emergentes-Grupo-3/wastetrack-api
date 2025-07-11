from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from config.db import get_db
from models.container import Container
from models.simulation import Simulation
from schemas.simulation import SimulationCreate, SimulationResponse
from utils.routes_openai import call_openai_for_simulation
from dependencies.auth import get_current_user
from models.user import User
from typing import List
import json

simulation = APIRouter(tags=["Simulations"], prefix="/simulation")

@simulation.get("/get-all-simulations", response_model=List[SimulationResponse])
def get_all_simulations(db: Session = Depends(get_db)):
    simulations = db.query(Simulation).order_by(Simulation.created_at.desc()).all()

    # Convertir string JSON de rutas a lista real
    result = []
    for sim in simulations:
        result.append(
            SimulationResponse(
                id=sim.id,
                created_at=sim.created_at,
                total_distance_km=sim.total_distance_km,
                duration_min=sim.duration_min,
                route=json.loads(sim.route),
                distances=sim.distances
            )
        )

    return result

@simulation.post("/generate-simulation", response_model=SimulationResponse, status_code=status.HTTP_201_CREATED)
def generate_simulation(
    payload: SimulationCreate,
    db: Session = Depends(get_db)
):
    # if current_user.role != "worker":
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only workers can generate simulations")

    containers = db.query(Container).filter(Container.guid.in_(payload.container_guids)).all()

    if not containers:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No valid containers found")

    # Generar ruta óptima
    route_guids, distances_json, total_distance_km, duration_min = call_openai_for_simulation(containers)

    # Guardar simulación
    simulation_entry = Simulation(
        total_distance_km=total_distance_km,
        duration_min=duration_min,
        route=json.dumps(route_guids),
        distances=distances_json
    )

    db.add(simulation_entry)
    db.commit()
    db.refresh(simulation_entry)

    return SimulationResponse(
        id=simulation_entry.id,
        created_at=simulation_entry.created_at,
        total_distance_km=simulation_entry.total_distance_km,
        duration_min=simulation_entry.duration_min,
        route=route_guids,
        distances=distances_json
    )
