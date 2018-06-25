
# coding: utf-8

# # Tutorial for the *CYCLUS* Fuel Cycle Simulator
# 
# [*CYCLUS*](http://fuelcycle.org/) is an open soruce fuel cycle simulator.  It is agent-based, and its user-customizable archetypes (called <font color='800000'>prototypes</font>) allow for more freedom in the fidelity, depth, and focus of the simulation.
# <br><br>
# This tutorial will begin with a simple exercise using Cycamore archetypes to familiarize the user with creating input files (in xml) and accessing data from the SQLite database output.  This tutorial is not an [exhaustive list](http://fuelcycle.org/user/index.html) of ways to do these things, but it should give new users a good starting point.

# ## Exercise 1:
# This first exercise will model a very simple scenario:
# -  There is a single uranium mine
# -  One enrichment facility producing UOX fuel
# -  One LWR, with a 1000 MWe capacity
# -  One repository, which takes SNF
# -  This is an open fuel cycle, there is no reprocessing or MOX fuel.
# 
# Throughout this tutorial, there will be cells of code mixed into the explanations.  Some of these will need information entered before they are run - a comment at the beginning of the cell will tell you.  If you are unfamiliar with Jupyter notebook, you can run a cell by selecting it, and using shift+enter or ctrl+enter (selected cells will have a blue or green line around them).  Please do not run all cells at once.

# ### Simulation: Control
# Let's begin by choosing our simulation parameters.
# 
# *CYCLUS* works in timesteps of 1 month by default.  At each time step, *CYCLUS* has phases in which each agent can take particular actions:
# -  <font color='800000'>Deployment</font>: New agents may enter the system
# -  Each agent prepares for material exchange
# -  The material trade occurs
# -  The agents act after the exchange
# -  <font color='800000'>Decommissioning</font>: Agents may leave the system
# <br><br>
# 
# 
# *CYCLUS* will manage these phases automatically, but the user must give:
# -  The duration (in months)
# -  The start month (e.g.: 1 for January)
# -  The start year
# -  Decay treatment:  'never' if all decay is turned off, 'manual', meaning it is only on if the individual archetype decays their own inventory, or 'lazy', which will compute decay only when archetypes fetch a particular composition.
# <br>
# There are other [optional parameters](http://fuelcycle.org/user/input_specs/control.html) that could be given, but these are the ones we will use during the tutorial.
# <br><br>
# For this exercise, the simuation will run for 50 years, or 600 months.  We'll model a system that starts in January, 2018.  Decay will be set to 'never' for now.

# In[1]:


# This cell requires user input.  Run it when you have entered everything.
import numpy as np
duration = 720
start_month = 1
start_year = 2018
decay = 'never'

simulation_parameters = [duration,start_month,start_year,decay]


# ### Archetypes:
# One of the features of *CYCLUS* is its ability to switch between different models of the facilities within the fuel cycle.  These models, called <font color='800000'>archetypes</font>, may change how the facility interacts with other facilities or how the physics of the facility are represented.
# <br><br>
# For example, reactor archetypes may change how they calculate their fresh and spent fuel compostions.  A very simple model might take fixed input and output recipes, and assume all material entering matches its input, and all material exiting matches its output.  A more complex model may tabulate reactor performance and physics parameters, and use interpolation to determine input and output recipes.  The most complex model could perform a full depletion calculation each time new fuel enters the reactor.
# <br><br>
# A simple set of archetypes have been created in [Cycamore](http://fuelcycle.org/user/cycamoreagents.html).  They are a good fit for simple tutorials, or for modeling facilities that are required, but not the focus of the simulation.  The Cycamore archetypes include:
# -  <font color='800000'>Source</font>: This is a generic source of fresh material.  This could cover a uranium mine, an enrichment facility, or even a fabrication facility, depending on how explicitly the user wants to model the front-end of the fuel cycle.
# -  <font color ='800000'>Enrichment</font>: This archetype uses the standard equations for enrichment of U-235, and has a limit on total enrichment capacity.
# -  <font color='800000'>Reactor</font>: This facility takes set input and output fuel recipes, and loads new assemblies at regular intervals.
# -  <font color='800000'>Separations</font>: This facility splits all the isotopes in its input stream into separate output streams.
# -  <font color='800000'>FuelFab</font>: This archetype uses the d-factor approach to mix streams of fissile and fissionable material and approximate a given recipe.
# -  <font color='800000'>Sink</font>:  This is a generic sink for any facility that will permanently hold nuclear material.  This could be an interim storage facility, a geological repository, or other long-term disposal methods a user may want to model.
# 
# When you customize or specify the details of an archetype, that is referred to as a <font color ='800000'>prototype</font>.

