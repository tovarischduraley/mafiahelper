import core


def get_role_emoji(role: core.Roles) -> str:
    match role:
        case core.Roles.MAFIA:
            return "🔫"
        case core.Roles.CIVILIAN:
            return "💛"
        case core.Roles.DON:
            # return "🎩"
            return "🤵🏿‍♂️"
        case core.Roles.SHERIFF:
            # return "🔎"
            return "🕵🏻‍♂️"
        case _:
            raise Exception(f"Unknown role <{role}>")


def get_team_emoji(team: core.Teams) -> str:
    match team:
        case core.Teams.RED:
            return "🔴"
        case core.Teams.BLACK:
            return "⚫️"
        case _:
            raise Exception(f"Unknown team <{team}>")
