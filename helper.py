from urlextract import URLExtract
extract = URLExtract()
import pandas as pd
from collections import Counter
import emoji

from wordcloud import WordCloud

def fetch_stats(selected_user, df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
        # fetches all rows with 'user' == selected user (selects all that satisfy boolean) and
        # retrieves its shape to see how many of those rows there are (# of messages)

    num_messages = df.shape[0]
    words = []
    for message in df['message']:
        words.extend(message.split())

    # fetch # of media messages:
    num_media_msg = df[df['message'].str.contains('video omitted')].shape[0] \
                    + df[df['message'].str.contains('image omitted')].shape[0] \
                    + df[df['message'].str.contains('.jpg')].shape[0]
    # .contains() doesn't work on a column BUT str.contains() does!

    links = []
    for message in df['message']:
        links.extend(extract.find_urls(message))

    return num_messages, len(words), num_media_msg, len(links)

def most_busy_users(df):
    x = df['user'].value_counts().head()
    df = round((df['user'].value_counts()/df.shape[0])*100, 2).reset_index().rename(
        columns={'user':'name', 'count':'percent'})
        # gives percentages of message per user
    return x, df

def create_wordcloud(selected_user, df):

    f = open('stop_hinglishAndPunctuation.txt', 'r')
    stop_words = f.read()

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
        groupName = ""
        # if user is picked, set groupName to an impossible value (nothing needs to be removed from the
        # sliced dataset, as it only contains messages from selected user)
    else:
        groupName = df['user'][0]

    temp = df[df['user'] != groupName]
    temp = remove_media(temp)

    def remove_stop_words(message):
        y = []
        for word in message.lower().split():
            if word not in stop_words:
                y.append(word)
        return " ".join(y)


    wc = WordCloud(width=500, height=500, min_font_size=10, background_color='white')
    temp['message'] = temp['message'].apply(remove_stop_words)
    df_wo_media = remove_media(temp)
    messages_wo_media = df_wo_media['message']
    # slice of another df retains same column names!
    df_wc = wc.generate(messages_wo_media.astype(str).str.cat(sep=""))
    # every message casted as a string (default type is 'mixed-integer')
    return df_wc

def remove_media(df):
    return df[~(df['message'].str.contains('video omitted')
                       | df['message'].str.contains('image omitted')
                       | df['message'].str.contains('.jpg'))]

def most_common_words(selected_user, df):

    f = open('stop_hinglishAndPunctuation.txt', 'r')
    stop_words = f.read()

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
        groupName = ""
        # if user is picked, set groupName to an impossible value (nothing needs to be removed from the
        # sliced dataset, as it only contains messages from selected user)
    else:
        groupName = df['user'][0]

    temp = df[df['user'] != groupName]
    temp = remove_media(temp)

    words = []
    for message in temp['message']:
        for word in message.lower().split():
            if word not in stop_words:
                words.append(word)

    most_common_df = pd.DataFrame(Counter(words).most_common(20))
    return most_common_df

def emoji_helper(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    emojis = []
    for message in df['message']:
        emojis.extend([c for c in message if c in emoji.EMOJI_DATA])
        # this version works!

    emoji_df = pd.DataFrame(Counter(emojis).most_common(len(Counter(emojis))))
    return emoji_df

def monthly_timeline(selected_user, df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    timeline = df.groupby(['year', 'month_num', 'month']).count()['message'].reset_index()

    time = []
    for i in range(timeline.shape[0]):
        time.append(timeline['month'][i] + " " + str(timeline['year'][i]))

    timeline['time'] = time

    return timeline

def daily_timeline(selected_user, df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    daily_timeline = df.groupby('only_date').count()['message'].reset_index()
    return daily_timeline

def week_activity_map(selected_user, df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df['day_name'].value_counts()

def month_activity_map(selected_user, df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df['month'].value_counts()

def activity_heatmap(selected_user, df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    act_heatmap = df.pivot_table(index='day_name', columns='period', values='message', aggfunc='count').fillna(0)
    act_heatmap = act_heatmap.sort_index()
    return act_heatmap