# ### Commodities:
# 
# *CYCLUS* models resource exchange through the use of the <font color='800000'>dynamic resource exchange</font>, or DRE.  A <font color='800000'>commodity</font> simply defines a resource that agents in the simulation may want to exchange with each other  For example, spent fuel would be a commodity that leaves a reactor facility, and then is "exchanged" with a repository to simulate its final disposal.  Defining a commodity gives no information about its composition - that is done be defining <font color='800000'>recipes</font>.

# ### A Note On Input Files:
# 
# There are multiple ways to create a *CYCLUS* input file.  This tutorial uses the jinja2 template library and .xml templates to create its input.  More detail will be given later, but for now, know that some parts of the archetypes (such as the name of the enrichment facility) are already included in the templates provided for the tutorial.  Beyond this lesson, it is possible to use or create other templates and tweak these "preloaded" details. 

# ### Creating recipes:
# 
# Whenever *CYCLUS* needs to know the composition of a material, it looks at the recipe for that material given in the input file.  Until now, "recipe" has been used to refer to fuel recipes, but the "recipe" section of the input file can include the recipe for natural uranium, spent fuel, fresh fuel, or any other material where the isotopic composition needs to be tracked.
# <br><br>
# First, we can declare the isotopic compostions of fresh and spent fuel.  We'll be using simple recipes: fresh fuel is 4.0% U-235 by mass, remainder U-238.  Spent fuel is 1.1% U-235, 94.0% U-238, 0.9% Pu-239, and 4.0% Cs-137.

# In[2]:


# This cell does not need user input, and you can run it now.

fresh_id = [92235,92238]
fresh_comp = [0.04, 0.96]

spent_id = [92235, 92238, 94239, 55137]
spent_comp = [0.011, 0.94, 0.009, 0.04]

import basics

# the function that will write the input takes in a dictionary for fresh and spent fuels, so
# below a function that will take the raw ID and composition data and put them in this format is called.
fresh,spent = basics.recipe_dict(fresh_id,fresh_comp,spent_id,spent_comp)

# we can look at these dictionaries to see how they are formatted:
print(fresh)
print(spent)


# The recipe for natural uranium has already been included in the template.

# ### Providing Reactor Data:
# 
# <font size='2'>Note: For the purposes of the tutorial, we'll input reactor information here in the notebook, then render it into a csv file and import it again.  Obviously, this isn't needed - we could directly input our reactor data and never bother with external files.  However, we're including this step to help new users who may be unfamiliar with python with one of many ways to import external data.</font>
# <br><br>
# 
# Exercise 1 models a single PWR.  It has a power capacity of 1000 MWe, and there is only one of them in the region.  Fill in the missing information.

# In[3]:


# This cell requires user input.  Run it when you have entered everything.

country = 'The Beehive'
reactor_name = 'Honeycomb3000'
type_reactor = 'PWR'
net_elec_capacity = 1000
operator = 'SeveralBees'


# In[4]:


# This cell does not need user input, and you can run it now.

if type_reactor != 'PWR':
    print('You gave a reactor type that was unexpected.  The tutorial will still run, '
          'but it will default to PWR conditions \n' + 'where necessary.  '
          'If you entered pwr instead of PWR, try capitalizing it.')

