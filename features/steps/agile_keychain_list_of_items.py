import os
import openpassword
from openpassword.exceptions import KeychainLockedException

TEMP_KEYCHAIN_PATH = os.path.join('tests', 'fixtures', 'temp.agilekeychain')
CORRECT_PASSWORD = "correctpassword"


@given('I have a keychain containing items')
def step_impl(context):
    context.items = ["website credential", "credit card number", "openpassword password", "DSA key"]

    _add_new_keychain_to_context(context)
    context.keychain.unlock(CORRECT_PASSWORD)
    [context.keychain.append({'id': item}) for item in context.items]


@when('I iterate over the keychain')
def step_impl(context):
    try:
        context.found_items = list(context.keychain)
    except KeychainLockedException:
        context.keychain_locked_exception_raised = True


@then('I should get all of those items')
def step_impl(context):
    for item in context.items:
        assert item in context.found_items


def _add_new_keychain_to_context(context):
    context.keychain = openpassword.AgileKeychain(TEMP_KEYCHAIN_PATH)
    context.keychain.initialise(CORRECT_PASSWORD)
    context.remove_path = TEMP_KEYCHAIN_PATH


@then('an KeychainLockedException should be raised')
def step_impl(context):
    if not context.keychain_locked_exception_raised:
        return False
