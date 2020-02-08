""" This program retrieves features of tracks from a playlist using Spotify
    Official API, put results inside Pandas dataframes and then uses Seaborn
    for data visualization
"""
import spotipy
import pandas as pd
import matplotlib.pyplot as plot
import seaborn as sns
from spotipy import util
from spotipy.oauth2 import SpotifyClientCredentials
from matplotlib import style

API_LIMIT = 50 # Spotify API limit

cid = "xx" # Spotify id token
secret = "xx" # Spotify API secret token

# Create client
client_credentials_manager = SpotifyClientCredentials(client_id=cid, client_secret=secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# Improve Pandas display settings
pd.set_option("display.width", 800)
pd.set_option("display.max_columns", 50)

# Change Seaborn default settings
sns.set_context('talk')
style.use('ggplot')

username = 'xx'  # Spotify username
playlist_name = 'asia indie'  # playlist name

playlists_results = sp.user_playlists(username) # Get playlist
playlist_ids = [playlist['id'] for playlist in playlists_results['items']
                if playlist['name'] == playlist_name] # Get playlist id

if not playlist_ids:
    raise Exception("Playlist {} not found".format(playlist_name))

# Get tracks from playlist
tracks_results = sp.user_playlist(username, playlist_ids[0])

# Note that we only store name, id and popularity of the main artist
df_tracks = pd.DataFrame([[t["track"]["id"], t["track"]["name"], t["track"]["artists"][0]["id"],
                           t["track"]["artists"][0]["name"], t["track"]["album"]["name"], t["track"]["popularity"]]
                          for t in tracks_results['tracks']['items']],
                        columns=["id", "song_name", "artist_id", "artist_name", "album_name", "popularity"])

# Normalize popularity by scaling down by 100
df_tracks["popularity_norm"] = df_tracks["popularity"] / 100.


def _get_artists_df(sp, artist_ids):
    # A helper method to get artist's information with pagination (since API call limit is 50)
    artist_list = []

    while artist_ids:
        artists_results = sp.artists(artist_ids[:API_LIMIT])
        artist_list += [[t["id"], t["genres"], t["popularity"]] for t in artists_results["artists"]]

        artist_ids = artist_ids[API_LIMIT:] # to move on with the next 50 ids

    df_artists = pd.DataFrame(artist_list, columns=["artist_id", "artist_genres", "artist_popularity"])

    df_artists["artist_popularity_norm"] = df_artists["artist_popularity"] / 100.

    return df_artists


artist_ids = df_tracks["artist_id"].unique().tolist()
df_artists = _get_artists_df(sp, artist_ids)

def _get_features_df(sp, track_ids):
    # A helper method to get track's features with pagination and return a DataFrame

    feature_list = []
    while track_ids:
        features_results = sp.audio_features(track_ids[:API_LIMIT])

        feature_list += features_results

        track_ids = track_ids[API_LIMIT:]

    df_features = pd.DataFrame(feature_list)[["id", "analysis_url", "duration_ms", "acousticness", "danceability",
                                              "energy", "instrumentalness", "liveness", "loudness", "valence",
                                              "speechiness", "key", "mode", "tempo", "time_signature"]]
    # tempo is in range 24-200 normalize it to 0-176
    df_features["tempo_norm"] = (df_features["tempo"] - 24) / 176.

    return df_features

track_ids = df_tracks["id"].unique().tolist() # get rid of duplicates
df_features = _get_features_df(sp, track_ids) # get tracks's features

# Create a df for current playlist to include track features and artist info
df_cur = df_features.merge(df_tracks, on="id")
df_cur = df_cur.merge(df_artists, on="artist_id")

# Create a new column with full name of the song
df_cur["full_name"] = df_cur["artist_name"] + " -- " + df_cur["song_name"]

# Sort songs by popularity
df_cur.sort_values("popularity", inplace=True, ascending=False)

df_cur["time_signature"] = df_cur["time_signature"].astype(pd.api.types.CategoricalDtype(categories=[1, 2, 3, 4, 5]))
df_cur["key"] = df_cur["key"].astype(pd.api.types.CategoricalDtype(categories=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]))


"""Create distplot, countplot, boxplot charts using Seaborn"""
def _distribution_plot(df, key, label, x_limits):
    ax = sns.distplot(df[[key]], bins=30, label=label)
    if x_limits is not None:
        ax.set_xlim(*x_limits)
    plot.title(key)
    plot.legend()
    plot.show()

x_limits = {"duration_ms": None, "loudness": (-60, 0), "tempo": (24, 200), "popularity": (0, 100),
            "artist_popularity": (0, 100)}

