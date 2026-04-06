# GDDL Demon Recommendation Request Requirements
## The Problem
When a `user_id` is provided in the RecommendationRequest, it seems to have too much of an influence over the recommendation result. I'm getting the same result regardless of desired tags or current level inputted, because of my beaten levels and skill distribution.
## A Solution
For now, ignore the beaten levels and skill distribution if either the `beaten_level_ids` (which should be changed to `level_id` to represent a level if we're on that levels page) or the `desired_tags` are not present. If both `beaten_level_ids` -> `level_id` or `desired_tags` are absent, then we use the the beaten levels and skill distribution from the `user_id` in our query.
**Extra:** It would be nice to have a boolean in the request to choose whether or not show already beaten levels in the result, **but they should not have an influence in the similarity search in either case.**