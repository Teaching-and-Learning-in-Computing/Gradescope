from gradescope import Gradescope, Role


gs = Gradescope(verbose=True)
courses = gs.get_courses(role=Role.INSTRUCTOR)
