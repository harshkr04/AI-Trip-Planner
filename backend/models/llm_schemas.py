from pydantic import BaseModel, Field
from typing import List, Optional, Literal

class ItinerarySegment(BaseModel):
    period: str = Field(..., description="Time of day (e.g., Morning, Afternoon, Evening)")
    activity: str = Field(..., description="Description of the activity")
    duration: Optional[str] = Field(None, description="Estimated duration")
    travel_time: Optional[str] = Field(None, description="Travel time to this location")
    booking_link: Optional[str] = Field(None, description="Link or instruction to book")
    cost_estimate: Optional[str] = Field(None, description="Estimated cost for this activity")

class ItineraryDay(BaseModel):
    day: int
    title: str = Field(..., description="Theme or title for the day")
    summary: str = Field(..., description="Short summary of the day")
    schedule: List[ItinerarySegment]
    cost_estimate: str = Field(..., description="Total estimated cost for the day")
    notes: List[str] = Field(default_factory=list, description="Accessibility, safety, or other notes")

class WeatherData(BaseModel):
    live: bool
    summary: Optional[str] = None
    days: Optional[List[dict]] = None
    placeholder_reason: Optional[str] = None

class FlightOption(BaseModel):
    airline: str
    flight_number: Optional[str] = None
    departure: str
    arrival: str
    price: str
    duration: str
    link: Optional[str] = None

class FlightsData(BaseModel):
    live: bool
    options: List[FlightOption] = Field(default_factory=list)
    fallback_reason: Optional[str] = None

class HotelOption(BaseModel):
    name: str
    rating: str
    price: str
    description: str
    pros: List[str] = Field(default_factory=list)
    cons: List[str] = Field(default_factory=list)
    link: Optional[str] = None

class HotelsData(BaseModel):
    live: bool
    options: List[HotelOption] = Field(default_factory=list)
    fallback_reason: Optional[str] = None

class ImageData(BaseModel):
    destination: str
    url: str

class ItineraryResponse(BaseModel):
    status: Literal["ok", "error"]
    itinerary: List[ItineraryDay]
    weather: WeatherData
    flights: FlightsData
    hotels: HotelsData
    images: List[ImageData] = Field(default_factory=list)
    logs: List[str] = Field(default_factory=list)
