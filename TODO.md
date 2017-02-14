# To Do

### Specific Actions
- Modify gpxpy module to parse HR & temperature data

### Choices to be made
- Decide on time horizon of
    - Sleep
    - Steps
    - Activities
        - Individual types
        - Overall (cardio)
- Coefficients for*
    - Sleep Score
    - Steps Score
    - Cardio Score
    - Activity Scores
- Should temperature be taken into account?

\* Do these need to/should these be learned by a model?


### Formalize
- Data input methods
- Script structure


### Figure out how to
- Work with GPX files
    - Extract HR data points
    - Calculate Suffer Score
- Automate data extraction from Garmin Connect
- Work with missing data (e.g. manual data entry when phone/watch was dead, or forgot HR monitor)
    - Need alternative to suffer score, for activities where HR data was not captured

### Incorporate additional data sources
- Need to look at different ways companies store their data to determine whether there is a common denominator (e.g. GPX)
    - E.g. Polar, Fitbit, Suunto, etc.
    - Look at platforms as well - Strava, Nike+, etc.


### Web App
- Start thinking about scope, required inputs, etc.
