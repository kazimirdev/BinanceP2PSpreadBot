from dataclasses import dataclass
from environs import Env

@dataclass
class TgBot:
    token: str
    admins: list[int]
    redis: bool

    @staticmethod
    def from_env(env: Env):
        token = env.str("TOKEN")
        admins = env.list("ADMINS", subcast=int)
        redis = env.bool("REDIS")
        return TgBot(token=token,
                     admins=admins, 
                     redis=redis)


@dataclass
class RedisConfig:
    """
    Redis configuration class.

    Attributes
    ----------
    redis_pass : Optional(str)
        The password used to authenticate with Redis.
    redis_port : Optional(int)
        The port where Redis server is listening.
    redis_host : Optional(str)
        The host where Redis server is located.
    """

    redis_pass: str|None
    redis_port: int|None
    redis_host: str|None

    def dsn(self) -> str:
        """
        Constructs and returns a Redis DSN (Data Source Name) for this database configuration.
        """
        if self.redis_pass:
            return f"redis://:{self.redis_pass}@{self.redis_host}:{self.redis_port}/0"
        else:
            return f"redis://{self.redis_host}:{self.redis_port}/0"

    @staticmethod
    def from_env(env: Env):
        """
        Creates the RedisConfig object from environment variables.
        """
        redis_pass = env.str("REDIS_PASS")
        redis_port = env.int("REDIS_PORT")
        redis_host = env.str("REDIS_HOST")

        return RedisConfig(redis_pass=redis_pass, 
                           redis_port=redis_port, 
                           redis_host=redis_host)


@dataclass
class Config:
    tgbot: TgBot
    redis: RedisConfig


def load_config(path: str|None = None) -> Config:
    env = Env()
    env.read_env(path)

    return Config(
        tgbot=TgBot.from_env(env),
        redis=RedisConfig.from_env(env)
    )

