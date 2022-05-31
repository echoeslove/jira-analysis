from jira import JIRA
jira_client = JIRA(server='http://172.20.200.191:8080',
                   auth=('chenmingjie', 'MITcoming511'))
jira_issues = jira_client.search_issues(
    'issuetype in (生产Bug, sub-Bug) ' +
    'AND status = Closed ' +
    'AND created >= 2022-03-28 ' +
    'AND assignee in (yurui, wangchengjie, xujian4, yinguanqun, ' +
    'yangyabing, lushijie, jitao, tianhao2, wuyuyang, chenmingjie, ' +
    'shantenghui, wuqicong, panzheqi, linjingyao, xiayan, wusong, ' +
    'yinrongjie, songjingjing, zhuzhoulin, chenhongnian, bingguanqi, ' +
    'luoxiaojing, yinshangsheng, chensixiong, hanjing, lihao3, ' +
    'lihaorui, duweibin, chenzhiwei2) ' +
    'ORDER BY created ASC, assignee ASC, updated DESC')

for single in jira_issues:
    print('key: {}, assignee: {}, type: {}, created: {}'.format(
        single.key, single.fields.assignee, single.fields.issuetype,
        single.fields.created))
