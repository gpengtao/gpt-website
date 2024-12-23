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


def get_app_name(content, alert_type):
    """根据告警类型和内容提取应用名称"""
    try:
        if alert_type == '应用报警':
            start = content.index('应用:') + len('应用:')
            end = content.index('指标:', start)
            return content[start:end].strip()
        elif alert_type == 'delta告警':
            start = content.index('描述:') + len('描述:')
            end = content.index('[target]', start)
            return content[start:end].strip()
        elif alert_type == 'job调度':
            start = content.index('作业：') + len('作业：')
            end = content.index('类型：', start)
            return content[start:end].strip()
    except ValueError:
        return None
    return None


def create_alert(datetime, content):
    """创建告警对象"""
    alert_type = get_alert_type(content)
    return {
        'datetime': datetime,
        'content': content,
        'alert_type': alert_type,
        'app_name': get_app_name(content, alert_type)
    }


def split_alerts(datetime, content):
    """拆分合并的告警内容"""
    alerts = []
    
    # 定义分隔标记
    markers = ['【OPS提醒】', '【OPS告警】']
    
    # 找到所有分隔位置
    positions = []
    for marker in markers:
        start = 0
        while True:
            pos = content.find(marker, start)
            if pos == -1:
                break
            positions.append(pos)
            start = pos + 1
    
    # 如果没有找到分隔符或只有一个，直接返回原内容
    if len(positions) <= 1:
        return [create_alert(datetime, content)]
    
    # 按位置排序
    positions.sort()
    
    # 根据位置拆分内容
    for i in range(len(positions)):
        start = positions[i]
        end = positions[i + 1] if i + 1 < len(positions) else len(content)
        alert_content = content[start:end].strip()
        if alert_content:
            alerts.append(create_alert(datetime, alert_content))
    
    return alerts


def calculate_app_name_stats(alerts):
    """计算应用名称统计信息"""
    app_name_count = {}
    
    # 统计应用名称出现次数
    for alert in alerts:
        if alert['app_name']:
            app_name_count[alert['app_name']] = app_name_count.get(alert['app_name'], 0) + 1
    
    # 将应用名称按数量排序
    app_name_stats = [
        {'name': name, 'count': count}
        for name, count in app_name_count.items()
        if name  # 过滤掉None值
    ]
    app_name_stats.sort(key=lambda x: (-x['count'], x['name']))  # 按数量降序，名称升序
    
    return app_name_stats


def ivr_logs(request):
    # 获取时间范围参数，默认为100小时
    hours = request.GET.get('hours', '100')
    # 确保hours是有效的选项
    valid_hours = ['24', '48', '72', '100', '168']  # 24小时、48小时、72小时、100小时、7天
    hours = hours if hours in valid_hours else '100'

    # 获取搜索参数
    keyword = request.GET.get('keyword', '').strip()
    alert_type = request.GET.get('alert_type', '').strip()
    app_name = request.GET.get('app_name', '').strip()

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
    ivr_logs = []
    for row in results:
        # 拆分合并的告警
        alerts = split_alerts(row[0], row[1])
        ivr_logs.extend(alerts)

    # 计算应用名称统计信息（在过滤之前计算，这样显示的是所有告警中的应用分布）
    app_name_stats = calculate_app_name_stats(ivr_logs)

    # 如果指定了告警类型，进行过滤
    if alert_type:
        ivr_logs = [log for log in ivr_logs if log['alert_type'] == alert_type]

    # 如果指定了应用名称，进行过滤
    if app_name:
        ivr_logs = [log for log in ivr_logs if log['app_name'] == app_name]

    valid_alert_types = ['应用报警', 'delta告警', 'job调度']

    return render(request, 'see_log/ivr_logs.html', {
        'ivr_logs': ivr_logs,
        'hours': hours,
        'valid_hours': valid_hours,
        'keyword': keyword,
        'alert_type': alert_type,
        'valid_alert_types': valid_alert_types,
        'app_name': app_name,
        'app_name_stats': app_name_stats,
    })


def see_log_home(request):
    """see_log首页"""
    return render(request, 'see_log/home.html')
