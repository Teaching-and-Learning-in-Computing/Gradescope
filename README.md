# Gradescope
A Python wrapper for Gradescope to easily retrieve data from your Gradescope Courses.

## Example Usage

After including the gradescope folder in your project, import the necessary files.

In order to be able to access your account, the `Gradescope` object requires a username and password as arguments.

```py
from gradescope import Gradescope

gs = Gradescope('my_username', 'my_password')

courses = gs.get_courses(role=Role.INSTRUCTOR)

assignments = gs.get_assignments(courses[0])

members = gs.get_members(courses[0])

gradebook = gs.get_gradebook(courses[0], members[0])

past_submissions = gs.get_past_submissions(courses[0], assignments[0], members[0])
```

## Contribution
Written by HyunJun Park and Daniel Song (UCI Spring 2024)
