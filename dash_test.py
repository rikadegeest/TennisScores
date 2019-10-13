#%%
# Data handling
import pandas as pd
import numpy as np

#import match data
matches = pd.read_csv("matches.csv") 

# Prepare the data
players = pd.DataFrame(index = (matches.loc[:,'home_team_player_1':'away_team_player_2'].melt().value.unique()))
players['matches_played'] = matches.loc[:,'home_team_player_1':'away_team_player_2'].melt()['value'].value_counts()
players['matches_won'] = matches.loc[:,['player1_won', 'player2_won']].melt()['value'].value_counts()
players['percentage_won'] = round(players['matches_won'] / players['matches_played'] * 100, 2)
#drops random empty row
players = players.dropna(how='all')
#fill in 0 when no matches were won
players = players.fillna(0)
players.sort_values(by=['percentage_won'], ascending=False)

#%%
# Bokeh libraries
from bokeh.io import output_file, output_notebook
from bokeh.plotting import figure, show, reset_output
from bokeh.models import ColumnDataSource
from bokeh.layouts import row, column, gridplot
from bokeh.models.widgets import Tabs, Panel, DataTable, TableColumn

# Determine where the visualization will be rendered
#output_file('filename.html')  # Render to static HTML, or 
# Render inline in a Jupyter Notebook
output_notebook()  

#create ColumnDatSourse objects
source = ColumnDataSource(players)


#format the tooltip
tooltip = [
            ('Player','@index'),
            ('Percentage won', '@percentage_won')
]

# Set up the figure(s)
fig = figure(plot_height=300, plot_width=300,
            title='Matches played vs matches won',
            x_axis_label='matches played', y_axis_label='matches won',
            x_range=(0, max(players['matches_played']) + 2), y_range=(0,max(players['matches_won']) + 2),
            toolbar_location=None, tooltips=tooltip)

            
# Draw the coordinates as circles
fig.circle(x='matches_played', y='matches_won',
           color='green', size=10, alpha=0.5, source=source)

#setup table columns
columns = [
            TableColumn(field='index', title='Player'),
            TableColumn(field='matches_played', title='Matches played'),
            TableColumn(field='matches_won', title='Matches won'),
            TableColumn(field='percentage_won', title='Percentage won')
]

match_stats_table = DataTable(source=source, columns=columns, index_position=None, height=150)

# Preview and save 
show(fig)  # See what I made, and save if I like it
show(match_stats_table)
#reset output
#reset_output()



#%%
