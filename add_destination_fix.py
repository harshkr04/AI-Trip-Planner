# Quick script to add destination to itinerary response
import sys

# Read the file
with open(r'c:\Users\Harsh\Desktop\travel\AI4\backend\routes\itinerary.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the location to insert the code
search_str = '''        response = {
            **plan_result,
            \"flights\": flights_array,
            \"hotels\": hotels_array,
            \"itinerary_id\": record[\"id\"],
            \"conversation\": record[\"conversation\"],
        }
        return response'''

replacement_str = '''        response = {
            **plan_result,
            \"flights\": flights_array,
            \"hotels\": hotels_array,
            \"itinerary_id\": record[\"id\"],
            \"conversation\": record[\"conversation\"],
        }
        
        # Add destination if not already in response (extracted from prompt in planner_service)
        if \"destination\" not in response and \"destination\" in trip:
            response[\"destination\"] = trip[\"destination\"]
        
        return response'''

# Replace
new_content = content.replace(search_str, replacement_str)

# Write back
with open(r'c:\Users\Harsh\Desktop\travel\AI4\backend\routes\itinerary.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Successfully added destination to response!")
