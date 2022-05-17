import aiohttp
from typing import TYPE_CHECKING, Optional, List
from khl_card.card import Card
from khl_card.types import NamedColor
from khl_card.modules import *
from khl_card.accessory import *

if TYPE_CHECKING:
    from ..bot import GenshinBot


async def get_events(genshin_bot: 'GenshinBot') -> Optional[List[dict]]:
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(genshin_bot.config.github_events_api) as response:
                events = await response.json()  # type: List[dict]
                return events
        except TimeoutError as e:
            return None


async def push_events(genshin_bot: 'GenshinBot') -> None:
    events = await get_events(genshin_bot)
    if events is None:
        return
    need_push = []
    for event in events:
        if int(event.get('id')) > genshin_bot.config.last_event_id:
            need_push.append(event)
        else:
            break
    while need_push:
        event = need_push.pop()
        await push_to_khl(event, genshin_bot)


async def push_to_khl(event, genshin_bot: 'GenshinBot'):
    event_type = event['type']
    card = Card()
    if event_type == 'PushEvent':
        user = event['actor']
        card.append(Section(Kmarkdown(f'**{user["display_login"]}**'), mode='left', accessory=Image(src=user['avatar_url'], size='sm', circle=True)))
        channel = await genshin_bot.fetch_public_channel(genshin_bot.config.update_channel)
        commits = event['payload']['commits']
        repo_name = event["repo"]["name"]
        if len(commits) == 1:
            url = commits[0]['url']  # type: str
            url = url.replace('api.', '').replace('repos/', '').replace('commits', 'commit')
        else:
            url = event["repo"]["url"]  # type: str
            url = url.replace('api.', '').replace('repos/', '') + '/compare/' + commits[0]['sha'] + '...' + commits[-1]['sha']
        card.set_color(NamedColor.AQUA)
        card.append(Section(Kmarkdown(f'[\[{repo_name}\] {len(commits)} new commits]({url})')))
        for commit in commits:
            sha = commit['sha'][:7]
            commit_url = commit['url']  # type: str
            commit_url = commit_url.replace('api.', '').replace('repos/', '').replace('commits', 'commit')
            author = commit['author']['name']
            commit_message = commit['message']
            module = Section(Kmarkdown(f'[{sha}]({commit_url}) {commit_message} - {author}'))
            card.append(module)
        await channel.send([card.build()])
        genshin_bot.config.set_last_event(int(event['id']))
    elif event_type == 'IssuesEvent':
        user = event['actor']
        card.append(Section(Kmarkdown(f'**{user["display_login"]}**'), mode='left', accessory=Image(src=user['avatar_url'], size='sm', circle=True)))
        channel = await genshin_bot.fetch_public_channel(genshin_bot.config.update_channel)
        card.set_color(NamedColor.GREEN)
        action = event['payload']['action']
        issue = event['payload']['issue']
        repo_name = event["repo"]["name"]
        title = issue['title']
        body = issue['body']
        issue_number = issue['number']
        issue_url = issue['html_url']
        if action == 'opened':
            card.append(Section(Kmarkdown(f'[\[{repo_name}\] Issue opened: #{issue_number} {title}]({issue_url})')))
            card.append(Section(Kmarkdown(body if body is not None else '')))
        elif action == 'closed':
            card.append(Section(Kmarkdown(f'[\[{repo_name}\] Issue closed: #{issue_number} {title}]({issue_url})')))
        await channel.send([card.build()])
        genshin_bot.config.set_last_event(int(event['id']))
    elif event_type == 'IssueCommentEvent':
        card.set_color(NamedColor.GOLD)
        user = event['payload']['comment']['user']
        card.append(Section(Kmarkdown(f'**{user["login"]}**'), mode='left', accessory=Image(src=user['avatar_url'], size='sm', circle=True)))
        channel = await genshin_bot.fetch_public_channel(genshin_bot.config.update_channel)
        comment = event['payload']['comment']
        issue = event['payload']['issue']
        repo_name = event["repo"]["name"]
        title = issue['title']
        number = issue['number']
        url = comment['html_url']
        card.append(Section(Kmarkdown(f'[\[{repo_name}\] New comment on issue #{number}: {title}]({url})')))
        card.append(Section(Kmarkdown(comment['body'])))
        await channel.send([card.build()])




