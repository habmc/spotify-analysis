# Analyzing Playlist Tracks

In this project, I used Spotify Official APIs to analyze my playlist with the goals of gaining insights into
my own music preference through audio analysis and hopefully finding some new songs I could tune in.


## Why?
I have a playlist on Spotify which includes all my favorite Asian Indie songs. The playlist is made of 52 songs that I have repeatedly listened to in recent months. And as always, I'm kind of getting bored of them right now. That's why I decided to analyze the audios in my playlist using Spotify APIs with the hope of understanding more about my preference -- what kind of audio features I am looking for specifically, how long a song should be, etc. 

## How?
First, I called the Spotify APIs to get my playlist id, all the tracks in it with basic details such as track name, artist name and id, album name and track popularity.

After that, I made another API call to get more details about the artists in my list such as genres and popularity.

Finally I called the API to get detailed features of my tracks:

- acousticness: a confidence measure from 0.0 to 1.0 of whether the track is acoustic. 1.0 represents high confidence the track is acoustic.

- danceability: how suitable a track is for dancing based on a combination of musical elements including tempo, rhythm stability, beat strength, and overall regularity. A value of 0.0 is least danceable and 1.0 is most danceable.

- duration_ms: duration of the track in milliseconds.

- energy: a measure from 0.0 to 1.0 that represents a perceptual measure of intensity and activity. Typically, energetic tracks feel fast, loud, and noisy. For example, death metal has high energy, while a Bach prelude scores low on the scale. Perceptual features contributing to this attribute include dynamic range, perceived loudness, timbre, onset rate, and general entropy.

- instrumentalness: predicts whether a track contains no vocals. The closer the instrumentalness value is to 1.0, the greater likelihood the track contains no vocal content. Values above 0.5 are intended to represent instrumental tracks, but confidence is higher as the value approaches 1.0.

- key: the key the track is in. Integers map to pitches using standard Pitch Class notation . E.g. 0 = C, 1 = C♯/D♭, 2 = D, and so on.

- liveness: detects the presence of an audience in the recording. Higher liveness values represent an increased probability that the track was performed live. A value above 0.8 provides strong likelihood that the track is live.

- loudness: the overall loudness of a track in decibels (dB). Values typical range between -60 and 0 db.

- mode: indicates the modality (major or minor) of a track, the type of scale from which its melodic content is derived. Major is represented by 1 and minor is 0.

- speechiness: detects the presence of spoken words in a track. The more exclusively speech-like the recording (e.g. talk show, audio book, poetry), the closer to 1.0 the attribute value. alues above 0.66 describe tracks that are probably made entirely of spoken words. Values between 0.33 and 0.66 describe tracks that may contain both music and speech, either in sections or layered, including such cases as rap music. Values below 0.33 most likely represent music and other non-speech-like tracks.

- tempo: overall estimated tempo of a track in beats per minute (BPM).

- time_signature: stimated overall time signature of a track. The time signature (meter) is a notational convention to specify how many beats are in each bar (or measure).

- valence: a measure from 0.0 to 1.0 describing the musical positiveness conveyed by a track. Tracks with high valence sound more positive (e.g. happy, cheerful, euphoric), while tracks with low valence sound more negative (e.g. sad, depressed, angry).

All these details were then stored inside different Pandas dataframes and later merged into one single dataframe to simplify the analyzing process.

## What I found out
<p float="left">
  <img src="/images/track_acousticness.png" width="400" />
  <img src="/images/track_danceability.png" width="400" /> 
</p>
<p float="left">
  <img src="/images/track_duration.png" width="400" />
  <img src="/images/track_energy.png" width="400" /> 
</p>
<p float="left">
  <img src="/images/track_instrumentalness.png" width="400" />
  <img src="/images/track_key.png" width="400" /> 
</p>
<p float="left">
  <img src="/images/track_mode.png" width="400" />
  <img src="/images/track_speechiness.png" width="400" /> 
</p>
<p float="left">
  <img src="/images/track_tempo.png" width="400" />
  <img src="/images/track_time_signature.png" width="400" /> 
</p>
<p float="left">
  <img src="/images/track_valence.png" width="400" />
</p>

From these graphs, it is easy to recognize that I tend to prefer songs with low instrumentalness/speechness/liveness, medium tempo, medium-to-high danceability and duration of 220 seconds. Song popularity and artist popularity span on a pretty wide range, which means that I do not really have preference regarding these. Valence is mainly distributed at around 0.4, suggesting that I listen to both cheerful and sad songs. It might suggest I prefer listening to sad songs a bit, but we don't know since the sample size is apparently not large enough. The result might be more accurate if you try to run the program with a bigger playlist, so try it!

Now let's compare my playlist with a sample Spotify playlist of the same genres:

<p float="left">
  <img src="/images/acousticness_comparison.png" width="450" />
  <img src="/images/artist_comparison.png" width="400" />
</p>
<p float="left">
  <img src="/images/time_signature_comparison.png" width="450" />
  <img src="/images/danceability_comparison.png" width="400" />
</p>
<p float="left">
  <img src="/images/duration_comparison.png" width="450" />
  <img src="/images/energy_comparison.png" width="400" />
</p>
<p float="left">
  <img src="/images/instrumentalness_comparison.png" width="450" />
  <img src="/images/key_comparison.png" width="400" />
</p>
<p float="left">
  <img src="/images/liveness_comparison.png" width="450" />
  <img src="/images/loudness_comparison.png" width="400" />
</p>
<p float="left">
  <img src="/images/mode_comparison.png" width="450" />
  <img src="/images/speechiness_comparison.png" width="400" />
</p>
<p float="left">
  <img src="/images/tempo_comparison.png" width="450" />
  <img src="/images/valence_comparison.png" width="400" />
</p>

The graphs show that my playlist differs from the 1000 Indie songs in these aspects:

- I like songs with slightly higher acousticness/speechiness/loudness/artist popularity

- I like songs with relatively lower danceablilty/tempo/valence

- I prefer songs in key (1, 4, 5) and like songs in key (2, 11) least

After gaining some insights into my own music preferences, I applied the filters below to the 1000 songs dataframes in order to keep only tracks that I potentially like:

- 0.4 <= danceability <= 0.8

- duration between 10% quartile of original playlist duration and 90% quartile
- instrumentalness <= 0.1
- key in (1,4,5,6,8,10)
- 80 <= tempo <= 110
- 0.3 <= valence <= 0.5

After running this code, I got a dataframe of 197 tracks. I then again used Spotipy to create a new Spotify playlist called "Asia Indie Trial" from these 197 tracks.


  <img src="/images/result.png"/>
  
## WHAT NEXT?

- Listen to the generated playlist and keep track of how many suits my taste.

- Run the same analysis on the generated playlist and see how it's similar to/ different from the original playlist.

- Find friends who major in Music and ask them to help me improve my recommendation's accuracy by taking advantage of Spotify Audio Analysis endpoints (which provides more in-depth analysis of audios like tatum, time intervals of beats/bars, audio sections, etc).

- Take ML courses and see how I can cluster my tracks?
