import sqlite3
import os

from django.shortcuts import render


# Create your views here.

def query_app_log(request, app_name):
    # 连接到SQLite数据库
    db_path = '/Users/pengtao.geng/Library/Application Support/btalk/databases/pengtao.geng.db'
    conn = sqlite3.connect(db_path)
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
            'id': row[0],
            'name': row[1],
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
    db_path = '/Users/pengtao.geng/Library/Application Support/btalk/databases/pengtao.geng.db'
    conn = sqlite3.connect(db_path)
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


def ivr_log(request):
    # 获取数据库路径（需要根据实际情况修改）
    db_path = '/Users/pengtao.geng/Library/Application Support/btalk/databases/pengtao.geng.db'

    # 连接数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 执行查询
    query = """
        SELECT
            strftime('%Y-%m-%d %H:%M:%S', datetime(`time` / 1000, 'unixepoch', '+8 hour')) AS datetime,
            Content as content
        FROM IM_Message
        WHERE "From" = 'rbt_delta_notify_ivr'
          AND time >= strftime('%s', 'now') * 72 - 100 * 60 * 60 * 1000
        ORDER BY time DESC
        limit 100
        """

    cursor.execute(query)
    results = cursor.fetchall()

    # 将结果转换为字典列表
    ivr_logs = [
        {
            'datetime': row[0],
            'content': row[1]
        }
        for row in results
    ]

    return render(request, 'see_log/ivr_log.html', {
        'ivr_logs': ivr_logs
    })
