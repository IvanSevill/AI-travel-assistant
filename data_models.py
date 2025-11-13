# data_models.py

from pydantic import BaseModel, Field
from typing import List, Optional

class Logistics(BaseModel):
    transport_type: str = Field(
        ...,
        description="Kind of transport (e.g., 'By foot', 'Metro L1', 'Taxi', 'Bus')."
    )
    estimated_duration: str = Field(
        ...,
        description="Estimated time, including the waiting time (e.g., '15 min', '45 min', '1h 10min')."
    )
    additional_notes: Optional[str] = Field(
        None,
        description="Short instructions, like 'Buy metro ticket' or 'Use the red metro line'."
    )

class Activity(BaseModel):
    name: str = Field(
        ...,
        description="Name of the place to visit or activity to perform."
    )
    short_description: str = Field(
        ...,
        description="Brief description of the place (maximum 2 sentences)."
    )
    location: str = Field(
        ...,
        description="Address or well-known reference point."
    )
    start_time: str = Field(
        ...,
        description="Activity start time in HH:MM format."
    )
    end_time: str = Field(
        ...,
        description="Activity end time in HH:MM format."
    )
    estimated_cost: str = Field(
        ...,
        description="Approximate cost per person (e.g., '15€', 'Free', '40 USD')."
    )

class Day(BaseModel):
    date: str = Field(
        ...,
        description="Date of the day in YYYY-MM-DD format."
    )
    day_name: str = Field(
        ...,
        description="Descriptive name of the day (e.g., 'Historic Center Exploration', 'Museum Day')."
    )
    activities: List[Activity] = Field(
        ...,
        description="Ordered list of activities planned for this day."
    )
    logistics_between_activities: List[Logistics] = Field(
        ...,
        description="List of logistics to move between Activity[i] and Activity[i+1]."
    )

class TravelItinerary(BaseModel):
    destination: str = Field(
        ...,
        description="Main city or region of the trip."
    )
    total_days: int = Field(
        ...,
        description="Total number of days the itinerary covers."
    )
    main_theme: str = Field(
        ...,
        description="Theme or main focus of the trip (e.g., 'Cultural and Historical', 'Adventure and Nature')."
    )
    daily_itinerary: List[Day] = Field(
        ...,
        description="List of the detailed planning, one 'Day' object for each day of the trip."
    )