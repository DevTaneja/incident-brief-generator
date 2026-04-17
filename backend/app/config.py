"""Configuration management for the application."""

import os
from typing import Dict, Optional
from pydantic_settings import BaseSettings
from pydantic import Field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class EnvironmentConfig(BaseSettings):
    """Environment-specific configuration."""
    
    # Application settings
    app_name: str = Field(default="Incident Brief Generator", env="APP_NAME")
    app_env: str = Field(default="development", env="APP_ENV")
    app_debug: bool = Field(default=True, env="APP_DEBUG")
    app_host: str = Field(default="0.0.0.0", env="APP_HOST")
    app_port: int = Field(default=8000, env="APP_PORT")
    
    # New Relic settings
    new_relic_api_key: Optional[str] = Field(default=None, env="NEW_RELIC_API_KEY")
    new_relic_account_id: Optional[str] = Field(default=None, env="NEW_RELIC_ACCOUNT_ID")
    
    # Splunk settings
    splunk_api_token: Optional[str] = Field(default=None, env="SPLUNK_API_TOKEN")
    splunk_host: str = Field(default="localhost", env="SPLUNK_HOST")
    splunk_port: int = Field(default=8089, env="SPLUNK_PORT")
    splunk_username: Optional[str] = Field(default=None, env="SPLUNK_USERNAME")
    splunk_password: Optional[str] = Field(default=None, env="SPLUNK_PASSWORD")
    
    # Jira settings
    jira_url: Optional[str] = Field(default=None, env="JIRA_URL")
    jira_email: Optional[str] = Field(default=None, env="JIRA_EMAIL")
    jira_api_token: Optional[str] = Field(default=None, env="JIRA_API_TOKEN")
    jira_project_key: str = Field(default="IBG", env="JIRA_PROJECT_KEY")
    
    # Environment configuration mapping
    # Format: "env_name:account_id,splunk_index,jira_project"
    prod_config: str = Field(default="prod:1234567,main,PROJ", env="PROD_CONFIG")
    staging_config: str = Field(default="staging:1234568,staging_main,STAG", env="STAGING_CONFIG")
    dev_config: str = Field(default="dev:1234569,dev_main,DEV", env="DEV_CONFIG")


    # Groq LLM settings
    groq_api_key: Optional[str] = Field(default=None, env="GROQ_API_KEY")
    groq_model: str = Field(default="llama-3.3-70b-versatile", env="GROQ_MODEL")
    
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        case_sensitive = False
    
    def get_environment_config(self, environment: str = "prod") -> Dict[str, str]:
        """
        Get configuration for a specific environment.
        
        Args:
            environment: Environment name (prod, staging, dev)
            
        Returns:
            Dictionary with account_id, splunk_index, jira_project
            
        Raises:
            ValueError: If environment not found
        """
        config_map = {
            "prod": self.prod_config,
            "staging": self.staging_config,
            "dev": self.dev_config
        }
        
        if environment not in config_map:
            raise ValueError(f"Unknown environment: {environment}")
        
        config_str = config_map[environment]
        parts = config_str.split(":")
        if len(parts) != 2:
            raise ValueError(f"Invalid config format for {environment}")
        
        values = parts[1].split(",")
        if len(values) != 3:
            raise ValueError(f"Invalid config values for {environment}")
        
        return {
            "account_id": values[0],
            "splunk_index": values[1],
            "jira_project": values[2]
        }


# Global configuration instance
settings = EnvironmentConfig()