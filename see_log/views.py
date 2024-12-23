import sqlite3

from django.shortcuts import render

# 数据库路径配置
DB_PATH = '/Users/pengtao.geng/Library/Application Support/btalk/databases/pengtao.geng.db'


# Create your views here.

def query_app_log(request, app_name):
    # 连接到SQLite数据库
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 执行查询，使用参数化查询来防止SQL注入
    cursor.execute("""
        select 
            strftime('%Y-%m-%d %H:%M:%S', datetime(`time` / 1000, 'unixepoch', '+8 hour')) c_datetime,
            Content
        from IM_Message
        where "From" = 'rbt_wmonitor_elog'
          and (Content like '%应用: ' || ? || '%')
          and (Content not like '%from netty client%')
          and (Content not like '%urls to invokers error%')
          and (Content not like '%securityTest-authTest%')
          AND time >= strftime('%s', 'now') * 1000 - 8 * 60 * 60 * 1000
        order by time desc;
    """, (app_name,))

    rows = cursor.fetchall()

    # 将查询结果转换为字典列表
    data = []
    for row in rows:
        data.append({
            'datetime': row[0],
            'content': row[1],
        })

    # 关闭数据库连接
    cursor.close()
    conn.close()

    return render(request, 'see_log/app_log_table.html', {
        'data': data,
        'app_name': app_name
    })


def app_logs(request):
    # 获取时间范围参数，默认为8小时
    hours = request.GET.get('hours', '8')
    # 确保hours是有效的选项
    valid_hours = ['1', '2', '8', '12', '24']
    hours = hours if hours in valid_hours else '8'

    # 连接到SQLite数据库
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 执行SQL查询
    sql = """
    select 
        REPLACE(SUBSTR(Content, 1, INSTR(Content, CHAR(10)) - 1) ,'[ErrorLog]应用: ', '') AS app_name,
        count(*) AS log_count
    from IM_Message
    where "From" = 'rbt_wmonitor_elog'
      and (Content not like '%from netty client%')
      and (Content not like '%urls to invokers error%')
      and (Content not like '%securityTest-authTest%')
      AND time >= strftime('%s', 'now') * 1000 - ? * 60 * 60 * 1000
    GROUP BY REPLACE(SUBSTR(Content, 1, INSTR(Content, CHAR(10)) - 1) ,'[ErrorLog]应用: ', '')
    ORDER BY log_count DESC;
    """

    cursor.execute(sql, (hours,))
    results = cursor.fetchall()

    # 处理查询结果
    log_stats = [{'app_name': row[0], 'log_count': row[1]} for row in results]

    # 计算总错误日志数
    total_logs = sum(stat['log_count'] for stat in log_stats)

    context = {
        'log_stats': log_stats,
        'total_logs': total_logs,
        'hours': hours,
        'valid_hours': valid_hours,
    }

    return render(request, 'see_log/app_logs.html', context)


def get_alert_type(content):
    """根据内容判断告警类型"""
    if '【OPS提醒】' in content and '描述: [调度系统]' not in content:
        return '应用报警'
    elif '【OPS告警】' in content:
        return 'delta告警'
    elif '描述: [调度系统]' in content:
        return 'job调度'
    return '未知类型'


def ivr_log(request):
    # 获取时间范围参数，默认为100小时
    hours = request.GET.get('hours', '100')
    # 确保hours是有效的选项
    valid_hours = ['24', '48', '72', '100', '168']  # 24小时、48小时、72小时、100小时、7天
    hours = hours if hours in valid_hours else '100'

    # 获取关键字参数和告警类型参数
    keyword = request.GET.get('keyword', '').strip()
    alert_type = request.GET.get('alert_type', '').strip()

    # 连接数据库
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 执行查询
    query = """
        SELECT
            strftime('%Y-%m-%d %H:%M:%S', datetime(`time` / 1000, 'unixepoch', '+8 hour')) AS datetime,
            Content as content
        FROM IM_Message
        WHERE "From" = 'rbt_delta_notify_ivr'
          AND time >= strftime('%s', 'now') * 1000 - ? * 60 * 60 * 1000
          AND (? = '' OR Content LIKE '%' || ? || '%')
        ORDER BY time DESC
        """

    cursor.execute(query, (hours, keyword, keyword))
    results = cursor.fetchall()

    # 将结果转换为字典列表，并计算告警类型
    ivr_logs = [
        {
            'datetime': row[0],
            'content': row[1],
            'alert_type': get_alert_type(row[1])
        }
        for row in results
    ]

    # 如果指定了告警类型，进行过滤
    if alert_type:
        ivr_logs = [log for log in ivr_logs if log['alert_type'] == alert_type]

    valid_alert_types = ['应用报警', 'delta告警', 'job调度']

    return render(request, 'see_log/ivr_log.html', {
        'ivr_logs': ivr_logs,
        'hours': hours,
        'valid_hours': valid_hours,
        'keyword': keyword,
        'alert_type': alert_type,
        'valid_alert_types': valid_alert_types,
    })
