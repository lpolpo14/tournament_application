# users/permissions.py

from rest_framework.permissions import BasePermission, SAFE_METHODS

"""
Helper methods/classes used for getting roles and ensuring proper role-based authorization.
"""
def get_user_role(user):
    """
    Safely returns user role.
    """
    if not user or not user.is_authenticated:
        return None

    if not hasattr(user, "details"):
        return None

    return user.details.role


def is_sports_admin(user):
    return get_user_role(user) == "sports_admin"


def is_referee(user):
    return get_user_role(user) == "referee"


def is_team_manager(user):
    return get_user_role(user) == "team_manager"


class DenyAll(BasePermission):
    """
    Useful for disabling update/delete actions in ModelViewSets.
    """

    def has_permission(self, request, view):
        return False

"""
The following classes are role-level permissions.
"""

class IsSportsAdmin(BasePermission):
    def has_permission(self, request, view):
        # Must be authenticated and be a sports admin
        return request.user.is_authenticated and is_sports_admin(request.user)


class IsTeamManager(BasePermission):
    def has_permission(self, request, view):
        # Must be authenticated and be a team manager
        return request.user.is_authenticated and is_team_manager(request.user)


class IsReferee(BasePermission):
    def has_permission(self, request, view):
        # Must be authenticated and be a referee
        return request.user.is_authenticated and is_referee(request.user)


class IsTeamManagerOfTeam(BasePermission):
    """
    Team managers can modify only their own teams.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and is_team_manager(request.user)

    def has_object_permission(self, request, view, obj):
        """
        Neat function, checks whether the request has a safe method (List etc.).
        If not, check if the actual team manager is trying to alter the object.
        """
        if request.method in SAFE_METHODS:
            return True

        return (
            is_team_manager(request.user)
            and obj.manager_id == request.user.id
        )


class IsAssignedReferee(BasePermission):
    """
    Referees can modify only matches assigned to them.
    """

    def has_object_permission(self, request, view, obj):
        return obj.referee_id == request.user.id # Is current user the referee with the assigned match?


class CanEditPlayerMatchStatistics(BasePermission):
    """
    Only the assigned referee can create/update/delete statistics.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and is_referee(request.user)

    def has_object_permission(self, request, view, obj):
        return obj.match.referee_id == request.user.id