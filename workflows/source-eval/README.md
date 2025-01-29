# Sample Scenario: Paperless Sprint1

This sample sennario is taken from a real course, where the students have to build a document-management system called Paperless using Java and Spring Boot.
The course is organized in sprints every two weeks and this is the workflow implementing auto-grading for the first sprint.

## Integration Tests

* Should succeed and score 100 points:
    ```shell
    .\run_codementor.ps1 workflows/source-eval/paperless-sprint1.wf.md REPO_URL=https://github.com/BernLeWal/fhtw-bif5-swkom-paperless.git
    ```

* Should fail the must-haves (not a java repo)
    ```shell
    .\run_codementor.ps1 workflows/source-eval/paperless-sprint1.wf.md REPO_URL=https://github.com/BernLeWal/fhtw-bwi4-swarc-material.git
    ```

* Should fail the must-haves (it's Java, but not Spring Boot)
    ```shell
    .\run_codementor.ps1 workflows/source-eval/paperless-sprint1.wf.md REPO_URL=https://github.com/BernLeWal/fhtw-eww3-sad-design-pattern-demo.git
    ```

* Should succeed the must-haves, but don't implement any of the other checks:
    ```shell
    .\run_codementor.ps1 workflows/source-eval/paperless-sprint1.wf.md REPO_URL=https://github.com/BernLeWal/SpringAIDemos.git
    ```

