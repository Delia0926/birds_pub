"""
Project Introduction:
As a bird-watcher, the project focuses on giving potential bird enthusiasts an overall view of species of birds found in Alberta and explore bird behaviour through the observation datasets we’ve acquired. 
This includes the exploration of common vs. rare birds, habitat locations of certain species, and how bird presence changes overtime –– both seasonally and throughout recent decades. 
co-workers: Jesse[main contributor], Anna, Val, Delia, Yichen
"""

"""
Part I: Preparing for Sources
"""
# Create Reusable Function
import os
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter, StrMethodFormatter

#Function to plot species counts or count groups, zoomed Out.
def plotCountsZoomedOut(counts, highlighted=None, title=None, saveas=None):
    highlight_index = None if highlighted == None else counts.index.get_loc(highlighted)

    fig, ax=plt.subplots()
    ax.yaxis.set_major_formatter(StrMethodFormatter("{x:,.0f}"))

    plt.bar(counts.index, counts)

    if highlighted != None:
        plt.bar(highlighted, counts[highlighted])

    plt.margins(x=0.03)
    plt.title(title)
    plt.xticks(rotation = 90, fontsize=7, color="lightgray" if highlighted !=None else "black")
    plt.ylabel("Counts")

    if highlighted !=None:
        plt.gca().get_xticklabels()[highlight_index].set_color("black")

    if saveas !=None:
        plt.savefig(os.path.join("/Users/delia/Desktop/Project-Python", saveas), bbox_inches="tight")

    plt.show()

    # Function to plot species counts or count groups, zoomed In    .
def plotCountsZoomedIn(counts, highlighted, title, saveas=None):
  highlight_index = counts.index.get_loc(highlighted)

  fig, ax=plt.subplots()
  ax.xaxis.set_major_formatter(StrMethodFormatter("{x:,.0f}"))

  zoomed_groups = None

# Slice this depending on the size/position of the highlight item.
  if counts.size <= 15:
    zoomed_groups = counts
  elif highlight_index - 7 < 0:
    zoomed_groups = counts[:15]
  elif highlight_index + 8 > counts.size:
    zoomed_groups = counts[-15:]
  else:
    zoomed_groups = counts[highlight_index - 7: highlight_index + 8]
  zoomed_index = zoomed_groups.index.get_loc(highlighted)

  plt.barh(zoomed_groups.index, zoomed_groups)
  plt.barh(highlighted, zoomed_groups[highlighted])
  plt.title(title)
  plt.yticks(color="gray")
  plt.xlabel("Count")

  plt.gca().get_yticklabels()[zoomed_index].set_color("black")

  if saveas != None:
    plt.savefig(os.path.join("/Users/delia/Desktop/Project-Python", saveas), bbox_inches="tight")

  plt.show()

# Pick one species to have a deeper analysis
highlight_species, plot_color = "Euphagus carolinus", "rebeccapurple" #Rusty Blackbird

"""
Part II: Import and Wrangle the Data
"""
import pandas as pd
observations = pd.read_csv("/Users/delia/Desktop/Project-Python/eBird Data - 2022-01 to 2022-12.csv",
                         usecols=["COMMON NAME", "SCIENTIFIC NAME", "OBSERVATION DATE", "LATITUDE", "LONGITUDE"])
taxonomy = pd.read_csv("/Users/delia/Desktop/Project-Python/ebird_taxonomy_v2022.csv",
                       usecols = ["PRIMARY_COM_NAME", "SCI_NAME", "SPECIES_GROUP"])

highlight_group = taxonomy.loc[taxonomy["SCI_NAME"] == highlight_species, "SPECIES_GROUP"].item()
highlight_common_name = taxonomy.loc[taxonomy["SCI_NAME"] == highlight_species, "PRIMARY_COM_NAME"].item()
ebird = pd.merge(
    observations,
    taxonomy,
    left_on=["SCIENTIFIC NAME"],
    right_on=["SCI_NAME"]
).drop(columns=["SCI_NAME","PRIMARY_COM_NAME"])

ebird=ebird.rename(columns={"SPECIES_GROUP":"SPECIES GROUP"})
ebird["OBSERVATION DATE"]=pd.to_datetime(ebird["OBSERVATION DATE"])

"""
Part III: Data Visualization - Plots
"""
#Observation Counts by Species and Group
group_counts = ebird.groupby("SPECIES GROUP").size()
group_counts = group_counts.sort_values()

plotCountsZoomedOut(group_counts, title = "2022 Observation Count by Species Group",
                    saveas="2022 obs Counts - All Species Groups.jpg")


plotCountsZoomedOut(group_counts, highlight_group, title="2022 Observation Count by Species Group",
                    saveas=f"2022 Obs Counts - {highlight_common_name} - Species Groups.jpg")

plotCountsZoomedIn(group_counts, highlight_group, title="2022 Obs Count by Species Group - Zoomed IN",
                   saveas=f"2022 obs Counts - {highlight_common_name} - Species Groups - Zoomed IN.jpg")

species_counts = ebird[ebird["SPECIES GROUP"] == highlight_group].groupby("COMMON NAME").size()
species_counts = species_counts.sort_values()

