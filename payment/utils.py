# -*- coding: utf-8 -*-

import dateutil.parser
import logging

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.utils.translation import ugettext_lazy as _
from django.utils import translation
from opaque_keys.edx.keys import CourseKey

from requests.exceptions import ConnectionError
from edxmako.shortcuts import render_to_string

from openedx.core.djangoapps.commerce.utils import ecommerce_api_client
from openedx.core.djangoapps.course_groups.models import CourseUserGroup
from openedx.core.djangoapps.course_groups.cohorts import get_cohort_by_name, \
    add_user_to_cohort

from courses.models import Course

logger = logging.getLogger(__name__)


def get_order(user, order_id):
    try:
        order = ecommerce_api_client(user).orders(order_id).get()
    except ConnectionError as e:
        order = None
        logger.exception(e)
    return order


def get_basket(user, order_id):
    return ecommerce_api_client(user).baskets(order_id).get()


def get_course(order_or_basket):
    """Retrieve course from order or basket product properties."""
    attributes = order_or_basket['lines'][0]['product']['attribute_values']
    course_key = [d['value'] for d in attributes if d['name'] == 'course_key'][0]
    return Course.objects.get(key=course_key)


def get_order_context(user, order, course):
    context = dict()
    context['order'] = order
    context['ordered_course'] = course
    context['user'] = user
    context['total_incl_tax'] = order['total_excl_tax']  # we do not know yet how we will handle taxes in the future...
    return context


def send_confirmation_email(user, order):
    course = get_course(order)
    subject = _(u"[FUN-MOOC] Payment confirmation")
    context = get_order_context(user, order, course)
    with translation.override(user.profile.language):
        text_content = render_to_string('payment/email/confirmation-email.txt', context)
        html_content = render_to_string('payment/email/confirmation-email.html', context)
    email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email],
            bcc=[settings.PAYMENT_ADMIN],
        )
    email.attach_alternative(html_content, "text/html")
    email.send()


def register_user_verified_cohort(user, order):
    """
    Once a user has been verified, add it to a cohort.

    The cohort to which the user should be added is given by the VERIFIED_COHORTS and the DEFAULT_VERIFIED_COHORT
    settings. VERIFIED_COHORTS is a dict of the form:

        {
            "<course id>": "<cohort name>",
        }

    If the course ID is not present in VERIFIED_COHORTS, the cohort name is given by DEFAULT_VERIFIED_COHORT.
    If a course is associated to a cohort that doesn't exist or an empty cohort name, then the user is not added to any
    cohort. Thus, to disable this feature for a specific course, set:

        VERIFIED_COHORTS = {
            "<course id>": None,
        }

    To disable this feature globally, set:

        VERIFIED_COHORTS = {}
        DEFAULT_VERIFIED_COHORT = None
    """
    course = get_course(order)
    verified_cohort_default_name = getattr(settings, "DEFAULT_VERIFIED_COHORT", "")
    verified_cohort_name = getattr(settings, "VERIFIED_COHORTS", {}).get(
        course.key,
        verified_cohort_default_name,
    )
    cohort = None
    if verified_cohort_name:
        course_key = CourseKey.from_string(course.key)
        try:
            cohort = get_course_cohort_by_name(course_key, verified_cohort_name)
        except CourseUserGroup.DoesNotExist:
            pass
    if cohort:
        # This will also trigger the edx.cohort.user_add_requested event
        add_user_to_cohort(cohort, user.email)


def format_date_order(order, format):
    return dateutil.parser.parse(order['date_placed']).strftime(format)
