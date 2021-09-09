# -*- coding: utf-8 -*-
"""
All asynchronous tasks runned through enDI are stored here
Tasks are handled by a celery service
Redis is used as the central bus
"""
import time
import transaction
from pyramid.threadlocal import get_current_request

from pyramid_celery import celery_app

from endi_base.exception import (
    UndeliveredMail,
    MailAlreadySent,
)
from endi_celery.mail import send_salary_sheet

from endi_celery.tasks import utils
from endi_celery.models import (
    MailingJob,
)


logger = utils.get_logger(__name__)


def _mail_format_message(mail_message_tmpl, company, kwds):
    """
    Return the message to be sent to a single company
    :param str mail_message_tmpl: Template for the mail message
    :param obj company: The company object
    :param dict kwds: Additionnal keywords to pass to the string.format method
    """
    kwds['company'] = company
    message = mail_message_tmpl.format(**kwds)
    return message


@celery_app.task(bind=True)
def async_mail_salarysheets(self, job_id, mails, force):
    """
    Asynchronously sent a bunch of emails with attached salarysheets

    :param int job_id: The id of the MailSendJob
    :param mails: a list of dict compound of
        {
            'id': company_id,
            'attachment': attachment filename,
            'attachment_path': attachment filepath,
            'message': The mail message,
            'subject': The mail subject,
            'company_id': The id of the company,
            'email': The email to send it to,
        }
    :param force: Should we force the mail sending
    """
    logger.info(u"We are launching an asynchronous mail sending operation")
    logger.info(u"  The job id : %s" % job_id)

    from endi_base.models.base import DBSESSION
    # Mark job started
    utils.start_job(self.request, MailingJob, job_id)

    mail_count = 0
    error_count = 0
    error_messages = []
    request = get_current_request()
    session = DBSESSION()
    for mail_datas in mails:
        transaction.begin()
        # since we send a mail out of the transaction process, we need to commit
        # each mail_history instance to avoid sending and not storing the
        # history
        try:
            company_id = mail_datas['company_id']
            email = mail_datas['email']

            if email is None:
                logger.error(u"no mail found for company {0}".format(
                    company_id)
                )
                continue
            else:
                message = mail_datas['message']
                subject = mail_datas['subject']
                logger.info(u"  The mail subject : %s" % subject)
                logger.info(u"  The mail message : %s" % message)

                mail_history = send_salary_sheet(
                    request,
                    email,
                    company_id,
                    mail_datas['attachment'],
                    mail_datas['attachment_path'],
                    force=force,
                    message=message,
                    subject=subject,
                )
                # Stores the history of this sent email
                session.add(mail_history)
            transaction.commit()

        except MailAlreadySent as e:
            transaction.abort()
            error_count += 1
            msg = u"Ce fichier a déjà été envoyé {0}".format(
                mail_datas['attachment']
            )
            error_messages.append(msg)
            logger.exception(u"Mail already delivered")
            logger.error(u"* Part of the Task FAILED")
            continue

        except UndeliveredMail as e:
            transaction.abort()
            error_count += 1
            msg = u"Impossible de délivrer de mail à l'entreprise {0} \
(mail : {1})".format(company_id, email)
            error_messages.append(msg)
            logger.exception(u"Unable to deliver an e-mail")
            logger.error(u"* Part of the Task FAILED")
            continue

        except Exception as e:
            transaction.abort()
            error_count += 1
            logger.exception(u"The subtransaction has been aborted")
            logger.error(u"* Part of the task FAILED !!!")
            error_messages.append(u"{0}".format(e))

        else:
            mail_count += 1
            logger.info(u"The transaction has been commited")
            logger.info(u"* Part of the Task SUCCEEDED !!!")

    messages = [u"{0} mails ont été envoyés".format(mail_count)]
    messages.append(
        u"{0} mails n'ont pas pu être envoyés".format(error_count)
    )

    logger.info(u"-> Task finished")
    if error_count > 0:
        utils.record_failure(
            MailingJob,
            job_id,
            error_messages=error_messages,
            messages=messages,
        )
    else:
        utils.record_completed(
            MailingJob,
            job_id,
            messages=messages,
        )