if species_counts.size > 15:
    plotCountsZoomedOut(species_counts,highlight_common_name, title = f"2022 Obs Counts\n({highlight_group})",
                        saveas=f"2022 obs Counts - {highlight_common_name}.jpg")

plotCountsZoomedIn(species_counts, highlight_common_name, title = f"2022 obs Counts\n({highlight_group})",
                   saveas=f"2022 obs Counts - {highlight_common_name}.jpg")

#Daily Observation
all_dates = pd.Series(index=pd.date_range("2022-01-01", "2022-12-31"), dtype="float64").fillna(0)

daily_counts = all_dates + ebird[ebird["SCIENTIFIC NAME"] == highlight_species].groupby("OBSERVATION DATE").size()
daily_counts_ra = pd.Series(daily_counts).rolling(window=14, min_periods=1).mean().fillna(0)

import matplotlib.dates as mdates

fig, ax = plt.subplots()
ax.yaxis.set_major_formatter(StrMethodFormatter("{x:,.0f}"))

plt.margins(0.01)
plt.bar(daily_counts.index, daily_counts, width=1.0, alpha=0.2, color=(plot_color or "royalblue"))
plt.plot(daily_counts_ra.index, daily_counts_ra, color=(plot_color or "royalblue"))
plt.xticks(rotation=0)
plt.ylabel("Daily Observations")

plt.xlim(ebird["OBSERVATION DATE"].min(), ebird["OBSERVATION DATE"].max())
if daily_counts.max() < 10:
  plt.ylim(0, 10)

plt.title(f"Daily Observations + 14-Day Rolling Average\n{highlight_common_name} ({highlight_species})")

ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(ax.xaxis.get_major_locator()))

plt.savefig(os.path.join("/Users/delia/Desktop/Project-Python",
            f"Daily Observation Counts - {highlight_common_name}.jpg"),bbox_inches="tight")

plt.show()

#Maps
import plotly.offline as py
import plotly.graph_objs as go

mapbox_token_file = "/Users/delia/Desktop/Project-Python/mapbox.token"

if not os.path.isfile(mapbox_token_file):
    raise Exception ("Missing token file: '/Users/delia/Desktop/Project-Python/mapbox.token'.")

file = open(mapbox_token_file)
for line in file:
    token = line.rstrip()
file.close()

species_observations = ebird[ebird["SCIENTIFIC NAME"] == highlight_species]

data = [
    go.Scattermapbox(
        lat = species_observations["LATITUDE"],
        lon = species_observations["LONGITUDE"],
        mode = "markers",
        marker = dict(
            size = 7,
            color = (plot_color),
            opacity = 0.5
        ),
        text = species_observations["OBSERVATION DATE"].tolist()
    )
]

layout = go.Layout(
    title = f"2022 Observations of {highlight_common_name} ({highlight_species})",
    autosize = True,
    height = 900,
    width = 700,
    hovermode = "closest",
    mapbox = dict(
        style = "light",
        accesstoken = token,
        bearing = 0,
        center = dict(
            lat = 54.9,
            lon = -115
        ),
        pitch = 0,
        zoom = 4,
    ),
)

fig = dict(data = data, layout = layout)
py.iplot(fig)


#Historical Annual Trend
history_filename = os.path.join("/Users/delia/Desktop/Project-Python", f"eBird Data - {highlight_common_name} - All Dates.csv")

if not os.path.isfile(history_filename):
    ebird_source = pd.read_csv("/Users/delia/Desktop/Project-Python/ebd_CA-AB_smp_relAug-2023.txt", delimiter="\t", chunksize=10_000)

    header_written = False
    for i, chunk in enumerate(ebird_source):
        historical_piece = chunk[chunk["SCIENTIFIC NAME"] == highlight_species]

        if historical_piece.size > 0:
            if i == 0:
                historical_piece.to_csv(history_filename, header=(not header_written), mode="a", index=False)
                header_written = True
            else:
                historical_piece.to_csv(history_filename, header=False, mode="a", index=False)

historical = pd.read_csv(history_filename, usecols=["OBSERVATION DATE"])
historical["OBSERVATION DATE"] = pd.to_datetime(historical["OBSERVATION DATE"])
historical["YEAR"] = historical["OBSERVATION DATE"].dt.year

annual_counts = historical[(historical["YEAR"] >= 1970) & (historical["YEAR"] < 2023)].groupby("YEAR").size()
fig, ax = plt.subplots()
ax.yaxis.set_major_formatter(StrMethodFormatter("{x:,.0f}"))

plt.bar(annual_counts.index, annual_counts, color=(plot_color or "royalblue"))

plt.xlabel("Year")
plt.ylabel("Total Annual Observations")

if annual_counts.max() < 10:
  plt.ylim(0, 10)

plt.title(f"Historical Annual Observation Counts\n{highlight_common_name} ({highlight_species})")

plt.savefig(os.path.join("/Users/delia/Desktop/Project-Python",
                         f"Historical Annual Obs - {highlight_common_name}.jpg"), bbox_inches="tight")

plt.show()
