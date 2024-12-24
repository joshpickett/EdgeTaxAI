# API Documentation

## Mileage Service

### Overview
The Mileage Service is a shared service that handles all mileage-related functionalities, including calculating mileage, adding mileage records, retrieving mileage history, and managing recurring trips.

### Endpoints
  - **POST** `/mileage`
  - **Request Body**: 
    ```json
    {
      "startLocation": "string",
      "end": "string",
      "purpose": "string",
      "recurring": "boolean"
    }
    ```
  - **Response**: 
    ```json
    {
      "distance": "number",
      "tax_deduction": "number"
    }
    ```

  - **POST** `/mileage/add`
  - **Request Body**: 
    ```json
    {
      "record": {
        "date": "string",
        "distance": "number",
        "purpose": "string"
      }
    }
    ```
  - **Response**: 
    ```json
    {
      "success": "boolean",
      "message": "string"
    }
    ```

  - **GET** `/mileage/history`
  - **Query Parameters**: 
    - `userId`: "string"
  - **Response**: 
    ```json
    [
      {
        "date": "string",
        "distance": "number",
        "purpose": "string"
      }
    ]
    ```

  - **POST** `/mileage/recurring`
  - **Request Body**: 
    ```json
    {
      "tripData": {
        "startLocation": "string",
        "end": "string",
        "purpose": "string",
        "recurring": "boolean"
      }
    }
    ```
  - **Response**: 
    ```json
    {
      "success": "boolean",
      "message": "string"
    }
    ```

### Offline Calculation
In cases where the application is offline, the Mileage Service provides a simplified offline calculation that returns a default message and a tax deduction of zero.

### Integration
The Mileage Service is integrated into both desktop and mobile applications. 

#### Desktop Implementation
The desktop mileage tracker utilizes the shared Mileage Service to handle mileage calculations and history retrieval.

#### Mobile Implementation
The mobile mileage tracking screen imports the Mileage Service and uses it to calculate mileage based on user input.

## Future Enhancements
### Shared Utilities

### Documentation Updates
