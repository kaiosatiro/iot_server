import logging
from random import randint
from time import sleep

from sqlalchemy.exc import IntegrityError
from sqlmodel import Session

import src.crud as crud
from src.models import (
    DeviceCreation,
    Message,
    MessageCreation,
    SiteCreation,
    UserCreation,
)
from src.utils import generate_random_number, random_lower_string


def insert_example_data(session: Session) -> None:
    logger = logging.getLogger("Example Data")
    logger.info("Inserting...")
    siteslen = len(SITES)
    deviceslen = len(DEVICES)

    if crud.get_user_by_username(db=session, username=USERS[0]["username"]):
        logger.warning("Example data already exists. Skipping...")
        return

    # One loop for each user
    for user_data in USERS:
        user_in = UserCreation(
            username=user_data["username"],
            email=user_data["email"],
            about=user_data["about"],
            is_active=True,
            is_superuser=False,
            password=random_lower_string(),
        )
        try:
            user = crud.create_user(db=session, user_input=user_in)
        except IntegrityError:
            logger.warning("User %s already exists. Skipping...", user_data["username"])
            continue

        # Random number of sites for each user
        for _ in range(randint(1, 3)):
            random_site = SITES[generate_random_number(0, siteslen - 1)]
            site_in = SiteCreation(
                name=random_site["name"],
                description=random_site["description"],
            )
            site = crud.create_site(db=session, site_input=site_in, owner_id=user.id)

            # Random number of devices for each site
            for _ in range(randint(1, 5)):
                random_device = DEVICES[generate_random_number(0, deviceslen - 1)]
                device_in = DeviceCreation(
                    name=random_device["name"],
                    model=random_device["model"],
                    type=random_device["type"],
                    description=random_device["description"],
                    site_id=site.id,
                    owner_id=user.id,
                )
                device = crud.create_device(db=session, device_input=device_in)

                # Insert example messages
                msg_in_list = []
                for message in MESSAGES.get(device.model):
                    for _ in range(10):
                        m = randint(6, 8)
                        d = randint(1, 30)
                        message_prep = MessageCreation(
                            device_id=device.id, message=message
                        )
                        message_in = Message.model_validate(
                            message_prep,
                            update={"inserted_on": f"2024-{m}-{d}T12:00:00Z"},
                        )
                        msg_in_list.append(message_in)

                session.add_all(msg_in_list)
                session.commit()
        sleep(0.1)


