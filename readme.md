# PLAN: Philippine Library Accessibility Navigator

## Library Spatial Accessibility Assessment Tool
Developed by [lhernandez0](https://github.com/lhernandez0)


## Table of contents
1. Project description
2. Who this project is for
3. Project dependencies
4. Instructions for using PLAN
   - Install PLAN
   - Configure PLAN
   - Run PLAN
   - Troubleshoot PLAN
5. Contributing guidelines
6. Additional documentation
7. How to get help
8. Terms of use


## Project description
With the **Philippine Library Accessibility Navigator (PLAN)**, you can analyze the accessibility of library services across various barangays in the Philippines using the Enhanced Two-Step Floating Catchment Area (E2SFCA) method.

**Key Features:**

- **Identify Accessibility Gaps:** Helps you identify areas with low library accessibility and potential gaps in library services.
  
- **Easy-to-Use Web App:**
  - Made with Streamlit, PLAN offers a streamlined, web-based interface for spatial accessibility analysis.
  - Eliminates the need for extensive GIS expertise.

- **User-Friendly Interface:**
  - Enables quick and interactive web application development.
  - Allows users to easily navigate the tool, upload data, adjust parameters, and visualize results.
  - Does not require the installation of complex GIS software.



## Who this project is for
This project is intended for librarians and administrators who need to analyze the accessibility of library services of their libraries.


## Project dependencies
PLAN is available for demo here:

For development of PLAN, ensure you have:
* Python 3.8+
* Docker
* Make

PLAN is built and tested on a WSL2 Ubuntu 20.04 machine.


## Instructions for using PLAN
Get started with **PLAN** by following these steps:


### Install PLAN
1. Clone the repository:
    ```sh
    git clone https://github.com/OpenLISPh/PLAN.git
    cd PLAN
    ```

2. Create and activate a virtual environment, and install the required Python packages using Make:
 
    ```sh
    make venv
    make dev
    ```

3. Start the PostgreSQL server with Docker:
    ```sh
    make db
    ```


### Configure PLAN
1. Obtain a Google Maps API key from the Google Cloud Platform.
2. Copy `.env.example` to `.env` and fill in the values.
    ```sh
    cp env.example .env
    ```


### Run PLAN
1. Launch the admin application by running `make admin`
2. Launch the user page by running `make run`


## Contributing guidelines
Contributions will be opened in the near future.


## Additional documentation
In-progress. Please be patient.

## How to get help
Check GitHub issues for help. Additional means will be available soon.

## Terms of use
Philippine Library Accessibility Navigator (PLAN) is licensed under the [MIT License](https://github.com/OpenLISPh/PLAN/blob/main/LICENSE).
