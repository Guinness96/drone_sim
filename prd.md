# Product Requirements Document: Autonomous Drone Simulation & Dashboard

**Version:** 1.0
**Date:** October 26, 2023
**Author:** Odhran Islas-Weymes
**Status:** Draft / In Development

## 1. Introduction

This document outlines the requirements for the "Autonomous Drone Simulation & Dashboard" project. The project aims to develop a software-based proof-of-concept (PoC) system that simulates an autonomous drone collecting environmental data, transmits this data to a backend server, stores it, and visualizes it on a secure web-based dashboard. This system will serve as a foundational tool for demonstrating key software engineering principles in simulation, data handling, and web application development, with a focus on environmental monitoring applications.

## 2. Goals & Objectives

### 2.1. Overall Project Goals
*   **G1: Demonstrate End-to-End System Functionality:** Successfully create a working PoC that integrates simulation, data processing, storage, and visualization.
*   **G2: Showcase Core Software Engineering Skills:** Apply and demonstrate proficiency in backend development, frontend development, database management, and basic simulation principles using a popular, modern tech stack.
*   **G3: Provide a Foundation for Future Development:** Create a modular and understandable codebase that could be extended for more advanced features or real-world drone integration in the future.
*   **G4: Explore Environmental Monitoring Concepts:** Simulate a scenario relevant to environmental data collection and provide basic tools for its interpretation.

### 2.2. Specific Project Objectives
*   **O1: Develop a Python-based Drone Simulation:**
    *   Simulate drone flight paths along predefined waypoints.
    *   Generate mock environmental sensor data (e.g., air quality, temperature, humidity) associated with drone locations and timestamps.
*   **O2: Implement a Robust Backend API:**
    *   Create secure API endpoints to receive and store simulated drone and sensor data.
    *   Provide API endpoints to efficiently serve processed/stored data to the web dashboard.
*   **O3: Set Up a Scalable Relational Database:**
    *   Design and implement a database schema in PostgreSQL to effectively store drone flight logs and time-series sensor readings.
*   **O4: Develop an Interactive and Secure Web Dashboard:**
    *   Build a responsive web application (React) for visualizing environmental data and drone activity.
    *   Implement secure user authentication (Auth0) to protect dashboard access.
    *   Display data dynamically using charts (Chart.js) and map-based visualizations (Leaflet.js).
*   **O5: Integrate Basic Analytics/Alerting Placeholder:**
    *   Implement a simple mechanism for identifying and highlighting potential "anomalies" (e.g., rule-based thresholds) in the sensor data for demonstration purposes.

## 3. Target Users & Use Cases

### 3.1. Target Users
*   **U1: Environmental Scientists/Researchers (Simulated):** Users who would want to visualize and get a basic understanding of collected environmental data patterns and drone activity.
*   **U2: System Administrators/Developers (Simulated):** Users who would manage the system, monitor its data flow, and potentially extend its functionality.
*   **U3: Module Assessors:** To evaluate the technical implementation, understanding of concepts, and project management.

### 3.2. Key Use Cases
*   **UC1: Simulate Drone Mission & Data Collection:**
    *   As a system operator (developer running the simulation), I want to run a Python script that simulates a drone flying a mission and generating environmental data, so that this data can be fed into the system.
*   **UC2: Securely Access Monitoring Dashboard:**
    *   As an authorized user, I want to log in securely to the web dashboard, so that I can access the monitoring information.
*   **UC3: View Latest Environmental Data:**
    *   As a dashboard user, I want to see the most recent sensor readings displayed clearly, so that I can get an up-to-date overview.
*   **UC4: Visualize Sensor Data Trends via Charts:**
    *   As a dashboard user, I want to view sensor data (e.g., temperature, humidity) over time on interactive charts, so that I can identify trends.
*   **UC5: Visualize Drone Flight Path & Sensor Locations on a Map:**
    *   As a dashboard user, I want to see the drone's flight path and the locations of sensor readings on an interactive map, so that I can understand the spatial context of the data.
*   **UC6: Identify Potential Data Anomalies:**
    *   As a dashboard user, I want to see a visual indication of sensor readings that exceed predefined thresholds (anomalies), so that I can quickly identify areas or times of interest.
*   **UC7: View Historical Flight and Sensor Data:**
    *   As a dashboard user, I want to be able to select a past flight and view its associated path and sensor data, so that I can review previous missions.

