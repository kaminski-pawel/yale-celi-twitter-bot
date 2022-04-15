import json
import time

from aws.sqs import delete_message, get_client, receive_message
from twitter.post_tweet import post_tweet


PAUSE_TIME_IN_SECONDS = 60 * 5


if __name__ == '__main__':
    client = get_client()
    while True:
        get_response = receive_message(client)
        if get_response.is_ok() and get_response.get_receipt_handle():
            receipt_handle = get_response.get_receipt_handle()

            print('=' * 30, '\n',
                  get_response.msg_body.replace('\n', ''), '\n', '=' * 30)
            twt_response = post_tweet(get_response.msg_body)
            if twt_response.errors:
                print('Failed to tweet. Error: %s' %
                      json.dumps(twt_response.errors))
                break

            del_response = delete_message(
                client, receipt_handle=receipt_handle)
            if not del_response.is_ok():
                print('Failed to delete message. Error: %s.' %
                      del_response.response)
                break
            time.sleep(PAUSE_TIME_IN_SECONDS)
        else:
            print('Failed to receive message. Status code: %s.' %
                  get_response.status_code)
            break
