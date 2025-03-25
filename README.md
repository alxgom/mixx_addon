#  MIXXX Dj software dashboard companion.

It is meant to complement my use of MIXXX as a tool for DJ-ing at swing and blues social dance events, as a ways to explore and analyze my library and my sets, and reflect on my choices and posibly give me new ideas to explore.
Eventually It could I would like to turn it into a built in add-on or a fork of MIXXX for social dance Djs. 

This program uses SQlite and Dash to generate a dashboard from a query of "mixxxdb.sqlite", a file that contains the metadata of my MIXXX library and playlists. 
The dashboard relies on my workflow, where I save the sets I played as playlists with a date and a short description of the event

![image](https://github.com/user-attachments/assets/729a3003-49dd-4fc8-b424-298464f3e12b)

## Example:

  
![image](https://github.com/user-attachments/assets/0502b100-2a16-416c-a13b-0ede16a1c6fb)




The dashboad consists on four tabs: 
- Agregate playlists: Aggregate metadata from past sets. Let's me see which artists I been playing most, which I haven't played, and other information. 
 
 - Crates: Analysis of my crates classification system (To be implemented)

- Individual Playlist: Analysis of individual sets. Which songs I played, in what order, bpm succession, etc. 

- Library: Meta analysis of my whole library. How many songs do I have, how I rate them, how many artists...

### Future ideas: 
- Use some AI tool to parse the web and enhance my data. For example, using online data to find the players of each ensemble. First date of publication of the song. Classify songs into Big band, or small ensembles; legacy artists or modern artists, etc...  