header = ['Country','Reactor Name','Type','Net Electric Capacity','Operator']
raw_input = [country,reactor_name,type_reactor,net_elec_capacity,operator]
filename = "tutorial_data.csv"

basics.write_csv(header,raw_input, filename)


# Within the reactor data, we gave how many reactors were initially deployed.  However, we still need to set how many mines, enrichment facilities, and repositories are in our region.  For now, we'll say that there is one of each facility in our region.

# In[5]:


# This cell requires user input.  Run it when you have entered everything.

n_mine = 1 
n_enrichment = 1
n_repository = 1


# ### Rendering the Input File:
# 
# In practice, your simulation may have more variables, and you may be pulling data from external databases.  But, for this tutorial, we are ready to render the main input file for *CYCLUS*.  At this point, it may be helpful to open the basics.py script, as a reference.<br>First, we'll import our "external data"  from a csv file with the information we gave earlier:

# In[6]:


# This cell does not need user input, and you can run it now.

reactor_data = basics.import_csv('test_data.csv')


# In[7]:


deployment_data = {}
for element in reactor_data.loc[:,'Country'].drop_duplicates():
    deployment_data[element] = [n_mine,n_enrichment,n_repository]
        
print(deployment_data)


# The input file is created in parts - it is common to have separate, smaller templates for the reactor, the recipes, and other blocks of the input file that require many variables.
# <br><br>
# Templates have been mentioned before this point, but haven't been shown.  Let's start by taking a look at the reactor template:

# In[8]:


# This cell does not need user input, and you can run it now.

with open('reactor_template_t.xml','r') as reactor:
    print(reactor.read())


# The facility and /facility subroots **(what is the right term here???)**  hold all the information about a specific prototype. There are facility blocks for each prototype made - the mine, the enrichment facility, and repository all have their own section within the main input, as well as sections for setting simulation parameters, and defining archetypes and commodities.
# <br><br>
# You may notice that some values had been replaced by something in {{ }}.  The template will recognize these as variables.  We can also take a look at the region, recipe, and main templates:

# In[9]:


with open('region_template_t.xml','r') as region:
    print(region.read())


# Within the region and recipe template, you will see {% for x,y in z.items() -%} ... {% endfor -%}.  These are for loops, and work similarly to for loops in other languages.  For each element in x,y (note that in both templates, we might more accurately say that the loops are {% for key, value in dicitionary.items() -%}, as in this specific instance, the input-rendering functions use dictionaries.) it copies whatever is between the {%-%} {% -%} brackets, and fills in the variables in the designated locations.

# In[10]:


with open('recipe_template_t.xml','r') as recipe:
    print(recipe.read())


# For example, in the recipe template above, the for loop in the fresh fuel recipe block will make a new nuclide block for each isotope in the fresh_fuel dicitionary.  To see this in action, we can simply render the recipe portion:

# In[11]:


rendered_recipe = basics.write_recipes(fresh,spent,'recipe_template_t.xml','1xn-rendered-recipe.xml')

with open(rendered_recipe,'r') as recipe:
    print(recipe.read())


# As you can see, within the fresh fuel recipe there are now two nuclide blocks, one for each isotope in the fresh dictionary we made earlier.<br><br>
# We can also look at the main input template.  In order to insert the already rendered parts into the main input file, it has {{variable}} sections where each section would go.  Then, in a fashion simiar to how the templates have been opened here in the notebook, the files are assigned to variables and inserted into the template.

# In[12]:


with open('main_input_t.xml','r') as main:
    print(main.read())
    
# this output is long:  To toggle showing this cell's output: press Esc to enter command mode, then press o to
# suppress output.  press o again in command mode to show it again.


# Now, let's actually create the input file.  The recipe portion was made earlier, so the only the reactor, region, and main input remains.

# In[13]:


