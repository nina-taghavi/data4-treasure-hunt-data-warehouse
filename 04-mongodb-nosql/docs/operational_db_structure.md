# CATCHEM Operational Database

This repository contains the schema and documentation for the **CATCHEM** operational database. The database is built on PostgreSQL and serves as the source data system before being processed or migrated to the MongoDB document store.

## Database Schema Overview

The database consists of 7 primary tables designed to manage users, locations, geocaching treasures, their individual stages, and user interaction logs. 

### Entity-Relationship Diagram

Below is the Entity-Relationship (ER) diagram representing the tables, attributes, and their connections.

```mermaid
erDiagram
    COUNTRY {
        string code PK
        string code3
        string name
    }
    
    CITY {
        string city_id PK
        string city_name
        float latitude
        float longitude
        string postal_code
        string country_code FK
    }
    
    USER_TABLE {
        string id PK
        string first_name
        string last_name
        string mail
        string number
        string street
        string city_city_id FK
    }
    
    TREASURE {
        string id PK
        string difficulty
        string terrain
        string city_city_id FK
        string owner_id FK
    }
    
    STAGE {
        string id PK
        string container_size
        string description
        float latitude
        float longitude
        int sequence_number
        string type
        string visibility
    }
    
    TREASURE_STAGES {
        string treasure_id FK
        string stages_id FK
    }
    
    TREASURE_LOG {
        string id PK
        string description
        datetime log_time
        string log_type
        datetime session_start
        string hunter_id FK
        string treasure_id FK
    }

    %% Relationships
    COUNTRY ||--o{ CITY : "contains"
    CITY ||--o{ USER_TABLE : "residence of"
    CITY ||--o{ TREASURE : "location of"
    USER_TABLE ||--o{ TREASURE : "owns"
    TREASURE ||--o{ TREASURE_STAGES : "links to"
    STAGE ||--o{ TREASURE_STAGES : "links from"
    USER_TABLE ||--o{ TREASURE_LOG : "creates (as hunter)"
    TREASURE ||--o{ TREASURE_LOG : "receives"