USERS = [
    {
        "username": "techsavvy99",
        "email": "tech_savvy99@example.com",
        "about": "Loves coding and open-source projects.",
    },
    {
        "username": "wanderlust22",
        "email": "wanderlust22@example.com",
        "about": "Passionate traveler and photographer.",
    },
    {
        "username": "gamerace",
        "email": "gamer_ace@example.com",
        "about": "Professional gamer and streamer.",
    },
    {
        "username": "bookwormreader",
        "email": "bookworm_reader@example.com",
        "about": "Avid reader and aspiring writer.",
    },
    {
        "username": "fitfreak",
        "email": "fit_freak@example.com",
        "about": "Fitness enthusiast and nutritionist.",
    },
    {
        "username": "artisti_soul",
        "email": "artistic_soul@example.com",
        "about": "Painter and digital artist.",
    },
    {
        "username": "codemaster",
        "email": "code_master@example.com",
        "about": "Full-stack developer and tech blogger.",
    },
    {
        "username": "musi_maniac",
        "email": "music_maniac@example.com",
        "about": "Music producer and DJ.",
    },
    {
        "username": "naturelover",
        "email": "nature_lover@example.com",
        "about": "Environmentalist and hiker.",
    },
    {
        "username": "chefdelight",
        "email": "chef_delight@example.com",
        "about": "Gourmet chef and food critic.",
    },
    {
        "username": "moviebuff",
        "email": "movie_buff@example.com",
        "about": "Film enthusiast and critic.",
    },
    {
        "username": "sciencegeek",
        "email": "science_geek@example.com",
        "about": "Astrophysics student and researcher.",
    },
    {
        "username": "designguru",
        "email": "design_guru@example.com",
        "about": "UI/UX designer with a passion for minimalism.",
    },
    {
        "username": "historybuff",
        "email": "history_buff@example.com",
        "about": "History teacher and museum curator.",
    },
    {
        "username": "yogawarrior",
        "email": "yoga_warrior@example.com",
        "about": "Certified yoga instructor and wellness coach.",
    },
    {
        "username": "animallover",
        "email": "animal_lover@example.com",
        "about": "Veterinarian and animal rights activist.",
    },
    {
        "username": "fashionista",
        "email": "fashionista@example.com",
        "about": "Fashion designer and stylist.",
    },
    {
        "username": "techwizard",
        "email": "tech_wizard@example.com",
        "about": "IT consultant and cybersecurity expert.",
    },
    {
        "username": "coffeeaddict",
        "email": "coffee_addict@example.com",
        "about": "Barista and coffee aficionado.",
    },
    {
        "username": "startupguru",
        "email": "startup_guru@example.com",
        "about": "Entrepreneur and venture capitalist.",
    },
    {
        "username": "bikerlife",
        "email": "biker_life@example.com",
        "about": "Motorcycle enthusiast and adventure seeker.",
    },
    {
        "username": "languagelearner",
        "email": "language_learner@example.com",
        "about": "Polyglot and language teacher.",
    },
    {
        "username": "photogpro",
        "email": "photog_pro@example.com",
        "about": "Professional photographer and photojournalist.",
    },
    {
        "username": "diycrafter",
        "email": "diy_crafter@example.com",
        "about": "DIY enthusiast and craftsperson.",
    },
    {
        "username": "fitnessfanatic",
        "email": "fitness_fanatic@example.com",
        "about": "Personal trainer and fitness coach.",
    },
    {
        "username": "traveljunkie",
        "email": "travel_junkie@example.com",
        "about": "Travel blogger and digital nomad.",
    },
    {
        "username": "ecowarrior",
        "email": "eco_warrior@example.com",
        "about": "Sustainability advocate and eco-friendly blogger.",
    },
    {
        "username": "codingninja",
        "email": "coding_ninja@example.com",
        "about": "Software engineer and coding mentor.",
    },
    {
        "username": "urbanexplorer",
        "email": "urban_explorer@example.com",
        "about": "Urban photographer and blogger.",
    },
    {
        "username": "sciencefan",
        "email": "science_fan@example.com",
        "about": "Biologist and science communicator.",
    },
]

