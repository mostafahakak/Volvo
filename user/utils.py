def upload_profile_picture(instance, filename):
    return "users/{0}/{1}".format(instance.get_full_name(), filename)
