import json
import random
import time

from aws.sqs import delete_message, get_client, receive_message
from twitter.create_tweet import SIZE_LIMIT
from twitter.post_tweet import post_tweet


PAUSE_TIME_IN_SECONDS = 60 * random.uniform(3, 7)  # * 5


if __name__ == '__main__':
    client = get_client()
    while True:
        get_response = receive_message(client)
        if get_response.is_ok() and get_response.get_receipt_handle():
            receipt_handle = get_response.get_receipt_handle()

            print('=' * 30, '\n',
                  get_response.msg_body.replace('\n', ''), '\n', '=' * 30)
            if len(get_response.msg_body) <= SIZE_LIMIT:
                twt_response = post_tweet(get_response.msg_body)
                if twt_response.errors:
                    print('Failed to tweet. Error: %s' %
                          json.dumps(twt_response.errors))
                    break
            else:
                print('/n')
                print('==> Tweet text is too long.', get_response.msg_body)
                print('/n/n/n')

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
