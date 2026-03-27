# Project Pitch
## GDDL Demon Recommender
**What problem does your project solve, or what becomes better for having it?**
I play a game called Geometry Dash, and the hardest levels in the game are called "Demons". With the range of difficulty between even demons are wide enough that they are separated into separate categories of demons: Easy Demon, Medium Demon, Hard Demon, Insane Demon, and Extreme Demon.
However, the community has a problem that "sometimes only 5 different categories isn't enough to differentiate an easier level in this category to another" (taken from the [gdladder.com](https://gdladder.com/) website). So the community has taken it upon themselves to use the Geometry Dash Demon Ladder (GDDL) to vote what tier every single demon should be placed in.
However, my main concern is that different demons are challenging different skill sets. So even if you have beaten a demon of a specific tier, you can't reliably **climb up the ladder** to the next tier if the next demon you play is challenging a completely different skill set than the one you are used to. That's where I want to create a *Demon Recommender* to ensure that you have your skill set built up sufficiently to tackle the demons that you want to beat as well as find demons challenging the types of gameplay the player wants to challenge.
**What technologies do you plan to use?**
I'm still working out a lot of the details here, but I know the GDDL is going to be my main source of information, and I'm able to get a lot of the information I need from it using an API key the GDDL has provided for use! I will probably need to store an embedded version of all the levels in some type of database (graph database or something like that) in order to perform some type of semantic search to find levels with the skillsets closest to ones they want/need to challenge.
I don't think it's necessary to have another whole web application for this, or the functionality that I'm currently thinking of doesn't require one, so I'm probably going to create a chrome extension that can just call the database to read/search the embedded data and return the closest candidate to the request. I haven't created a chrome extension before, so that will be very fun to explore!
**Your goals for the project and a rough timeline of when you might accomplish them**
Research the tech stack required to make this happen, whether as a chrome extension or otherwise (3 hours).
Read and understand the documentation required to acquire the data from the GDDL API (2 hours).
Design and create a database to store the embedded version of the data and store that data (5 hours).
Implement the code/query(s) to search the database and retrieve the best match with the request (5 hours).
Create the UI for the user to input their request to find a demon recommendation (5 hours).
Implement updating the database every week or so with updated data as community opinion evolves and new demons get released (2 hours).
Implement some type of algorithm that can figure out a player's skillsets from the levels they've beaten and recommend a demon for them to play (8 hours).
If time permits, fine-tune the match returned from the database or the algorithm to figure out a player's skillset.
**Why are you interested in this project?**
I'm interested in this project, because I really like playing Geometry Dash and challenging myself to beat some of these hardest levels in the game.