## 4. Functional Requirements

*Refer to the detailed Functional Requirements (FRs) outlined in the technical project plan or task list. Key FRs include:*

*   **FR-SIM-01:** System shall simulate drone movement along a series of waypoints.
*   **FR-SIM-02:** System shall generate mock sensor data (timestamp, location, temperature, humidity, AQI).
*   **FR-API-01:** API shall provide an endpoint to receive and store simulation data.
*   **FR-API-02:** API shall provide endpoints to retrieve flight lists, specific flight data, and latest sensor readings.
*   **FR-DB-01:** Database shall store flight details, drone positions, and sensor readings.
*   **FR-WEB-01:** Web dashboard shall require user authentication for access.
*   **FR-WEB-02:** Dashboard shall display sensor data in tabular format.
*   **FR-WEB-03:** Dashboard shall display sensor data trends using charts.
*   **FR-WEB-04:** Dashboard shall display drone flight paths and sensor locations on an interactive map.
*   **FR-WEB-05:** Dashboard shall visually indicate data points flagged as anomalies.

## 5. Non-Functional Requirements

*   **NFR-PERF-01 (Performance):** Dashboard data displays (tables, initial chart/map load for a flight) should render within 3-5 seconds on a typical broadband connection. (PoC level)
*   **NFR-SEC-01 (Security):** User authentication shall be handled by Auth0, preventing unauthorized access to the dashboard. API endpoints requiring authentication must validate Auth0 tokens.
*   **NFR-USAB-01 (Usability):** The web dashboard shall be intuitive and easy to navigate for viewing data. Key information should be readily accessible.
*   **NFR-MAINT-01 (Maintainability):** Code shall be organized into logical modules (simulation, backend, frontend) with clear separation of concerns. Key functions and components should be reasonably commented. (PoC level)
*   **NFR-REL-01 (Reliability):** The system components (API, DB) should be stable during typical demo scenarios. Data integrity should be maintained. (PoC level)
*   **NFR-SIMACC-01 (Simulation Accuracy):** The simulation is for PoC purposes; flight dynamics will be simplified, and sensor data will be mock data, but should follow plausible patterns and ranges.

## 6. Design & Technical Considerations

*   **Technology Stack:**
    *   **Simulation:** Python
    *   **Backend API:** Python (Flask)
    *   **Database:** PostgreSQL
    *   **Frontend:** React.js
    *   **Charting:** Chart.js
    *   **Mapping:** Leaflet.js
    *   **Authentication:** Auth0
*   **Architecture:** A three-tier architecture (Frontend Client -> Backend API Server -> Database) with a separate Python simulation script feeding data into the API.
*   **Data Flow:** Simulation generates data -> Python script POSTs to Flask API -> Flask API validates & stores in PostgreSQL -> React frontend GETs data from Flask API -> React frontend visualizes data.

## 7. Release Criteria (for PoC Completion / Demo)

*   [ ] All key use cases (UC1-UC6) are demonstrable.
*   [ ] Simulation script successfully generates data and sends it to the backend API.
*   [ ] Backend API correctly stores data in PostgreSQL and serves it to the frontend.
*   [ ] Users can securely log in to the React dashboard via Auth0.
*   [ ] Dashboard correctly displays sensor data in tables, charts, and on a map.
*   [ ] Basic anomaly indication is functional.
*   [ ] Code is committed to GitHub with a clear structure.
*   [ ] Code Manifest and Software Demonstration Video are prepared.

## 8. Future Considerations (Out of Scope for this PoC)

*   Real-time data streaming (WebSockets).
*   More sophisticated drone flight physics in the simulation.
*   Integration of actual machine learning models for anomaly detection/prediction.
*   User-configurable alert notifications.
*   User accounts with different roles/permissions beyond basic authentication.
*   Deployment to a cloud hosting platform.
*   More comprehensive error handling and logging.
*   Automated testing (unit, integration).

## 9. Open Issues / Questions
*   (This section can be used to track any uncertainties or decisions that need to be made during development)
    *   E.g., Final decision on the exact schema for sensor data anomalies.
    *   E.g., Specific refresh rate for "latest data" on the dashboard.

---
This PRD should act as your guiding star. When you're deciding on a feature or how to implement something, refer back to this to ensure it aligns with the defined goals, objectives, and user needs for this specific proof-of-concept.