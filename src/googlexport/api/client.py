
from google.oauth2.service_account import Credentials
from googlexport.api.scopes import GoogleScope
from typing import List
import apiclient.discovery

class GoogleServiceClient:
    def __init__(self, credsFile: str, scopes: List[GoogleScope] = []):
        if not isinstance(credsFile, str):
            raise ValueError("credsFile must be a string")
        
        if not isinstance(scopes, list):
            raise ValueError("scopes must be a list")
        
        for scope in scopes:
            if not isinstance(scope, GoogleScope):
                raise ValueError("scopes must be a list of GoogleScope")
        
        self._creds = Credentials.from_service_account_file(credsFile, scopes=[scope.value for scope in scopes])

    def GetService(self, serviceName: str, version: str):
        if not isinstance(serviceName, str):
            raise ValueError("serviceName must be a string")
        
        if not isinstance(version, str):
            raise ValueError("version must be a string")
        
        return apiclient.discovery.build(serviceName, version, credentials=self._creds)
        