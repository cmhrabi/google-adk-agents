import requests


def get_current_time(timezone: str = "America/Toronto") -> dict:
    """
    Fetches current time information for a specified timezone.
    
    Args:
        timezone (str): The timezone to query (e.g., "America/Toronto", "Europe/London", "Asia/Tokyo").
                       Defaults to "America/Toronto".
    
    Returns:
        dict: A dictionary containing time information including:
            - datetime: Current datetime in the specified timezone
            - timezone: The queried timezone
            - utc_offset: UTC offset for the timezone
            - day_of_week: Day of week (0=Sunday, 6=Saturday)
            - day_of_year: Day number in the year
            - unixtime: Unix timestamp
            - dst: Whether daylight saving time is active
            - abbreviation: Timezone abbreviation
            
    Raises:
        requests.RequestException: If the API request fails
        ValueError: If the timezone is invalid
    """
    base_url = "http://worldtimeapi.org/api/timezone"
    url = f"{base_url}/{timezone}"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    
    except requests.HTTPError as e:
        if response.status_code == 404:
            raise ValueError(f"Invalid timezone: {timezone}. Please check the timezone format.")
        else:
            raise requests.RequestException(f"API request failed with status {response.status_code}: {e}")
    
    except requests.RequestException as e:
        raise requests.RequestException(f"Failed to fetch time data: {e}")