SITES = [
    {
        "name": "Greenhouse",
        "description": "A controlled environment used for growing plants, \
            monitored for temperature and humidity to ensure optimal growing conditions.",
    },
    {
        "name": "Cold Storage Room",
        "description": "A refrigerated area used to store perishable goods, \
            monitored for consistent low temperatures and humidity to prevent spoilage.",
    },
    {
        "name": "Server Room",
        "description": "A room housing computer servers, closely monitored for \
            temperature and humidity to prevent overheating and equipment failure.",
    },
    {
        "name": "Warehouse",
        "description": "A large storage facility, often monitored for temperature, \
            humidity, and movement to protect stored goods and track inventory.",
    },
    {
        "name": "Laboratory",
        "description": "A controlled environment for scientific research, \
            monitored for temperature, humidity, and air quality to maintain precise experimental conditions.",
    },
    {
        "name": "Wine Cellar",
        "description": "A specialized storage room for wine, \
            monitored for temperature and humidity to preserve the quality of the wine.",
    },
    {
        "name": "Aquarium",
        "description": "A large tank or room for aquatic animals, \
            monitored for water temperature, pH levels, and salinity to ensure a healthy environment.",
    },
    {
        "name": "Museum Exhibit Room",
        "description": "A room displaying valuable artifacts, \
            monitored for temperature, humidity, and light exposure to protect delicate items.",
    },
    {
        "name": "Data Center",
        "description": "A facility used to house computer systems, \
            monitored for temperature, humidity, and airflow to ensure operational efficiency and prevent equipment failure.",
    },
    {
        "name": "Pharmaceutical Storage",
        "description": "A room or facility where medications are stored, \
            monitored for temperature and humidity to maintain the efficacy of the drugs.",
    },
    {
        "name": "Archive Room",
        "description": "A room used to store important documents, \
            often monitored for temperature, humidity, and light to preserve paper and other materials.",
    },
    {
        "name": "Green Data Center",
        "description": "A data center focused on sustainability, \
            monitored for temperature, humidity, and energy usage to maintain efficiency and reduce environmental impact.",
    },
    {
        "name": "Hospital Operating Room",
        "description": "A sterile environment in a hospital, \
            monitored for temperature, humidity, and air quality to ensure patient safety during surgeries.",
    },
    {
        "name": "Server Cabinet",
        "description": "An enclosed space for servers within a larger room, \
            monitored for temperature and airflow to prevent overheating.",
    },
    {
        "name": "Climate-Controlled Storage",
        "description": "A storage facility with controlled temperature and humidity, \
            used to store sensitive items like electronics, art, and documents.",
    },
    {
        "name": "Residential Attic",
        "description": "The uppermost space in a home, \
            monitored for temperature and humidity to prevent heat buildup and moisture damage.",
    },
    {
        "name": "Food Processing Plant",
        "description": "A facility where food is processed, monitored for temperature, \
            humidity, and cleanliness to ensure product safety and quality.",
    },
    {
        "name": "Indoor Sports Facility",
        "description": "An enclosed area for sports activities, \
            monitored for temperature and air quality to maintain a comfortable environment for athletes.",
    },
    {
        "name": "Indoor Pool Area",
        "description": "An enclosed swimming pool, monitored for temperature, \
            humidity, and air circulation to ensure comfort and safety.",
    },
    {
        "name": "Brewery",
        "description": "A facility where beer is produced, monitored for temperature and \
            humidity to control the fermentation process and maintain product quality.",
    },
    {
        "name": "Art Gallery",
        "description": "A room or building where art is displayed, monitored for temperature, \
            humidity, and light exposure to preserve the artworks.",
    },
    {
        "name": "Hospital Ward",
        "description": "A patient care area in a hospital, monitored for temperature, \
            air quality, and hygiene to ensure a safe and comfortable environment.",
    },
    {
        "name": "Yacht Interior",
        "description": "The interior of a luxury boat, monitored for temperature, \
            humidity, and movement to ensure comfort and safety at sea.",
    },
    {
        "name": "Library Rare Book Room",
        "description": "A special section in a library for rare and valuable books, \
            monitored for temperature, humidity, and light exposure to prevent deterioration.",
    },
    {
        "name": "Indoor Farming Facility",
        "description": "A facility used for growing crops indoors, \
            monitored for temperature, humidity, and light to optimize plant growth.",
    },
    {
        "name": "Residential Wine Room",
        "description": "A dedicated space in a home for wine storage, \
            monitored for temperature and humidity to preserve the quality of the wine.",
    },
    {
        "name": "Fish Hatchery",
        "description": "A facility for breeding and raising fish, \
            monitored for water temperature, oxygen levels, and cleanliness to ensure a healthy environment.",
    },
    {
        "name": "Laboratory Clean Room",
        "description": "A highly controlled environment in a lab, \
            monitored for air quality, temperature, and humidity to minimize contamination.",
    },
    {
        "name": "Residential Basement",
        "description": "The lower level of a home, monitored for temperature, \
            humidity, and potential water intrusion to prevent mold and structural damage.",
    },
    {
        "name": "Cold Room",
        "description": "A space designed to maintain low temperatures for storage, \
            monitored for consistent cooling and humidity to preserve items.",
    },
]

