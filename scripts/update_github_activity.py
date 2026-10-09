"""Refresh the homepage contribution calendar from GitHub's GraphQL API.

Run with a GITHUB_TOKEN in the environment. Only daily counts are stored; repository
names never leave GitHub.
"""

import json
import os
import sys
import urllib.request
from datetime import UTC, datetime
from pathlib import Path
from typing import TypedDict

GITHUB_LOGIN = 'Adamruns'
GRAPHQL_URL = 'https://api.github.com/graphql'
OUTPUT_PATH = Path(__file__).resolve().parent.parent / 'assets' / 'data' / 'github-activity.json'
# Private work contributions only reach this query while the profile shares them.
# A sharp drop means that setting was turned off, so keep the last good calendar.
MINIMUM_RETAINED_SHARE = 0.5
CALENDAR_QUERY = '''
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount } }
      }
    }
  }
}
'''


class GitHubActivity(TypedDict):
    counts: list[int]
    start: str
    total: int
    updated: str


class CalendarShrankError(Exception):
    def __init__(self, previous_total: int, new_total: int) -> None:
        super().__init__(
            f'GitHub reported {new_total} contributions, down from {previous_total}. '
            'Check that "Include private contributions on my profile" is still enabled.'
        )


def fetch_calendar(token: str) -> dict:
    request = urllib.request.Request(
        GRAPHQL_URL,
        data=json.dumps({'query': CALENDAR_QUERY, 'variables': {'login': GITHUB_LOGIN}}).encode(),
        headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        graphql_response = json.load(response)

    if graphql_response.get('errors'):
        raise RuntimeError(f'GitHub GraphQL errors: {graphql_response["errors"]}')

    return graphql_response['data']['user']['contributionsCollection']['contributionCalendar']


def build_activity(calendar: dict) -> GitHubActivity:
    days = [day for week in calendar['weeks'] for day in week['contributionDays']]
    return {
        'counts': [day['contributionCount'] for day in days],
        'start': days[0]['date'],
        'total': calendar['totalContributions'],
        'updated': datetime.now(UTC).isoformat(timespec='seconds'),
    }


def read_previous_activity() -> GitHubActivity | None:
    if not OUTPUT_PATH.exists():
        return None

    return json.loads(OUTPUT_PATH.read_text())


def main() -> None:
    token = os.environ.get('GITHUB_TOKEN')
    if not token:
        sys.exit('Set GITHUB_TOKEN to query the GitHub GraphQL API.')

    activity = build_activity(fetch_calendar(token))
    previous_activity = read_previous_activity()
    if previous_activity:
        if activity['total'] < previous_activity['total'] * MINIMUM_RETAINED_SHARE:
            raise CalendarShrankError(previous_activity['total'], activity['total'])

        if (activity['start'], activity['counts']) == (previous_activity['start'], previous_activity['counts']):
            print('GitHub activity is unchanged.')
            return

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(activity, separators=(',', ':')) + '\n')
    print(f'Wrote {activity["total"]} contributions starting {activity["start"]}.')


if __name__ == '__main__':
    main()
