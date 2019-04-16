nations = [
    "Britain",
    "France",
    "Germany",
    "Italy",
    "Japan",
    "Soviet Union",
    "United States",
]

theater_selector_dict = {
    n: ["{} - {}".format(n, i) for i in range(20)] for n in nations
}

theater_selector_dict["Britain"] = [
    "1940 - Fall of France",
    "1940 - Dad's Army",
    "1940-44 - Raiders!",
    "1940-41 - East Africa",
    "1940-41 - Operation Compass",
    "1940-43 - Behind Enemy Lines",
    "1942 - Operation Lightfoot",
    "1942-43 - Tunisia",
    "1942 - Fall of Singapore",
    "1942-45 - Burma",
    "1944 - Monte Cassino",
    "1944 - Normandy",
    "1944 - Market Garden",
    "1945 - Into the Rich",
]

default_list_dict = {
    "lists": {
        "default": {
            "hq": {"major": None, "captain": None, "infantry": None},
            "platoons": [],
            "nationality": "Britain",
            "theater_selector": "1944 - Normandy",
            "initial_cost": 0,
            "logistics_points": 0,
        }
    },
    "session_data": {"current_list": "default"},
}
