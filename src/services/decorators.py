from functools import wraps

from fastapi import HTTPException, status


def roles_required(roles):
    """
    Decorator for user role checking.
    """

    def decorator(function):
        @wraps(function)
        async def inner(**kwargs):
            if kwargs['current_user'].role not in roles:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You cannot do it!')

            response = await function(**kwargs)
            return response

        return inner

    return decorator
