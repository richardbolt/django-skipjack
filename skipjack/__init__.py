""" URL Definitions for the Skipjack AuthorizeAPI. """  

SKIPJACK_POST_URL = "https://www.skipjackic.com" \
        "/scripts/evolvcc.dll?AuthorizeAPI"
SKIPJACK_TEST_POST_URL = "https://developer.skipjackic.com" \
        "/scripts/evolvcc.dll?AuthorizeAPI"

SKIPJACK_TEST_STATUS_POST_URL = "https://developer.skipjackic.com" \
        "/scripts/evolvcc.dll?SJAPI_TransactionStatusRequest"
SKIPJACK_STATUS_POST_URL = "https://www.skipjackic.com" \
        "/scripts/evolvcc.dll?SJAPI_TransactionStatusRequest"

SKIPJACK_TEST_STATUS_CHANGE_POST_URL = "https://developer.skipjackic.com" \
        "/scripts/evolvcc.dll?SJAPI_TransactionChangeStatusRequest"
SKIPJACK_STATUS_CHANGE_POST_URL = "https://www.skipjackic.com" \
        "/scripts/evolvcc.dll?SJAPI_TransactionChangeStatusRequest"