for key in ["duration_ms", "acousticness", "danceability", "energy", "instrumentalness", "liveness",
                    "loudness", "valence", "speechiness", "tempo", "popularity", "artist_popularity"]:
    _distribution_plot(df_cur, key, label="My Indie Playlist", x_limits=x_limits.get(key, (0, 1)))


def _countplot(df, key, label):
    ax = sns.countplot(data=df, x=key, palette="tab20")
    ax.set_title(label)
    plot.show()

for key in ["key", "time_signature", "mode"]:
    _countplot(df_cur, key, label="My Indie Playlist")


ax = sns.boxplot(data=df_cur[["acousticness", "danceability", "energy", "instrumentalness", "liveness",
                              "valence", "speechiness", "artist_popularity_norm", "popularity_norm", "tempo_norm"]])
ax.set_title("My Indie Playlist")
plot.show()

""" Get 1000 tracks of my favorite genres from Spotify API to later compare audio features"""
number_of_tracks = 1000
genres = {"vietnamese hip hop", "k-indie"} # my favorite genres

search_runs = int(number_of_tracks / API_LIMIT) # number of times API is called

search_list = []
for i in range(search_runs):
    for genre in genres:
        search_results = sp.search('genre:"{}"'.format(genre), type="track", limit=API_LIMIT, offset=API_LIMIT*i)

        search_list += [[t["id"], t["name"], t["artists"][0]["id"], t["artists"][0]["name"],
                            t["album"]["name"], t["popularity"]]
                           for t in search_results['tracks']['items']]

df_search = pd.DataFrame(search_list,
                         columns=["id", "song_name", "artist_id", "artist_name", "album_name", "popularity"])
df_search["popularity_norm"] = df_search["popularity"] / 100 # normalize popularity
track_ids = df_search["id"].unique().tolist() # get unique track ids
df_features = _get_features_df(sp, track_ids) # get songs' features
artist_ids = df_search["artist_id"].unique().tolist() # get unique artist ids
df_artists = _get_artists_df(sp, artist_ids) # get artist info

df_sample = df_features.merge(df_search, on="id")
df_sample = df_sample.merge(df_artists, on="artist_id")
df_sample["full_name"] = df_sample["artist_name"] + " -- " + df_sample["song_name"]
df_sample.sort_values("popularity", inplace=True, ascending=False) # sort by song popularity

# Convert time_signature and key to category
df_sample["time_signature"] = df_sample["time_signature"].astype(pd.api.types.CategoricalDtype(categories=[1, 2, 3, 4, 5]))
df_sample["key"] = df_sample["key"].astype(pd.api.types.CategoricalDtype(categories=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]))


# Repeat the same plot analysis on both my playlist and the Indie Playlist sample from Spotify
def _distplot2(df, df_other, key, labels, x_limits):
    ax = sns.distplot(df[[key]], bins=30, label=labels[0])
    if x_limits is not None:
        ax.set_xlim(*x_limits)
    ax = sns.distplot(df_other[[key]], bins=30, label=labels[1])
    if x_limits is not None:
        ax.set_xlim(*x_limits)
    plot.title(key)
    plot.legend()
    plot.show()

def _countplot2(df, df_other, key, labels):
    fig, ax = plot.subplots(1, 2)
    sns.countplot(data=df, x=key, ax=ax[0], palette="tab20")
    ax[0].set_title(labels[0])
    sns.countplot(data=df_other, x=key, ax=ax[1], palette="tab20")
    ax[1].set_title(labels[1])
    plot.show()

for key in ["duration_ms", "acousticness", "danceability", "energy", "instrumentalness", "liveness",
            "loudness", "valence", "speechiness", "tempo", "popularity", "artist_popularity"]:
    _distplot2(df_cur, df_sample, key,
              labels = ["My Indie Playlist", "1000 Indie rock songs"],
              x_limits = x_limits.get(key, (0, 1)))

for key in ["key", "time_signature", "mode"]:
    _countplot2(df_cur, df_sample, key, labels=["My Indie Playlist", "1000 Indie songs"])

fig, ax = plot.subplots(2, 1)
sns.boxplot(data=df_cur[["acousticness", "danceability", "energy", "instrumentalness", "liveness",
                         "valence", "speechiness", "artist_popularity_norm", "popularity_norm",
                         "tempo_norm"]], ax=ax[0])
ax[0].set_title("My Indie Playlist")
sns.boxplot(data=df_sample[["acousticness", "danceability", "energy", "instrumentalness", "liveness",
                           "valence", "speechiness", "artist_popularity_norm", "popularity_norm",
                           "tempo_norm"]], ax=ax[1])
ax[1].set_title("1000 Indie songs")
plot.show()
