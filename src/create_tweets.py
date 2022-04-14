# import json
import typing as t

from airtable.from_airtable import AirtableTransformer, join_on_key
from aws.sqs import get_client, send_message_batch
from twitter.create_tweet import DateWrapper, Item, TweetText


# def _save_to_file(data: t.List[str], filename: str) -> None:
#     with open(filename, 'w', encoding='utf-8') as f:
#         json.dump(data, f, ensure_ascii=False)


def _order_tweets_list(tweets: t.List[t.Dict[str, t.Any]]):
    return sorted(tweets, key=lambda d: DateWrapper(
        d['orig_date_of_last_action']
        if 'orig_date_of_last_action' in d
        else d.get('orig_created_time', '2022-01-01T00:00:00.000Z')))


if __name__ == '__main__':
    yale_airtable = AirtableTransformer()
    yale_airtable.input_json = 'assets/yale_current.json'
    yale_airtable.prefix = 'orig_'
    yale_airtable.use_created_time = True
    yale_table = yale_airtable.get_table()

    extended_airtable = AirtableTransformer()
    extended_airtable.input_json = 'assets/additional-table_current.json'
    extended_airtable.prefix = 'e_'
    extended_table = extended_airtable.get_table()

    table = _order_tweets_list(
        join_on_key(yale_table, extended_table, join_on='slug'))

    tweets = []
    for _item in table:
        item = Item(**Item.to_args(_item))
        if item.action and item.name:
            tweets.append(TweetText(item).text())

    send_message_batch(get_client(), tweets)
