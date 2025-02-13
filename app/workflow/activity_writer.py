"""
ActivityWriter module  - Writes Activity instances to file
"""

from app.workflow.activity import Activity, ActivityVisitor


class ActivityWriter(ActivityVisitor):
    """Writes Activity instances to file"""

    def __init__(self, file):
        self.file = file
        self.visited_activities = set()


    def visit_start(self, activity: Activity) -> None:
        """Write the START activity"""
        self._write(activity, "@{ shape: f-circ, label: \"start\"}")

    def visit_set(self, activity: Activity) -> None:
        """Write the SET activity"""
        self._write(activity, f"[{activity.kind.value}: {activity.expression}]")

    def visit_assign(self, activity: Activity) -> None:
        """Write the ASSIGN activity"""
        self._write(activity, f"[{activity.kind.value}: {activity.expression}]")

    def visit_check(self, activity: Activity) -> None:
        """Write the CHECK activity"""
        self._write(activity, "{" + f"{activity.expression}" + "}")

    def visit_prompt(self, activity: Activity) -> None:
        """Write the PROMPT activity"""
        self._write(activity, f"[{activity.kind.value}: {activity.expression}]")

    def visit_ask(self, activity: Activity) -> None:
        """Write the ASK activity"""
        self._write(activity, "@{ shape: manual-input, label: \"" + \
                    f"{activity.kind.value}: {activity.expression}" + "\" }")

    def visit_execute(self, activity: Activity) -> None:
        """Write the EXECUTE activity"""
        self._write(activity, f"[\"{activity.kind.value}: {activity.expression}\"]")

    def visit_call(self, activity: Activity) -> None:
        """Write the CALL activity"""
        self._write(activity, f"[[{activity.expression}]]")

    def visit_success(self, activity: Activity) -> None:
        """Write the SUCCESS activity"""
        self._write(activity, "@{ shape: stadium  }")

    def visit_failed(self, activity: Activity) -> None:
        """Write the FAILED activity"""
        self._write(activity, "@{ shape: stadium  }")

    def visit_on(self, activity: Activity) -> None:
        """Write the ON activity"""
        self._write(activity, "@{ shape: stadium  }")


    def _write(self, activity: Activity, caption: str, recursive : bool = True) -> None:
        if activity is None:
            return
        if activity in self.visited_activities:
            return
        self.file.write(f"  {activity.name}" + caption + "\n")
        self.visited_activities.add(activity)

        # define the flow to the next activity
        if activity.next is not None:
            self.file.write(f"  {activity.name} --> ")
            if activity.kind == Activity.Kind.CHECK:
                self.file.write("|TRUE| ")
            self.file.write(f"{activity.next.name}\n")
            if recursive is True:
                activity.next.accept(self)

        if activity.other is not None:
            self.file.write(f"  {activity.name} --> ")
            if activity.kind == Activity.Kind.CHECK:
                self.file.write("|FALSE| ")
            elif activity.kind == Activity.Kind.CALL:
                self.file.write("|FAILED| ")
            self.file.write(f"{activity.other.name}\n")
            if recursive is True:
                activity.other.accept(self)
