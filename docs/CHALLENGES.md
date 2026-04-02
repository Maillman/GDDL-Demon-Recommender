# Challenges With The Project
## GDDL API Rate Limit
**The Problem:** After doing some research on the GDDL API. I noticed that the entire API has a rate limit of 100 requests/minute. Part of this project requires that I have up-to-date information about the levels and especially their tags. So this project requires a sync to occur at some point, but the amount of levels currently recorded in the GDDL is over 10,000! I would have to call the API at least over 10,000 times just to get the tags for every level! Doing a full sync would require several hours and put stress on the API during that time.
**The Solution:** Cache the RatingCount for each level. The biggest thing I care about with this project is the tags associated with each level. I know that the tags won't change if the RatingCount doesn't change. As long as I keep track of and cache the RatingCount for each level, I can determine whether I should fetch the tags for that level or keep the tags currently stored in the DB.
## Embedding Quality
**The Problem:** The query results are returning levels that aren't really desired after ["verifying"](#Notes) the levels the query results returning.
**The Solution:** Remove the name, difficulty tier, and category of the level from the embedding. Also repeat the more dominant tags several times in the embedding to ensure that they have more influence over the query results.
## GDDL SPA Conflicting With Loading Content
**The Problem:** The https://gdladder.com/ is a Single-Page Application. This isn't so much of a problem until you want to start injecting content to it with content scripts. The content scripts only get run once when the page initially loads, and subsequent navigations do not re-trigger these scripts because the browser does not perform a full page refresh.
**The Solution:** Have a service worker background script detect navigation events and reinitalize the needed content scripts.
## Additional Notes
1. The word "verifying" in the Geometry Dash community refers to a person who first beats a level and confirms the level is humanly possible. I am NOT using the word in that context!