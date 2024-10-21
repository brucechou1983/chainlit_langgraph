from typing import Awaitable, Callable, Dict, Optional

from chainlit.config import config
from chainlit.oauth_providers import get_configured_oauth_providers
from chainlit.telemetry import trace
from chainlit.user import User
from chainlit.utils import wrap_user_function


@trace
def maybe_oauth_callback(
    func: Callable[
        [str, str, Dict[str, str], User, Optional[str]], Awaitable[Optional[User]]
    ],
) -> Optional[Callable]:
    """
    Framework agnostic decorator to authenticate the user via oauth

    Args:
        func (Callable[[str, str, Dict[str, str], User, Optional[str]], Awaitable[Optional[User]]]): The authentication callback to execute.

    Example:
        @cl.oauth_callback
        async def oauth_callback(provider_id: str, token: str, raw_user_data: Dict[str, str], default_app_user: User, id_token: Optional[str]) -> Optional[User]:

    Returns:
        Optional[Callable[[str, str, Dict[str, str], User, Optional[str]], Awaitable[Optional[User]]]]: The decorated authentication callback.
    """

    if len(get_configured_oauth_providers()) == 0:
        return None

    config.code.oauth_callback = wrap_user_function(func)
    return func