DEVICES = [
    {
        "name": "ThermoGuard",
        "model": "TG-500",
        "type": "Temperature Sensor",
        "description": "Accurate temperature monitoring for environments like cold storage rooms and server rooms.",
    },
    {
        "name": "HumidiCheck",
        "model": "HC-200",
        "type": "Humidity Sensor",
        "description": "Maintains optimal humidity levels in greenhouses and wine cellars.",
    },
    {
        "name": "MotionEye",
        "model": "ME-300",
        "type": "Motion Sensor",
        "description": "Detects movement in warehouses and archive rooms, enhancing security.",
    },
    {
        "name": "AirMonitor Pro",
        "model": "AM-400",
        "type": "Air Quality Sensor",
        "description": "Monitors air quality in laboratories and hospital operating rooms to ensure a safe environment.",
    },
    {
        "name": "AquaSense",
        "model": "AS-150",
        "type": "Water Quality Sensor",
        "description": "Monitors water conditions in aquariums and fish hatcheries for optimal aquatic health.",
    },
    {
        "name": "LightGuard",
        "model": "LG-100",
        "type": "Light Sensor",
        "description": "Controls light exposure in art galleries and museum exhibit rooms to protect delicate items.",
    },
    {
        "name": "SmartVent",
        "model": "SV-250",
        "type": "Ventilation Control",
        "description": "Regulates airflow and ventilation in indoor sports facilities and server rooms.",
    },
    {
        "name": "ColdChainMonitor",
        "model": "CCM-350",
        "type": "Temperature and Humidity Sensor",
        "description": "Ensures consistent temperature and humidity in pharmaceutical storage and cold storage rooms.",
    },
    {
        "name": "PlantPulse",
        "model": "PP-600",
        "type": "Soil Moisture Sensor",
        "description": "Monitors soil moisture levels in greenhouses and indoor farming facilities to optimize plant growth.",
    },
    {
        "name": "HeatShield",
        "model": "HS-120",
        "type": "Thermal Camera",
        "description": "Detects heat anomalies in server rooms and electrical panels to prevent overheating.",
    },
    {
        "name": "AquaFlow",
        "model": "AF-220",
        "type": "Water Flow Sensor",
        "description": "Monitors water flow in indoor pool areas and fish hatcheries to maintain optimal conditions.",
    },
    {
        "name": "EnviroGuard",
        "model": "EG-900",
        "type": "Environmental Sensor",
        "description": "Comprehensive environmental monitoring for warehouses and cold rooms, including temperature, humidity, and air quality.",
    },
    {
        "name": "VibrationAlert",
        "model": "VA-500",
        "type": "Vibration Sensor",
        "description": "Monitors vibrations in sensitive areas like server cabinets and laboratory equipment to prevent damage.",
    },
    {
        "name": "SecureCam",
        "model": "SC-700",
        "type": "Security Camera",
        "description": "High-definition security monitoring for parking lots, hallways, and driveways.",
    },
    {
        "name": "CO2Tracker",
        "model": "COT-110",
        "type": "Carbon Dioxide Sensor",
        "description": "Monitors CO2 levels in greenhouses and indoor farming facilities to ensure optimal plant growth.",
    },
    {
        "name": "LeakDetect",
        "model": "LD-300",
        "type": "Water Leak Sensor",
        "description": "Detects water leaks in residential basements and server rooms to prevent water damage.",
    },
    {
        "name": "PressureCheck",
        "model": "PC-210",
        "type": "Pressure Sensor",
        "description": "Monitors pressure in HVAC systems within climate-controlled storage and data centers.",
    },
    {
        "name": "WindGuard",
        "model": "WG-400",
        "type": "Wind Sensor",
        "description": "Monitors wind speed and direction on rooftops and outdoor facilities.",
    },
    {
        "name": "SoundSense",
        "model": "SS-100",
        "type": "Noise Sensor",
        "description": "Measures noise levels in hospital wards and indoor sports facilities to maintain a comfortable environment.",
    },
    {
        "name": "SmokeAlert",
        "model": "SA-250",
        "type": "Smoke Detector",
        "description": "Detects smoke in laboratories and server rooms, triggering early warnings to prevent fire damage.",
    },
    {
        "name": "SmartThermostat",
        "model": "ST-600",
        "type": "Smart Thermostat",
        "description": "Automates temperature control in residential attics and conference rooms for energy efficiency.",
    },
    {
        "name": "EnergyMonitor",
        "model": "EM-450",
        "type": "Energy Consumption Sensor",
        "description": "Tracks energy usage in data centers and laboratories, optimizing energy efficiency.",
    },
    {
        "name": "BioSense",
        "model": "BS-300",
        "type": "Biometric Sensor",
        "description": "Monitors biometric data in hospital operating rooms and fitness centers to ensure patient and athlete safety.",
    },
    {
        "name": "UVGuard",
        "model": "UVG-120",
        "type": "UV Sensor",
        "description": "Monitors UV radiation in greenhouses and laboratories to protect plants and sensitive materials.",
    },
    {
        "name": "OzoneTracker",
        "model": "OT-400",
        "type": "Ozone Sensor",
        "description": "Measures ozone levels in pharmaceutical storage and clean rooms to maintain air quality.",
    },
    {
        "name": "HumidityControl",
        "model": "HC-150",
        "type": "Humidity Controller",
        "description": "Regulates humidity in archive rooms and cold storage rooms to prevent damage to sensitive items.",
    },
    {
        "name": "GasAlert",
        "model": "GA-500",
        "type": "Gas Leak Sensor",
        "description": "Detects gas leaks in laboratories and cold rooms, ensuring safety and compliance.",
    },
    {
        "name": "AquaTemp",
        "model": "AT-200",
        "type": "Water Temperature Sensor",
        "description": "Monitors water temperature in swimming pools and fish hatcheries to maintain optimal conditions.",
    },
    {
        "name": "SmartMeter",
        "model": "SM-320",
        "type": "Smart Energy Meter",
        "description": "Tracks and reports energy usage in residential homes and smart buildings for efficiency.",
    },
    {
        "name": "OccupancySensor",
        "model": "OS-230",
        "type": "Occupancy Sensor",
        "description": "Detects occupancy in conference rooms and laboratories to optimize lighting and HVAC usage.",
    },
]


