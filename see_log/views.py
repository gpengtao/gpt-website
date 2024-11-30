import sqlite3
from django.shortcuts import render


# Create your views here.

def query_log(request, app_name):
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
          and strftime('%Y-%m-%d %H:%M:%S', datetime(`time` / 1000, 'unixepoch', '+8 hour')) >= datetime('now', '-1 day', 'start of day')
          and (Content not like '%from netty client%')
          and (Content not like '%urls to invokers error%')
          and (Content not like '%securityTest-authTest%')
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

    return render(request, 'see_log/log_table.html', {
        'data': data,
        'app_name': app_name
    })
