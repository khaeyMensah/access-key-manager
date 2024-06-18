def is_school_personnel(user):
    return user.is_authenticated and user.is_school_personnel

def is_admin(user):
    return user.is_authenticated and user.is_admin