MESSAGES = {
    "TG-500": [
        {"timestamp": "2024-08-30T12:00:00Z", "temperature": 21.5, "unit": "C"},
        {"timestamp": "2024-08-30T13:00:00Z", "temperature": 22.0, "unit": "C"},
        {"timestamp": "2024-08-30T14:00:00Z", "temperature": 21.8, "unit": "C"},
    ],
    "HC-200": [
        {"timestamp": "2024-08-30T12:00:00Z", "humidity": 55.2, "unit": "%"},
        {"timestamp": "2024-08-30T13:00:00Z", "humidity": 54.8, "unit": "%"},
        {"timestamp": "2024-08-30T14:00:00Z", "humidity": 55.5, "unit": "%"},
    ],
    "ME-300": [
        {
            "timestamp": "2024-08-30T12:00:00Z",
            "movement_detected": True,
            "zone": "Warehouse A",
        },
        {
            "timestamp": "2024-08-30T13:00:00Z",
            "movement_detected": False,
            "zone": "Warehouse A",
        },
        {
            "timestamp": "2024-08-30T14:00:00Z",
            "movement_detected": True,
            "zone": "Warehouse B",
        },
    ],
    "AM-400": [
        {"timestamp": "2024-08-30T12:00:00Z", "air_quality_index": 42, "unit": "AQI"},
        {"timestamp": "2024-08-30T13:00:00Z", "air_quality_index": 39, "unit": "AQI"},
        {"timestamp": "2024-08-30T14:00:00Z", "air_quality_index": 45, "unit": "AQI"},
    ],
    "AS-150": [
        {
            "timestamp": "2024-08-30T12:00:00Z",
            "ph": 7.2,
            "temperature": 26.5,
            "unit": "C",
        },
        {
            "timestamp": "2024-08-30T13:00:00Z",
            "ph": 7.1,
            "temperature": 26.7,
            "unit": "C",
        },
        {
            "timestamp": "2024-08-30T14:00:00Z",
            "ph": 7.3,
            "temperature": 26.4,
            "unit": "C",
        },
    ],
    "LG-100": [
        {"timestamp": "2024-08-30T12:00:00Z", "light_level": 300, "unit": "lux"},
        {"timestamp": "2024-08-30T13:00:00Z", "light_level": 350, "unit": "lux"},
        {"timestamp": "2024-08-30T14:00:00Z", "light_level": 320, "unit": "lux"},
    ],
    "SV-250": [
        {
            "timestamp": "2024-08-30T12:00:00Z",
            "ventilation_status": "on",
            "airflow_rate": 120,
            "unit": "CFM",
        },
        {
            "timestamp": "2024-08-30T13:00:00Z",
            "ventilation_status": "on",
            "airflow_rate": 115,
            "unit": "CFM",
        },
        {
            "timestamp": "2024-08-30T14:00:00Z",
            "ventilation_status": "off",
            "airflow_rate": 0,
            "unit": "CFM",
        },
    ],
    "CCM-350": [
        {
            "timestamp": "2024-08-30T12:00:00Z",
            "temperature": 3.5,
            "humidity": 65.0,
            "unit": "C/%",
        },
        {
            "timestamp": "2024-08-30T13:00:00Z",
            "temperature": 3.7,
            "humidity": 64.5,
            "unit": "C/%",
        },
        {
            "timestamp": "2024-08-30T14:00:00Z",
            "temperature": 3.6,
            "humidity": 65.2,
            "unit": "C/%",
        },
    ],
    "PP-600": [
        {"timestamp": "2024-08-30T12:00:00Z", "soil_moisture": 45.2, "unit": "%"},
        {"timestamp": "2024-08-30T13:00:00Z", "soil_moisture": 44.8, "unit": "%"},
        {"timestamp": "2024-08-30T14:00:00Z", "soil_moisture": 45.5, "unit": "%"},
    ],
    "HS-120": [
        {
            "timestamp": "2024-08-30T12:00:00Z",
            "temperature": 40.5,
            "hotspot_detected": False,
            "unit": "C",
        },
        {
            "timestamp": "2024-08-30T13:00:00Z",
            "temperature": 42.3,
            "hotspot_detected": True,
            "unit": "C",
        },
        {
            "timestamp": "2024-08-30T14:00:00Z",
            "temperature": 41.0,
            "hotspot_detected": False,
            "unit": "C",
        },
    ],
    "AF-220": [
        {"timestamp": "2024-08-30T12:00:00Z", "water_flow_rate": 15.5, "unit": "L/min"},
        {"timestamp": "2024-08-30T13:00:00Z", "water_flow_rate": 15.0, "unit": "L/min"},
        {"timestamp": "2024-08-30T14:00:00Z", "water_flow_rate": 16.2, "unit": "L/min"},
    ],
    "EG-900": [
        {
            "timestamp": "2024-08-30T12:00:00Z",
            "temperature": 22.5,
            "humidity": 55.0,
            "air_quality_index": 40,
            "unit": "C/%/AQI",
        },
        {
            "timestamp": "2024-08-30T13:00:00Z",
            "temperature": 22.8,
            "humidity": 54.5,
            "air_quality_index": 38,
            "unit": "C/%/AQI",
        },
        {
            "timestamp": "2024-08-30T14:00:00Z",
            "temperature": 22.7,
            "humidity": 55.2,
            "air_quality_index": 42,
            "unit": "C/%/AQI",
        },
    ],
    "VA-500": [
        {"timestamp": "2024-08-30T12:00:00Z", "vibration_level": 2.5, "unit": "mm/s"},
        {"timestamp": "2024-08-30T13:00:00Z", "vibration_level": 2.7, "unit": "mm/s"},
        {"timestamp": "2024-08-30T14:00:00Z", "vibration_level": 2.6, "unit": "mm/s"},
    ],
    "SC-700": [
        {
            "timestamp": "2024-08-30T12:00:00Z",
            "image_url": "https://example.com/image1.jpg",
            "movement_detected": False,
        },
        {
            "timestamp": "2024-08-30T13:00:00Z",
            "image_url": "https://example.com/image2.jpg",
            "movement_detected": True,
        },
        {
            "timestamp": "2024-08-30T14:00:00Z",
            "image_url": "https://example.com/image3.jpg",
            "movement_detected": False,
        },
    ],
    "COT-110": [
        {"timestamp": "2024-08-30T12:00:00Z", "co2_level": 415, "unit": "ppm"},
        {"timestamp": "2024-08-30T13:00:00Z", "co2_level": 420, "unit": "ppm"},
        {"timestamp": "2024-08-30T14:00:00Z", "co2_level": 417, "unit": "ppm"},
    ],
    "LD-300": [
        {
            "timestamp": "2024-08-30T12:00:00Z",
            "water_leak_detected": False,
            "location": "Basement",
        },
        {
            "timestamp": "2024-08-30T13:00:00Z",
            "water_leak_detected": False,
            "location": "Basement",
        },
        {
            "timestamp": "2024-08-30T14:00:00Z",
            "water_leak_detected": True,
            "location": "Basement",
        },
    ],
    "PC-210": [
        {"timestamp": "2024-08-30T12:00:00Z", "pressure": 101.5, "unit": "kPa"},
        {"timestamp": "2024-08-30T13:00:00Z", "pressure": 101.7, "unit": "kPa"},
        {"timestamp": "2024-08-30T14:00:00Z", "pressure": 101.6, "unit": "kPa"},
    ],
    "WG-400": [
        {
            "timestamp": "2024-08-30T12:00:00Z",
            "wind_speed": 12.5,
            "wind_direction": "NW",
            "unit": "km/h",
        },
        {
            "timestamp": "2024-08-30T13:00:00Z",
            "wind_speed": 11.8,
            "wind_direction": "N",
            "unit": "km/h",
        },
        {
            "timestamp": "2024-08-30T14:00:00Z",
            "wind_speed": 13.2,
            "wind_direction": "NE",
            "unit": "km/h",
        },
    ],
    "SS-100": [
        {"timestamp": "2024-08-30T12:00:00Z", "noise_level": 45.5, "unit": "dB"},
        {"timestamp": "2024-08-30T13:00:00Z", "noise_level": 44.8, "unit": "dB"},
        {"timestamp": "2024-08-30T14:00:00Z", "noise_level": 46.2, "unit": "dB"},
    ],
    "SA-250": [
        {"timestamp": "2024-08-30T12:00:00Z", "smoke_detected": False},
        {"timestamp": "2024-08-30T13:00:00Z", "smoke_detected": False},
        {"timestamp": "2024-08-30T14:00:00Z", "smoke_detected": True},
    ],
    "ST-600": [
        {
            "timestamp": "2024-08-30T12:00:00Z",
            "temperature_setpoint": 22.5,
            "current_temperature": 22.0,
            "unit": "C",
        },
        {
            "timestamp": "2024-08-30T13:00:00Z",
            "temperature_setpoint": 22.5,
            "current_temperature": 22.2,
            "unit": "C",
        },
        {
            "timestamp": "2024-08-30T14:00:00Z",
            "temperature_setpoint": 22.5,
            "current_temperature": 22.1,
            "unit": "C",
        },
    ],
    "EM-450": [
        {"timestamp": "2024-08-30T12:00:00Z", "energy_usage": 1500, "unit": "Wh"},
        {"timestamp": "2024-08-30T13:00:00Z", "energy_usage": 1450, "unit": "Wh"},
        {"timestamp": "2024-08-30T14:00:00Z", "energy_usage": 1520, "unit": "Wh"},
    ],
    "BS-300": [
        {
            "timestamp": "2024-08-30T12:00:00Z",
            "heart_rate": 75,
            "body_temperature": 36.5,
            "unit": "bpm/C",
        },
        {
            "timestamp": "2024-08-30T13:00:00Z",
            "heart_rate": 78,
            "body_temperature": 36.7,
            "unit": "bpm/C",
        },
        {
            "timestamp": "2024-08-30T14:00:00Z",
            "heart_rate": 76,
            "body_temperature": 36.6,
            "unit": "bpm/C",
        },
    ],
    "UVG-120": [
        {"timestamp": "2024-08-30T12:00:00Z", "uv_index": 5, "unit": ""},
        {"timestamp": "2024-08-30T13:00:00Z", "uv_index": 6, "unit": ""},
        {"timestamp": "2024-08-30T14:00:00Z", "uv_index": 5, "unit": ""},
    ],
    "OT-400": [
        {"timestamp": "2024-08-30T12:00:00Z", "ozone_level": 0.03, "unit": "ppm"},
        {"timestamp": "2024-08-30T13:00:00Z", "ozone_level": 0.04, "unit": "ppm"},
        {"timestamp": "2024-08-30T14:00:00Z", "ozone_level": 0.03, "unit": "ppm"},
    ],
    "HC-150": [
        {
            "timestamp": "2024-08-30T12:00:00Z",
            "humidity_setpoint": 50.0,
            "current_humidity": 48.5,
            "unit": "%",
        },
        {
            "timestamp": "2024-08-30T13:00:00Z",
            "humidity_setpoint": 50.0,
            "current_humidity": 49.0,
            "unit": "%",
        },
        {
            "timestamp": "2024-08-30T14:00:00Z",
            "humidity_setpoint": 50.0,
            "current_humidity": 48.8,
            "unit": "%",
        },
    ],
    "GA-500": [
        {
            "timestamp": "2024-08-30T12:00:00Z",
            "gas_leak_detected": False,
            "gas_type": "Methane",
        },
        {
            "timestamp": "2024-08-30T13:00:00Z",
            "gas_leak_detected": True,
            "gas_type": "Methane",
        },
        {
            "timestamp": "2024-08-30T14:00:00Z",
            "gas_leak_detected": False,
            "gas_type": "Methane",
        },
    ],
    "AT-200": [
        {"timestamp": "2024-08-30T12:00:00Z", "water_temperature": 28.0, "unit": "C"},
        {"timestamp": "2024-08-30T13:00:00Z", "water_temperature": 27.8, "unit": "C"},
        {"timestamp": "2024-08-30T14:00:00Z", "water_temperature": 28.2, "unit": "C"},
    ],
    "SM-320": [
        {"timestamp": "2024-08-30T12:00:00Z", "energy_consumed": 2500, "unit": "Wh"},
        {"timestamp": "2024-08-30T13:00:00Z", "energy_consumed": 2450, "unit": "Wh"},
        {"timestamp": "2024-08-30T14:00:00Z", "energy_consumed": 2520, "unit": "Wh"},
    ],
    "OS-230": [
        {
            "timestamp": "2024-08-30T12:00:00Z",
            "occupancy_status": "occupied",
            "people_count": 5,
        },
        {
            "timestamp": "2024-08-30T13:00:00Z",
            "occupancy_status": "vacant",
            "people_count": 0,
        },
        {
            "timestamp": "2024-08-30T14:00:00Z",
            "occupancy_status": "occupied",
            "people_count": 3,
        },
    ],
}
