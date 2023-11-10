from db.model import *


def apply_name_condition(users_query, name_user):
    if name_user:
        users_query = users_query.where(User.name.contains(name_user))
    return users_query


def apply_team_name_condition(teams_query, name_team):
    if name_team:
        teams_query = teams_query.where(Team.name.contains(name_team))
    return teams_query
