import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from unittest.mock import MagicMock, patch
from backend.services.planner_service import generate_full_plan
from backend.models.llm_schemas import ItineraryResponse

# Mock response data
MOCK_LLM_RESPONSE = {
    "status": "ok",
    "itinerary": [
        {
            "day": 1,
            "title": "Arrival in Paris",
            "summary": "Arrive and explore.",
            "schedule": [
                {"period": "Morning", "activity": "Land at CDG", "duration": "2h"},
                {"period": "Afternoon", "activity": "Check in", "duration": "1h"}
            ],
            "cost_estimate": "€50",
            "notes": ["Keep passport handy"]
        }
    ],
    "weather": {"live": False, "summary": "Mock Weather"},
    "flights": {"live": False, "options": []},
    "hotels": {"live": False, "options": []},
    "images": [],
    "logs": ["Test Log"]
}

@patch("backend.services.planner_service.llm_service")
@patch("backend.services.planner_service.get_weather_for_trip")
@patch("backend.services.planner_service.get_flight_options")
@patch("backend.services.planner_service.get_hotel_options")
def test_generate_full_plan_structure(mock_hotels, mock_flights, mock_weather, mock_llm_service):
    # Setup mocks
    mock_weather.return_value = {"live": False, "summary": "Mock Weather"}
    mock_flights.return_value = {"live": False, "options": []}
    mock_hotels.return_value = {"live": False, "options": []}
    
    # Mock LLM service to return the dict directly (as our implementation does)
    mock_llm_service.generate_itinerary.return_value = MOCK_LLM_RESPONSE
    
    trip = {"prompt": "Trip to Paris", "start_date": "2025-05-01", "end_date": "2025-05-05"}
    
    result = generate_full_plan(trip)
    
    assert result["status"] == "ok"
    assert len(result["itinerary"]) == 1
    assert result["itinerary"][0]["title"] == "Arrival in Paris"
    assert "logs" in result
    print("Test passed!")

if __name__ == "__main__":
    # Manually run the test function with mocks
    # We need to manually patch since we aren't using pytest fixtures/decorators in main
    with patch("backend.services.planner_service.llm_service") as mock_llm, \
         patch("backend.services.planner_service.get_weather_for_trip") as mock_weather, \
         patch("backend.services.planner_service.get_flight_options") as mock_flights, \
         patch("backend.services.planner_service.get_hotel_options") as mock_hotels:
         
         test_generate_full_plan_structure(mock_hotels, mock_flights, mock_weather, mock_llm)
