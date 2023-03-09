# Business Search Tool Backend

The backend for the Business Search Tool, built with [Python](https://www.python.org/) and the [FastAPI](https://fastapi.tiangolo.com/) framework. This backend serves as the API for the frontend to retrieve information about businesses in a specific area of the US.

## API Overview

The backend API performs the following steps to retrieve information about businesses in a specific area:

1. Calls the Google Places textsearch API with a text search string based on frontend queries to get back a list of businesses that have place IDs and a little bit of other information.
2. Filters the list by total number of reviews.
3. Calls the Google Place Details API for each place ID to get the business's website.
4. Returns the list of websites and number of reviews associated with each place to the frontend.

## Deployment

The backend is hosted on [Google Cloud Run](https://cloud.google.com/run). Follow the documentation for Google Cloud Run to deploy the backend API.

## Contributing

This project is open for contributions. Feel free to open an issue or submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
