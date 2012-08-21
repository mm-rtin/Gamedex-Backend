from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from google.appengine.api import users

import logging


class Authentication(object):

    ADMIN_EMAIL = 'hexvector@gmail.com'

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # authenticate admin
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @staticmethod
    def authenticate_admin(orig_func):

        # decorated function
        def _decorated(*args, **kwargs):

            # get authenticated user
            user = users.get_current_user()

            # logged in page
            if user:

                logging.info('-------- AUTHENTICATE ADMIN -----------')
                logging.info(user.email())
                logging.info('------------------------')

                # validate admin email
                if user.email() == Authentication.ADMIN_EMAIL:

                    # authenticated > call original function with arguments
                    return orig_func(*args, **kwargs)

                else:
                    # not admin > return to index
                    return render_to_response('index.html')

            # redirect to login page
            loginURL = users.create_login_url('/')
            return HttpResponseRedirect(loginURL)

        return _decorated