rendered_reactor = basics.write_reactor(reactor_data, 'reactor_template_t.xml','1xn-rendered-reactor.xml')
with open(rendered_reactor,'r') as reactor:
    print(reactor.read())


# In[14]:


rendered_region = basics.write_region(reactor_data,deployment_data,'region_template_t.xml','1xn-rendered-region.xml')
with open(rendered_region,'r') as region:
    print(region.read())


# In[15]:


basics.write_main_input(simulation_parameters,rendered_reactor,rendered_region,rendered_recipe,
                 'main_input_t.xml','1xn-rendered-main-input.xml')
with open('1xn-rendered-main-input.xml','r') as maininput:
    print(maininput.read())


# It is possible to change some of the variables in this input file to suit user preference.  However, certain names used in one scetion must match the names used in others.  For reference, an image of an input file has been included below, with the parts that must match each other highlighted in matching colors.
# <br><br>
# <img src="colorcodet1.png">
# <img src="colorcodet2.png">
# <img src="colorcodet3.png">
# <img src="colorcodet4.png">
# <img src="colorcodet5.png">
# <img src="colorcodet6.png">

# ### Run the Simulation:
# *CYCLUS* can be run using a single terminal command, given below.  The cell will run this command for you, but it's also possible to remove the ! and directly run it in the terminal

# In[16]:


# CYCLUS will not overwrite an old file - delete the old version if you run a simulation again and put
# the output to the same filename
#!rm singlereactortutorial.sqlite
#!cyclus 1xn-rendered-main-input.xml -o singlereactortutorial1.sqlite
# this is a command that can be executed in your terminal, without the ! . The -o flag is used to
# set the name of the output file.  Without it, the default is "cyclus.sqlite"


# ### Analyze the results:
# *CYCLUS* creates a .sqlite file as its output.  SQL is a database file type that consists of a series of tables.  A few functions have been included in basics.py to pull information from the sqlite database and create figures.<br><br>
# An sqlite database can be opened and its contents viewed, but these database browsers often aren't as helpful as importing the data into an external function and manipulating it with there would be.  However, it can still be helpful to open and view the tables.
# <img src="Selection_002.png" width="850"><br><br>
# This a view of the tables within the database (using DB browser for SQLite).  However, to view the data within these tables, switch to the Browse Data tab:<br>
# <img src="Selection_003.png" width="850"><br>
# And select the table of interest.  Some tables have data that may need to be manipulated or used alongside other data in other tables, which is why using something such as a python script is often ideal.

# First, a cursor that points to the sqlite file is created:

# In[17]:


cur = basics.get_cursor('singlereactortutorial.sqlite')


# plot_in_out_flux will plot the material coming into or out of the prototype of choice, and allows for cumulative and total plotting options.  For example, setting the influx boolean to true, cumulative to true, and total to true adds up all the isotopes cumulatively at each timestep for materials entering the reactor.  This creates a plot of cumulative fuel into reactors over time.

# In[18]:


basics.plot_in_out_flux(cur, 'NuclearRepository',True, 'Cumulative Isotope Inventory of Repository',is_cum = True,is_tot = False)


# In[19]:


basics.plot_in_out_flux(cur, '1000MWe Honeycomb3000',True, 'Cumulative Fuel into Reactors Over Time',
                 is_cum = True,is_tot = True)


# In[20]:


basics.plot_in_out_flux(cur, 'UraniumMine',False, 'Uranium Mine production Over Time',is_cum = False,is_tot = True)


# In[21]:


basics.plot_in_out_flux(cur, 'EnrichmentPlant',False, 'Enrichment Plant Production Over Time',
                 is_cum = False,is_tot = False)


# In[22]:


uranium_utilization = basics.u_util_calc(cur)


# In[23]:


basics.plot_swu(cur,False)


# In[24]:


basics.plot_power_ot(cur,False,True)


# After reading and understanding the general structure of the *CYCLUS* output file and how to index within an sql file, you should be able to pull desired data in ways beyond the functions in this tutorial.
