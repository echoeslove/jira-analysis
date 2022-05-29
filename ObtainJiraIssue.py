from jira import JIRA
jira_client = JIRA(server='http://172.20.200.191:8080',
                   auth=('chenmingjie', 'MITcoming511'))
jira_issues = jira_client.search_issues(
    'assignee in (currentUser()) ORDER BY created DESC, updated DESC')

for single in jira_issues:
    print('key: {}, assignee: {}, type: {}'.format(
        single.key, single.fields.assignee, single.fields.issuetype))
