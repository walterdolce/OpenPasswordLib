Feature: Retrieve the list of items from a keychain
  So that I can overview the contents of a keychain
  As an API user
  I want to be able to iterate over the items in the keychain

  Scenario: Iterating over a keychain
    Given I have a keychain containing items
    When I iterate over the keychain
    Then I should get all of those items

  Scenario: Failing to iterate over a locked keychain
    Given I have a locked keychain
    When I iterate over the keychain
    Then an KeychainLockedException should be raised

  Scenario: Verifying an item exists in the keychain

  Scenario: Failing to verify if an item exists in a locked keychain