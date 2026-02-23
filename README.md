# Mixxx DJ Dashboard Companion

A data visualization dashboard for [Mixxx](https://mixxx.org/), designed to help Swing and Blues DJs analyze their library, sets, and playing habits. It parses the Mixxx SQLite database to provide insights into played tracks, tempos, artists, and more.

It is meant to complement my use of Mixxx for social dance events, allowing me to reflect on my choices, rediscover forgotten tracks, and find new ideas for future sets.

![Dashboard Preview](https://github.com/user-attachments/assets/729a3003-49dd-4fc8-b424-298464f3e12b)

## How It Works

This application uses Python (Dash & Plotly) to query the `mixxxdb.sqlite` file, which contains all metadata for your Mixxx library and playlists.

The dashboard relies on a workflow where sets played are saved as playlists with a date and a short description of the event.

![Set Analysis](https://github.com/user-attachments/assets/0502b100-2a16-416c-a13b-0ede16a1c6fb)

## Features

The dashboard consists of four main sections:

### 1. Aggregate Playlists

Aggregate metadata from past sets to analyze trends over time.

- **Set Filtering**: Easily select sets by date, style (e.g., Blues vs. Lindy), or manually via a collapsible checklist.
- **Artist Stats**: See who you play the most and identify "one-hit wonders" vs. staples.
- **BPM Distribution**: Analyze the tempo range of your sets.
- **Song Repetition**: Track how often you repeat songs across different sets.

### 2. Individual Playlist

Deep dive into specific sets to analyze the flow of the night.

- **Track Sequence**: Visualize the order of songs played.
- **BPM flow**: View the tempo progression throughout the set.
- **Duration & Ratings**: Review track lengths and your own ratings.
- **Spotify Export**: Recreate your DJ sets as public Spotify playlists with a single click via OAuth integration.

### 3. Library Content

Meta-analysis of your entire music library.

- **Rating Distribution**: See how you've rated your collection.
- **BPM Overview**: Understand the tempo distribution of your whole library.

### 4. Crates (In Development)

Analysis of your crate classification system to help organize and audit your library structure.

## Live Demo

An online example with a subset of data can be found here:  
[**Live Dashboard**](https://dj-dashboard.onrender.com/)

## Future Roadmap

- **AI Metadata Enhancement**: Use external APIs or AI tools to enrich library data (e.g., finding original recording dates, identifying band members/personnel, classifying sub-genres like Big Band vs. Small Combo).
- **Advanced Crate Analysis**: More detailed insights into how tracks are organized.
