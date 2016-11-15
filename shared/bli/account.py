from flask import current_app
from datetime import datetime

from shared.util import logger, error, constants
from shared.db.model import *
from shared.services import mail
import random, string

LOGGER = logger.getLogger('shared.bli.account')

def __trim_dict(**kwargs):
    return {key: value for key, value in kwargs.items() if value}

def signup(account):
    LOGGER.info('signup entry')

    try:
        existing_account = get_account_by_email(account.email)
    except Exception as e:
        LOGGER.error(e.message)
        raise error.DatabaseError(constants.GENERIC_ERROR,e)

    if existing_account is not None:
        raise error.AccountExistsError(constants.ACCOUNT_WITH_EMAIL_ALREADT_EXISTS)

    try:
        #NOTE: The account parameters are not verified, if it is a non None value then it will be sent as param to the Account model
        current_app.db_session.add(account)
        current_app.db_session.commit()
    except Exception as e:
        LOGGER.error(e.message)
        raise error.DatabaseError(constants.GENERIC_ERROR,e)

    #Send verification email
    try:
        initiate_email_verification(account)
    except error.DatabaseError as e:
        Logger.error(e.message)
        raise error.EmailVerificationSendingError(constants.GENERIC_ERROR, e.orig_exp)

    LOGGER.info('signup exit')

def isEmailVerified(account):
    if account and (account.status == int(Account.VERIFIED) or account.status == int(Account.VERIFIED_EMAIL)):
        return True
    return False

def initiate_email_verification(account):
    LOGGER.info('initiate_email_verification entry')
    id = str(account.id + constants.EMAIL_ACCOUNT_ID_CONSTANT)
    print 'TEST id=:%s' % (id)
    token = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(constants.EMAIL_VERIFICATION_TOKEN_LENGTH))
    print 'TEST token=:%s' % (token)
    account.email_verification_token = token

    try:
        #save token to DB
        current_app.db_session.add(account)
        current_app.db_session.commit()
    except Exception as e:
        LOGGER.error(e.message)
        raise error.DatabaseError(constants.GENERIC_ERROR,e)

    # send verification email
    link = constants.EMAIL_VERIFICATION_LINK % (id, token)
    text = 'Thanks for signing up with Ziplly.\nPlease click on the below link to verify your email.\n'+link
    html_text = "<h3>Thanks for signing up with Ziplly.</h3><br /><h4>Please click on the below link to verify your email.</h4><br />"+link

    try:
        mail.send(current_app.config['ADMIN_EMAIL'],
            account.email,
            constants.EMAIL_VERIFICATION_SUBJECT,
            text,
            html_text)
    except Exception as e:
        LOGGER.error(e.message)
        raise error.MailServiceError(constants.GENERIC_ERROR,e)

    LOGGER.info('initiate_email_verification exit')

def verify_email(id, token):
    LOGGER.info('verify_email entry')

    account_id = id - constants.EMAIL_ACCOUNT_ID_CONSTANT
    try:
        account = get_account_by_id(account_id)
    except Exception as e:
        LOGGER.error(e.message)
        raise error.DatabaseError(constants.GENERIC_ERROR,e)

    if not account:
        raise error.AccountNotFoundError('Invalid verification code.')
    elif account.status == int(Account.VERIFIED) or account.status == int(Account.VERIFIED_EMAIL):
        raise error.AccountEmailAlreadyVerifiedError('Email already verified.')
    elif token != account.email_verification_token:
        raise error.EmailVerificationNotMatchError('Invalid verification code.')
    else:
        try:
            account.status = Account.VERIFIED_EMAIL
            stripe_customer = current_app.stripe_client.create_customer(
            account.email)
            account.stripe_customer_id = stripe_customer['id']
            account.time_updated = datetime.now()
            current_app.db_session.add(account)
            current_app.db_session.commit()
        except Exception as e:
            LOGGER.error(e.message)
            raise error.DatabaseError(constants.GENERIC_ERROR,e)

    LOGGER.info('verify_email exit')

def is_application_complete(account):
    LOGGER.info('is_application_complete entry')
    if not account or \
        not account.employers or \
        not account.get_usable_fis() or \
        not account.is_active_primary_bank_verified():
        LOGGER.info('is_application_complete:False exit')
        return False
    LOGGER.info('is_application_complete:True exit')
    return True

def application_next_step(account):
    LOGGER.info('application_next_step entry')
    next = {}
    if not account.employers:
        next['enter_employer_information'] = True
    elif not account.get_usable_fis():
        next['add_bank'] = True
    elif not account.is_active_primary_bank_verified():
        primary_bank = account.get_active_primary_bank()
        #TODO: currently if the account has active banks atleast  one of them is primary_bank
        # not checking if primary_bank == None
        next['verify_bank'] = True
        next['id'] = primary_bank.id
    else:
        next['application_complete'] = True
    LOGGER.info('application_next_step exit')
    return next

def add_employer(account, employer):
    LOGGER.info('add_employer entry')
    if not account:
        raise ValueError('Invalid account (None) passed in.')
    if not employer:
        raise ValueError('Invalid employer (None) passed in.')

    try:
        account.employers.append(employer)
        current_app.db_session.add(account)
        current_app.db_session.commit()
    except Exception as e:
        LOGGER.error(e.message)
        raise error.DatabaseError(constants.GENERIC_ERROR,e)
    LOGGER.info('add_employer exit')
