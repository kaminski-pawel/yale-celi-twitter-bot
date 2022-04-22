import datetime
from dataclasses import dataclass, field
import random
import string
import typing as t
from urllib.parse import urlparse


SIZE_LIMIT = 280


class TwitterHandle(str):
    """
    Wrapper to help to get the twitter handle or hashtag from an url.
    """

    def __init__(self, *args, **kwargs):
        self.parsed_url = urlparse(self)

    def is_url(self):
        return all([self.parsed_url.scheme, self.parsed_url.netloc])

    @property
    def name(self):
        if self.is_url():
            return self.parsed_url.path.split('/')[-1]
        return self._get_cleaned_name()

    def _get_cleaned_name(self) -> str:
        """
        Removes everything before `/` char, everything after ` (` char,
        also spaces ` ` and `string.punctuation`. Returns cleaned `self` copy.
        """
        s = self.split('/')[-1].split(' (')[0].replace(' ', '')
        return s.translate(str.maketrans('', '', string.punctuation))

    @property
    def hashtag(self):
        return f'#{self.name}' if self.name else ''

    @property
    def handle(self):
        return f'@{self.name}' if self.name else ''


class DateWrapper(datetime.date):
    def __new__(cls, *args):
        """
        Params:
            args: ('2022-04-01T16:57:22.000Z', )

        Returns:
            datetime.date(2022, 1, 1) or empty str
        """
        try:
            t = datetime.datetime.fromisoformat(args[0].rstrip('Z'))
            return super().__new__(cls, t.year, t.month, t.day)
        except ValueError:
            return ''

    def describe(self):
        """Returns date in `Jan 1, 2022` format"""
        return self.strftime(f'%b {self.day}, %Y')


@dataclass
class Item:
    """
    Fixed interface to changing API of original sources,
    dependent on Airtable column names.
    """
    name: str = ''
    industry: str = ''
    status: str = ''
    _status: str = ''
    action: str = ''
    _twitter: str = ''
    twitter: TwitterHandle = field(init=False)
    _updated: str = ''
    updated: datetime.date = field(init=False)
    _last_action: str = ''
    last_action: datetime.date = field(init=False)

    def __post_init__(self, *args, **kwargs):
        self.status = self._get_status()
        self.updated = DateWrapper(datetime.datetime.now(
            datetime.timezone.utc).isoformat())
        self.twitter = TwitterHandle(
            self._twitter if self._twitter else self.name)
        self.last_action = DateWrapper(self._last_action)

    def get(self, key) -> t.Any:
        return getattr(self, key)

    def _get_status(self) -> str:
        return self._status.lower().replace(' ', '')

    @staticmethod
    def to_args(item: t.Dict[str, str]) -> t.Dict[str, str]:
        """Filters dictionary from original source API to arguments of `Item` dataclass.

        Param:
            item: {'orig_name': 'P&G', 'omit': 'omit this'...}
        Returns:
            item: {'name': 'P&G'...}
        """
        def _to_proper_argname(key: str) -> str:
            """
            Transforms input dict key name to valid argument of `Item` dataclass.
            """
            args_keys = {
                'orig_name': 'name',
                'orig_industry': 'industry',
                'orig_grade': '_status',
                'orig_action': 'action',
                'e_twitter': '_twitter',
                'orig_created_time': '_updated',
                'orig_date_of_last_action': '_last_action',
            }
            return args_keys[key] if key in args_keys else ''
        try:
            return {_to_proper_argname(k): v
                    for k, v in item.items()
                    if _to_proper_argname(k) in Item.__dataclass_fields__.keys()}
        except KeyError:
            raise Exception('Please include missing `Item` dataclass arguments '
                            'in _to_proper_argname() function')


class TweetText:
    """
    Creates a tweet text content.

    Example usage:
        ```
        item = Item(**Item.to_args(_some_dict_from_api))
        txt = TweetText(item).text()
        ```
    """

    def __init__(self, item: Item) -> None:
        self.item = item
        self._size_limit = SIZE_LIMIT  # 280
        self._hashtags = [
            '#Boycott',
            '#PutinWarCrimes',
            '#SanctionsRussia',
            '#SaveUkraine',
            '#StandUpForUkraine',
            '#StandWithUkraine',
            '#StopPutin',
            '#StopRussia',
            '#StopWarInUkraine',
            '#Ukraine',
            '#WarInUkraine',
            '#NoWar',
            '#RussiaWar',
        ]

    def text(self) -> str:
        """Returns a tweet content e.g. 
            `🟧 Procter & Gamble (Consumer Staples) is holding off new investments/development in 🇷🇺.

            Current action: scale back unspecified operations in #Russia 
            and stop new investments (as of Apr 8, 2022). 
            #proctergamble #StandWithUkraine #nowar`
            """
        return ' '.join([self._text(), self.hashtags])

    def _text(self) -> str:
        tweet = f'{self.icon} {self.who} {self.what}{self.details}{self.when}.'
        return tweet.replace(' Russia', ' #Russia').replace('  ', ' ').strip()

    @property
    def icon(self) -> str:
        return {
            'diggingin': '🚫',  # ⛔ 🛑 🚫 🟥 ❌
            'buyingtime': '🟧',  # ⚠
            'scalingback': '🟨',
            'suspension': '🟩',
            'withdrawal': '✅',
            '': '',
        }[self.item.status]

    @property
    def who(self) -> str:
        if self.item.industry:
            return f"{self.item.name} ({self.item.industry})"
        else:
            return self.item.name

    @property
    def what(self) -> str:
        return {
            'diggingin': 'is continuing business-as-usual in 🇷🇺.\n\n',
            'buyingtime': 'is holding off new investments/development in 🇷🇺.\n\n',
            'scalingback': 'is reducing current operations in 🇷🇺.\n\n',
            'suspension': 'is suspending 💼 in 🇷🇺.\n\n',
            'withdrawal': 'is withdrawing 💼 from 🇷🇺.\n\n',
            '': '',
        }[self.item.status]

    @property
    def when(self) -> str:
        if self.item.updated and self.item.last_action:
            last_action = self.item.last_action.describe()
            updated = self.item.updated.describe()
            return f' (date of action: {last_action}; up-to-date on: {updated})'
        elif self.item.updated:
            updated = self.item.updated.describe()
            return f' (up-to-date on: {updated})'
        else:
            return ''

    @property
    def details(self) -> str:
        return f"Current action: {self.item.action}"

    @property
    def hashtags(self) -> str:
        tweet_size = len(self._text())
        hashtags, _hashtags = '', ''
        random.shuffle(self._hashtags)
        for hashtag in [self.item.twitter.hashtag, *self._hashtags]:
            _hashtags += ' ' + hashtag
            if tweet_size + len(' '.join(_hashtags).strip()) < self._size_limit:
                hashtags += ' ' + hashtag
        return hashtags.strip()
