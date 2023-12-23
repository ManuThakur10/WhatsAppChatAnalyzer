import re
import pandas as pd


def preprocess(data):
    pattern = '\[\d{1,2}/\d{1,2}/\d{2},\s\d{1,2}:\d{1,2}:\d{2}\s(?:AM|PM)\]\s'
    messages = re.split(pattern, data)[1:]
    dates = re.findall(pattern, data)

    df = pd.DataFrame({'user_message': messages, 'message_date': dates})
    # convert to datetime
    df['message_date'].replace('\u202f', '')
    df['user_message'] = df['user_message'].replace(to_replace=r'\u202f', value='', regex=True)
    df['user_message'] = df['user_message'].replace(to_replace=r'\u200e', value='', regex=True)
    df['message_date'] = pd.to_datetime(df['message_date'], format='[%m/%d/%y, %I:%M:%S %p] ')
    # The space at the end was causing an error that took awhile to debug!
    df.rename(columns={'message_date': 'date'}, inplace=True)
    df.head()

    users = []
    messages = []
    for message in df['user_message']:
        # entry = re.split('([\w\W]+?):\s', message)
        entry = re.split(r':\s*', message, 1)
            # modified to include image url (wasn't working with above approach)
            # new method works because whatsApp doesn't allow ':' in username, so
            # split ':' will always be the first ':'
        if entry[1:]:  # username
            users.append(entry[0])
            messages.append(entry[1])
        else:
            users.append('group_notification')
            messages.append(entry[0])
    df['user'] = users
    df['message'] = messages
    df.drop(columns=['user_message'], inplace=True)

    df['only_date'] = df['date'].dt.date
    df['year'] = df['date'].dt.year
    df['month_num'] = df['date'].dt.month
    df['month'] = df['date'].dt.month_name()
    df['day'] = df['date'].dt.day
    df['day_name'] = df['date'].dt.day_name()
    df['hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute

    period = []
    for hour in df[['day_name', 'hour']]['hour']:
        if hour == 23:
            period.append(str(hour) + "-" + str('00'))
        elif hour < 10:
            period.append(str('0') + str(hour) + "-" + str(hour + 1))
        else:
            period.append(str(hour) + "-" + str(hour + 1))

    df['period'] = period

    return df