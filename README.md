# Business Search Tool Backend

The backend for the Business Search Tool, built with [Python](https://www.python.org/) and the [FastAPI](https://fastapi.tiangolo.com/) framework. This backend serves as the API for the frontend to retrieve information about businesses in a specific area of the US.

## API Overview

The backend API performs the following steps to retrieve information about businesses in a specific area:

1. Calls the Google Places textsearch API with a text search string based on frontend queries to get back a list of businesses that have place IDs and a little bit of other information.
2. Filters the list by total number of reviews.
3. Calls the Google Place Details API for each place ID to get the business's website.
4. Returns the list of websites and number of reviews associated with each place to the frontend.

## Getting Started with the Business Search Tool Backend

Follow these steps to get the backend API up and running on your local machine.

### Prerequisites

- [Python 3.6 or later](https://www.python.org/downloads/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Google Places API Key](https://developers.google.com/maps/gmp-get-started#create-project)

### Installation

1. Clone the repository
2. Navigate to the backend directory
3. Install the dependencies: `pip install -r requirements.txt`
4. Set the Google Places API Key as an environment variable: `export API_KEY="your_api_key_here"`
5. Start the development server: `uvicorn main:app --reload`
6. Access the API at `http://localhost:8000/docs`

## Deployment

The backend is hosted on [Google Cloud Run](https://cloud.google.com/run) via a Docker container. Follow the documentation for Google Cloud Run to deploy the backend API. Ensure you have a correctly written Dockerfile in your source directory. ALSO when deploying the container to any cloud service, check the service settings to ensure it is listening on the correct HTTP (10000) to match the container.

## Contributing

This project is open for contributions. Feel free to open an issue or submit a pull request.
