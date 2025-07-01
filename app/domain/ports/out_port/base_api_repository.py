from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import requests


class IBaseApiRepository(ABC):
    """
    A base interface for repositories that communicate with external APIs.
    """

    def __init__(self, base_url: str):
        self.base_url = base_url
        self.default_headers = {
            'Content-Type': 'application/json'
            # Add any default headers that should be included in every request
        }

    @abstractmethod
    def send_request(
        self,
        method: str,
        endpoint: str,
        headers: Optional[Dict[str, str]] = None,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        Abstract method to send an HTTP request.

        Args:
            method (str): HTTP method (GET, POST, PUT, DELETE).
            endpoint (str): API endpoint to send the request to.
            headers (Dict[str, str], optional): Custom headers to include in the request.
            data (Dict[str, Any], optional): Request payload for POST, PUT, etc.
            params (Dict[str, Any], optional): Query parameters for GET requests.

        Returns:
            Any: The response from the API.
        """
        pass

    @abstractmethod
    def handle_response(self, response: requests.Response) -> Any:
        """
        Abstract method to handle the API response.

        Args:
            response (requests.Response): The response object from the API request.

        Returns:
            Any: Processed response data or error handling.
        """
        pass

    @abstractmethod
    def handle_error(self, error: Exception) -> None:
        """
        Abstract method to handle errors during the API request.

        Args:
            error (Exception): The exception object raised during the request.

        Raises:
            Any custom error or log information.
        """
        pass

 
