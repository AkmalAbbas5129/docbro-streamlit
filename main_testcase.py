from crewai import Agent, Task, Crew, Process
from crewai_tools import FileReadTool, DirectoryReadTool
from datetime import datetime

from utils import  get_llm
from langsmith import traceable


def call_crew_kickoff(brd_path, sdd_path, repo_path, default_llm):

    file_read_tool = FileReadTool()
    brd_file_read_tool = FileReadTool(brd_path)
    sdd_file_read_tool = FileReadTool(sdd_path)
    directory_reader_tool = DirectoryReadTool(directory=repo_path)



    #####-------------------Agents ------------------------------>>>>>>>>>>>>>>>
    solution_architect = Agent(
        role="Solution Architect",
        goal="Summarize the key points of the BRD and SDD document, focusing on the project objectives, scope, technical requirements,"
             " and vendor qualifications. Ensure that the summary is clear, concise, and captures the essence of the BRD and SDD.",
        allow_delegation=False,
        verbose=True,
        backstory=(
            "You possess a strong understanding of project management and procurement processes. Your expertise allows you to distill complex BRD and SDD "
            "documents into summaries that highlight critical information for stakeholders to make informed decisions."
        ),
        llm=default_llm
    )

    # Agent: Code Analyzer
    code_analyzer = Agent(
        role="Senior Developer",
        goal="Analyze the structure of code files to identify functions, classes, and logic and then write test cases.",
        verbose=True,
        memory=True,
        llm=default_llm,
        backstory="You are a senior developer and expert in understanding code structure, identifying key components and writing test cases.",
        tools=[directory_reader_tool, file_read_tool]
    )

    #### Tasks-------------------->>>>>>>>>>>>

    solution_architect_task = Task(
        description=(
            "### BRD and SDD Document Analysis ###\n"
            "1. Use the BRD and SDD Reader tool to retrieve the content of the BRD and SDD document.\n"
            "2. Carefully review the BRD and SDD content and identify the key sections, including business objectives, functional requirements, "
            "non-functional requirements, assumptions, constraints, and stakeholder roles.\n"
            "3. Summarize each section, focusing on the most critical information that will help stakeholders understand the project's business goals and "
            "requirements.\n"
            "4. Ensure that the summary is concise, clear, and captures the essence of the BRD and SDD, making it easier for decision-makers to evaluate the "
            "project’s alignment with business needs.\n"
            "5. Highlight any unique or critical requirements that may impact the project’s success, risk, or scope.\n"
            "6. Provide a final summary that offers a high-level overview of the entire BRD and SDD document."
        ),
        expected_output=(
            "A well-structured summary of the BRD and SDD document, including concise descriptions of the business objectives, functional and non-functional requirements, "
            "assumptions, constraints, and any critical factors. The summary should be clear and actionable, providing stakeholders with a quick "
            "understanding of the BRD and SDD key points and its alignment with business goals."
        ),
        tools=[brd_file_read_tool, sdd_file_read_tool],
        agent=solution_architect,
    )

    # Task: Analyze Code
    analyze_code_task = Task(
        description="Utilize BRD and SDD summary and Analyze each code file to identify functions, classes, and main logic."
                    "Write test cases for each identified function/method based code analysis and the provided BRD."
                    "1- The test cases should be comprehensive and cover all functional aspects."
                    "2- Write code for each test case."
                    "3- Comment each line of code for its functionality.",
        expected_output='A set of test cases (with code) covering all identified functions/methods and requirements.',
        context = [solution_architect_task],
        tools=[directory_reader_tool, file_read_tool],
        agent=code_analyzer,
        async_execution=False
    )

    # Step 3: Define the Process
    tc_crew = Crew(
        agents=[solution_architect, code_analyzer],
        tasks=[solution_architect_task, analyze_code_task],
        process=Process.sequential,
        planning=True,
        planning_llm=default_llm,
        verbose=1
    )

    # Begin the task execution
    result = tc_crew.kickoff()

    return result

@traceable(run_type="llm",  name="TestCase")
def testcase_main(brd_path, sdd_path, repo_path):

    default_llm = get_llm()

    # start Crew to generate SDD
    result = call_crew_kickoff(brd_path, sdd_path, repo_path, default_llm)

    current_datetime = datetime.now()
    formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
    # File name
    file_name = "./TestCase-Docs/generated_testcases/testcases_" + formatted_datetime + "_.md"

    # Save text to the markdown file
    with open(file_name, "w") as file:
        file.write(str(result))

    return str(result)


if __name__ == "__main__":

    sdd_path = "./DocBro-Docs/SDD-Docs/generated-sdd/my_sdd.md"
    brd_path = "./DocBro-Docs/BRD-Docs/generated-brd/my_brd.md"
    repo_path = "./DocBro-Docs/repos/flask_app"


    response = testcase_main(brd_path, sdd_path, repo_path)
    print(response)