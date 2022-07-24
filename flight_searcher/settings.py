from pydantic import BaseSettings, Field, RedisDsn


# special methods for creating settings
def create_user_agent(
    app_name: str, deployment_build: str, company_name: str, environment: str
):
    return f"{app_name}/{deployment_build} ({company_name} {environment})"


# settings definition
class Environment:
    local: str = "local"
    dev: str = "dev"
    production: str = "production"
    canary: str = "canary"


class MainSettings(BaseSettings):
    # mainly for user agent
    app_name: str = Field(env="app_name", default="My app")
    deployment_build: str = Field(env="deployment_build", default="local")
    environment: str = Field(env="environment", default=Environment.local)
    company_name: str = Field(env="company_name", default="jonas")
    # access to external resources
    redis_url: RedisDsn = Field(env="redis_url", default="redis://localhost/0")
    sentry_dsn: str = Field(env="sentry_dsn", default=None)
    # helpers
    is_debug: bool = Field(env="debug", default=False)


main_stgs = MainSettings()


class AllSettings(MainSettings):
    user_agent: str = create_user_agent(
        main_stgs.app_name,
        main_stgs.deployment_build,
        main_stgs.company_name,
        main_stgs.environment,
    )
    is_local: bool = main_stgs.environment == Environment.local


SETTINGS = AllSettings()
