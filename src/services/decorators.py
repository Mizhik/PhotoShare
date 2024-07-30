from functools import wraps

from fastapi import HTTPException, status


def roles_required(roles):
    """
    Decorator for checking if the current user has one of the required roles.

    **Parameters:**

    - `roles` (list): A list of roles that are allowed to access the decorated endpoint.

    **Returns:**

    - Function: The decorator function that wraps the original function.

    **Usage:**

    This decorator is used to restrict access to certain routes or functions based on user roles. 
    It checks if the `current_user` has a role that is included in the `roles` parameter. 
    If the user’s role is not in the allowed roles, it raises a 403 Forbidden HTTP exception.

    **Example:**

    ```python
    @roles_required([Role.admin, Role.moderator])
    @router.get("/admin-only")
    async def admin_only_route(current_user: User = Depends(UserRepository.get_current_user)):
        return {"message": "You have access to this route."}
    ```

    In this example, only users with `Role.admin` or `Role.moderator` will be able to access the `/admin-only` route. Users with other roles will receive a 403 Forbidden error.

    **Raises:**

    - `HTTPException`: If the `current_user`'s role is not in the `roles` list, an HTTP 403 Forbidden exception is raised with the detail message 'You cannot do it!'.
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
